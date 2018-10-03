# -*- coding: utf-8 -*-
from dailyreport.company_object.models import BoilerHouse, BoilerBookmark, ThermalArea, Branch
from django.db.models.query_utils import Q

def get_boilers(actor, company_objects=[], bookmarks_id=[]):
    """
    Возвращает объекты моделей котельных по указанным объектам и "закладке". Закладка это некая
    характеристика котельной см. модель BoilerBookmark. 
        @param bookmarks: закладки по котельным
        @param company_objects: объекты структуры. Список метаданных,
                в котором указывается [{name: <Branch|ThermalArea|BoilerHouse>, id: <Идентификатор>},{...}]
    """
    
    # Филиалы, котельные и тепловые р-ны
    _branches = []
    _thermals = []
    _boilers = []
    
    # список объектов котельных
    boilers = []
    
    # котельные которые помечены закладкой
    _bookmarked_boilers_id = []

    if company_objects:
        for item in company_objects:
            if item[u'name']==u'branch':
                _branches.append(item[u'id'])
            elif item[u'name']==u'thermalarea':
                _thermals.append(item[u'id'])
            elif item[u'name']==u'boilerhouse':
                _boilers.append(item[u'id'])
    
    # Вычислить идентификаторы котельных, если указаны закладки
    if bookmarks_id != [] and bookmarks_id != None:
        for bookmark in BoilerBookmark.objects.select_related().filter(id__in=bookmarks_id):
            #идентификаторы котельных
            _bookmarked_boilers_id.extend( list(bookmark.boiler.all().values_list('id', flat=True)) )
    
    # если не было указано закладок
    if _bookmarked_boilers_id == []:
        # Если не было выбрано ни одного объекта 
        if _branches == [] and _thermals == [] and _boilers == []:
            boilers = BoilerHouse.objects.filter(enabled=True).order_by('branch__name','thermalArea__name','order_index','name').distinct()
        else:
            try:
                # Если выбран какой-то объект, но не было выбрано никакой закладки
                boilers = BoilerHouse.objects.filter(Q(branch__id__in = _branches)|
                                                     Q(thermalArea__id__in=_thermals)|
                                                     Q(id__in=_boilers), enabled=True).order_by('branch__name','thermalArea__name','order_index','name').distinct()
                
            except Exception as ex:
                print ex
    else:

        # Если была выбрана хоть одна закладка, и не было выбрано ни одного объекта
        if _branches == [] and _thermals == [] and _boilers == []:
            boilers = BoilerHouse.objects.filter(id__in=_bookmarked_boilers_id, enabled=True).order_by('branch__name','thermalArea__name','order_index','name').distinct()
        else:
            # Если выбрана хотя бы одна закладка и хотя бы один объект
            boilers = BoilerHouse.objects.filter(Q(branch__id__in = _branches)|
                 Q(thermalArea__id__in=_thermals)|
                 Q(id__in=_boilers), id__in=_bookmarked_boilers_id, enabled=True).order_by('branch__name','thermalArea__name','order_index','name').distinct()
    

    return boilers
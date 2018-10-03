# -*- coding: utf-8 -*-

from jsonrpc import jsonrpc_method
from models import Branch, ThermalArea, BoilerHouse, BoilerBookmark
from django.core import serializers
from django.conf import settings
from dailyreport.fuel.models import FuelInfo
from dailyreport.water.models import WaterConsumptionCategory
from dailyreport.company_object.utils import get_boilers
from dailyreport.company_object.models import Period
from dailyreport.user_profile.models import UserProfile
from datetime import datetime
import traceback
import sys
import logging
from dailyreport.utils import qooxdoo_utils

_logger = logging.getLogger(__name__)
#
# Филиалы
#

@jsonrpc_method('companyObject.addBranch', authenticated=True, safe=False)
def add_branch(request, json_model):
    """
    
    """
    pass

@jsonrpc_method('companyObject.removeBranch', authenticated=True, safe=False)
def remove_branch(request, id):
    """
    
    """
    pass

@jsonrpc_method('companyObject.editBranch', authenticated=True, safe=False)
def edit_branch(request, json_model):
    """
    
    """
    pass

@jsonrpc_method('companyObject.getBranches', authenticated=True)
def get_branches(request):
    """
    Получить список филиалов для пользователя. 
    
    Каждый пользователь доступен через профиль. В зависимости от 
    принадлежности к филиалу пользователь должен видеть: 
    либо все филиалы, если пользователь находится в Дирекции, либо только 
    тот к которому относится. 
    """
    try:
        _logger.info(u"[companyObject.getBranches()] - Получить список филиалов для пользователя: %s"%
                     unicode(request.user.username))
        
        profile,created = UserProfile.objects.get_or_create(user=request.user)
        branches = []

        if created or profile.branch == None:
            branches = serializers.serialize("json", Branch.objects.all().order_by('name'))
        else:
            branches = serializers.serialize("json", Branch.objects.filter(id=profile.branch.id).order_by('name'))
        
    except Exception as ex:
        _logger.error(u"[companyObject.getBranches()] - Не удалось получить список филиалов для пользователя: %(user)s. %(exception)s " %
                      {'user': unicode(request.user.username),
                      'exception': unicode(ex)})
        
        raise ex
    
    return branches

@jsonrpc_method('companyObject.getBranchById', authenticated=True, safe=False)
def get_branch(request, id=0):
    pass


#
# Тепловые районы
#

@jsonrpc_method('companyObject.addThermalArea', authenticated=True, safe=False)
def add_thermal(request, json_model):
    """
    
    """
    pass

@jsonrpc_method('companyObject.removeThermalArea', authenticated=True, safe=False)
def remove_thermal(request, id):
    """
    
    """
    pass

@jsonrpc_method('companyObject.editThermalArea', authenticated=True, safe=False)
def edit_thermal(request, json_model):
    """
    
    """
    pass

@jsonrpc_method('companyObject.getThermalAreas', authenticated=True, safe=False)
def get_thermals(request):
    """
    
    """
    pass

@jsonrpc_method('companyObject.getThermalAreaById', authenticated=True, safe=False)
def get_thermal(request, id):
    """
    
    """
    pass

@jsonrpc_method('companyObject.getThermalAreaByBranchId', authenticated=True, safe=False)
def get_thermal_by_branch(request, branch_id):
    """
    Получить объекты тепловых районов для филиала
    """
    thermals = ThermalArea.objects.filter(branch__id = branch_id).order_by('name')
    data = serializers.serialize("json", thermals)
    
    return data

#
# Объект компании
#

@jsonrpc_method('companyObject.addCompanyObject', authenticated=True, safe=False)
def add_company_object(request, json_model):
    """
    
    """
    pass

@jsonrpc_method('companyObject.removeCompanyObject', authenticated=True, safe=False)
def remove_company_object(request, id):
    """
    
    """
    pass

@jsonrpc_method('companyObject.editCompanyObject', authenticated=True, safe=False)
def edit_company_object(request, obj_id, name, address, enabled, fuel_info_ids, water_category_ids, bookmark_ids):
    """
    
    """
    boiler = BoilerHouse.objects.get(id=obj_id)
    
    boiler.boilerbookmark_set.clear()
    bookmarks = BoilerBookmark.objects.filter(id__in=bookmark_ids)
    for bookmark in bookmarks:
        bookmark.boiler.add(boiler)
       
    fuel_infos = FuelInfo.objects.filter(id__in=fuel_info_ids)
    water_categories = WaterConsumptionCategory.objects.filter(id__in=water_category_ids)
    
    return True    


@jsonrpc_method('companyObject.getCompanyObjects', authenticated=True, safe=False)
def get_company_objects(request):
    """
    
    """
    pass

@jsonrpc_method('companyObject.getCompanyObjectById', authenticated=True, safe=True)
def get_company_object_by_id(request, obj_id):
    """
    
    """
    from django.core import serializers
    
    serialized = serializers.serialize('json',BoilerHouse.objects.filter(id = obj_id))
    return {'boiler':serialized} 

@jsonrpc_method('companyObject.saveCompanyObject', authenticated=True, safe=False)
def save_company_object(request, company_object, periods):
    """
    
    """
    try:
        if company_object['$$user_id'] == 0:
            pass
        else:
            boiler = BoilerHouse.objects.get(id = company_object['$$user_id'])
            boiler.address = company_object['$$user_address']
            boiler.name = company_object['$$user_name']
            boiler.enabled = company_object['$$user_enabled']
            boiler.report_deviation = qooxdoo_utils.get_item(company_object,'reportEnabled')
            boiler.periods.clear()
            boiler.save()
            
            for period in periods:
                item = None
                
                if int(period['$$user_id']) > 0:
                    item = Period.objects.get(id=period['$$user_id'])
                else:
                    item = Period()

                item.start = datetime.strptime(period['$$user_start'], settings.DATE_FORMAT).date()
                item.end = datetime.strptime(period['$$user_end'], settings.DATE_FORMAT).date() 
                item.save()
                
                boiler.periods.add(item)
            boiler.save()
            return serializers.serialize("json", [boiler])
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
        logging.getLogger(__name__).error(ex) 
    
    return None

@jsonrpc_method('companyObject.getCompanyObjectByThermalId', authenticated=True, safe=False)
def get_company_object_by_thermal_id(request, thermal_id):
    """
    Получить объекты компании для теплового района
    """
    company_objects = BoilerHouse.objects.filter(thermalArea__id = thermal_id, enabled=True).order_by('order_index','name')
    data = serializers.serialize("json", company_objects)
    return data


@jsonrpc_method('companyObjects.getCompanyObjectsFromMix', authenticated=True, safe=False)
def get_company_object_from_mix(request, company_objects, bookmarks_id):
    """
    Получить объекты компании для теплового района
    """
    print company_objects
    print bookmarks_id
    ids = []
    for boiler in get_boilers(request.user, company_objects, bookmarks_id):
        ids.append(boiler.id)
    
    print ids
    return {'boilers': ids}
#
# Закладки
#

@jsonrpc_method('companyObject.addBookmark', authenticated=True, safe=False)
def add_bookmark(request, json_model):
    """
    
    """
    pass

@jsonrpc_method('companyObject.removeBookmark', authenticated=True, safe=False)
def remove_bookmark(request, id):
    """
    
    """
    pass

@jsonrpc_method('companyObject.editBookmark', authenticated=True, safe=False)
def edit_bookmark(request, json_model):
    """
    
    """
    pass

@jsonrpc_method('companyObject.getBookmarks', authenticated=True, safe=False)
def get_bookmarks(request):
    """
    Получить все закладки
    """
    data = serializers.serialize("json", BoilerBookmark.objects.all().order_by('name'))
    return data

@jsonrpc_method('companyObject.getBookmarkByBoilerId', authenticated=True, safe=False)
def get_bookmarks_by_boiler(request, boiler_id):
    """
    Получить все закладки для котельной
    """
    try:
        obj = BoilerHouse.objects.select_related().get(id=boiler_id)
        ids = obj.boilerbookmark_set.all().values_list('id', flat=True)

        data = []
        all_bookmarks = BoilerBookmark.objects.all().order_by('name')

        for bookmark in all_bookmarks:
            item = {}

            if bookmark.id in ids:
                item['assigned'] = True
            else:
                item['assigned'] = False

            item['id'] = bookmark.id
            item['name'] = bookmark.name
            item['boiler'] = boiler_id
            item['test'] = True
            
            data.append(item)
        
        #print data
        return {'bookmarks': data}
    except Exception as ex:
        print ex
    
    return {'bookmarks': data}

@jsonrpc_method('companyObject.saveBookmarkByBoilerId', authenticated=True, safe=False)
def save_bookmark_by_boiler(request, bookmarks, boiler_id):
    """
    Сохранить информацию о закладках для котельной.
    """
    for bookmark in bookmarks:
        if bookmark['$$user_assigned'] == True:
            bm = BoilerBookmark.objects.get(id=bookmark['$$user_id'])
            boiler = BoilerHouse.objects.get(id=boiler_id)
            bm.boiler.add(boiler)
            bm.save()

    return {'success' : True} 

@jsonrpc_method('companyObject.getBookmarkById', authenticated=True, safe=False)
def get_bookmark(request, id):
    """
    
    """
    pass 


@jsonrpc_method('companyObject.getPeriodsByCompanyObjectId', authenticated=True, safe=False)
def get_periods_by_company_object_id(request, boiler_id):
    """
    Получить список периодов для объекта
    """
    try:
        boiler = BoilerHouse.objects.get(id=boiler_id)
        data = []
        for item in boiler.periods.all().values_list('id','start','end'):
            data.append([item[0], unicode(item[1]), unicode(item[2])])
        
        return {'periods': data}
    except Exception as ex:
        print ex
    
    return None
    



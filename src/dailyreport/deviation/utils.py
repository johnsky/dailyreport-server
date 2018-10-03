# -*- coding: utf-8 -*-

from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.conf import settings

from dailyreport.deviation.models import ParameterDeviationProblemState,\
    ParameterDeviationProblem, ParameterDeviationProblemComment,\
    DeviationResponcible, DeviationConcerned
from dailyreport.company_object.utils import get_boilers
from dailyreport.authentication.utils import get_project_admin_user
from dailyreport.utils.date_utils import get_now
from dailyreport.water.models import WaterConsumption
from dailyreport.fuel.models import FuelConsumption
from dailyreport.electricity.models import ElectricityConsumption
from dailyreport.company_object.models import Branch, Resource
from django.contrib.auth.models import User


def create_problem(consumption_obj):
    """
    Создать проблему которая началась с определенного числа.
    1. Создать и сохранить сущность проблемы в состоянии Открыта;
    2. Создать комментарий с описанием проблемы;
    3. Добавить заинтересованные и ответственные лица;
    """
    if consumption_obj is None:
        raise Exception(u'Объект с данными о суточном расходе не указан.') 
    
    state_open = ParameterDeviationProblemState.objects.get(name=settings.DEVIATION_PROBLEM_STATE_OPEN)
    
    admin = get_project_admin_user()
    
    if admin == None:
        raise Exception(u"Не найден ни один пользователь-администратор.")
    
    
    
    problem = None    
    resource_obj = None
    
    if isinstance(consumption_obj, WaterConsumption):
        resource_obj = Resource.objects.get(name = settings.RESOURCE_TYPE_WATER)
        problem = ParameterDeviationProblem.objects.create(start_date = consumption_obj.date,
                                                        state = state_open,
                                                        boiler = consumption_obj.boiler,
                                                        resource = resource_obj,
                                                        water = consumption_obj)
        
    #    
    elif isinstance(consumption_obj, FuelConsumption): 
        resource_obj = Resource.objects.get(name = settings.RESOURCE_TYPE_FUEL)
        problem = ParameterDeviationProblem.objects.create(start_date = consumption_obj.date,
                                                        state = state_open,
                                                        boiler = consumption_obj.boiler,
                                                        resource = resource_obj,
                                                        fuel = consumption_obj)

    # 
    elif isinstance(consumption_obj, ElectricityConsumption):
        resource_obj = Resource.objects.get(name = settings.RESOURCE_TYPE_ELECTRICITY)
        problem = ParameterDeviationProblem.objects.create(start_date = consumption_obj.date,
                                                        state = state_open,
                                                        boiler = consumption_obj.boiler,
                                                        resource = resource_obj,
                                                        electricity = consumption_obj)

    else:
        raise Exception(u"Тип объекта не поддерживается.")
    
    comment_text = u"""
                    <p>Создана запись. Отклонение по ресурсу: %(type)s</p>
                    <p>Состояние: %(state)s</p>
                    <p>Дата: %(date)s </p>
                    <p>Плановое значение: %(plan_value)s</p>  
                    <p>Фактическое значение: %(actual_value)s<p>"""
    
    comment_text = comment_text % {'type'           : unicode(problem.resource),
                                   'state'          : unicode(state_open),
                                   'date'           : consumption_obj.date,
                                   'plan_value'     : consumption_obj.plan_day,
                                   'actual_value'   : consumption_obj.actual_day }
    
    comment = ParameterDeviationProblemComment.objects.create(author = admin,
                                                              date = get_now(),
                                                              text = comment_text,
                                                              deviation = problem)
    
    responcibles = DeviationResponcible.objects.filter(branch__id=consumption_obj.boiler.branch.id)
    
    if len(responcibles) == 0 :
        branch = Branch.objects.get(id = consumption_obj.boiler.branch.id)
        raise Exception(u"Нет ответственных людей за проблемы связанные с отклонением суточных показателей от плана в филиале " +unicode(branch.name))
    
    for responcible in responcibles:
        problem.responsible.add(responcible.responcible)
    
    concerned = DeviationConcerned.objects.all()
    if len(concerned) == 0:
        raise Exception(u"Нет заинтересованных лиц")

    for item in concerned:
        problem.concerned.add(item.concerned)

    problem.save()
    
    return problem


def close_problem(actor, problem):
    """
    Закрыть проблему.
    """
    if problem == None:
        raise Exception(u"Необходимо указать проблему, которую нужно закрыть!")
    
    if actor == None:
        raise Exception(u"Необходимо указать того, кто закрывает проблему!")
    
    state_closed = ParameterDeviationProblemState.objects.get(name=settings.DEVIATION_PROBLEM_STATE_CLOSED)
    problem.state = state_closed
    problem.save()
    
    comment_text = u"""<p>Закрыта пользователем : %(actor)s</p>""" % {'actor' : unicode(actor)}
    
    comment = ParameterDeviationProblemComment.objects.create(author = actor,
                                                              date = get_now(),
                                                              text = comment_text,
                                                              deviation = problem)
    
def add_concerned():
    pass

def add_responsible():
    pass

def remove_responsible():
    pass

def remove_concerned():
    pass

def add_comment():
    pass


def look_for_problems_query(actor, company_objects=[], bookmarks = [], state=None, resource=None, sort_by=None, sort_order=None):
    """
    Найти проблемы по указанным параметрам.
    
    @param actor: 
    @param state: Состояние проблемы
    @param company_objects: Объекты структуры. Список метаданных,
                в котором указывается [{name: <Branch|ThermalArea|BoilerHouse>, id: <Идентификатор>},{...}]
    """
    
    problems = []
    
    boilers = get_boilers(actor, company_objects, bookmarks)
    
    query_set = ParameterDeviationProblem.objects.select_related()
    
    
    if boilers!= []:
        if resource == 'Вода':
            query_set.filter(water__boiler__in = boilers)
        elif resource == 'Электричество':
            query_set.filter(electricity__boiler__in = boilers)
        elif resource == 'Топливо':
            query_set.filter(fuel__boiler__in = boilers)
        else:
            query_set.filter(Q(water__boiler__in = boilers) | Q(electricity__boiler__in = boilers) | Q(fuel__boiler__in = boilers))
    else:    
        if resource == 'Вода':
            query_set.filter(water__isnull=False)
        elif resource == 'Электричество':
            query_set.filter(electricity__isnull = False)
        elif resource == 'Топливо':
            query_set.filter(fuel__isnull = False)
    
    if state:
        query_set.filter(state__name == state)
    
    if sort_by =='ID':
        query_set.extra(order_by("-id"))
    elif sort_by == 'start_date':
        query_set.extra(order_by("-start_date"))
    elif sort_by == 'branch':
        query_set.order_by().boiler.branch.name
    elif sort_by == 'thermal':
        query_set.order_by().boiler.thermalArea.name
        
    elif sort_by =='company_object': query_set.get_resource().boiler.name,
    elif sort_by =='resource': query_set.get_resource_name(),
    elif sort_by =='state': query_set(problem.state)                     
    
    return query_set


def look_for_problems(actor, first_row, last_row, company_objects, bookmarks, state, resource, sort_by=None, sort_order=None):
    """
    Найти проблемы по указанным параметрам.
    
    @param actor: 
    @param state: Состояние проблемы
    @param company_objects: Объекты структуры. Список метаданных,
                в котором указывается [{name: <Branch|ThermalArea|BoilerHouse>, id: <Идентификатор>},{...}]
    """
    
    problems = []
    boilers = get_boilers(actor, company_objects, bookmarks)
    print boilers
    problems = ParameterDeviationProblem.objects.filter(boiler__in = boilers,
        state__name__in=state, resource__name__in = resource).values(
        'id','start_date','boiler__branch__name','boiler__thermalArea__name', 'boiler__name', 'resource__name', 'state__name')[first_row: last_row+1]
    print problems
    #if state:
    #    print "==========================================="
    #    query_set.filter(state__name == state)
    
    #if sort_by =='ID':
    #    query_set.extra(order_by("-id"))
    #elif sort_by == 'start_date':
    #    query_set.extra(order_by("-start_date"))
    #elif sort_by == 'branch':
        #query_set.order_by().boiler.branch.name
    #    pass
    #elif sort_by == 'thermal':
        #query_set.order_by().boiler.thermalArea.name
    #    pass
    #elif sort_by =='company_object':
    #    pass
        #query_set.get_resource().boiler.name,
    #elif sort_by =='resource':
        #query_set.get_resource_name(),
    #    pass
    #elif sort_by =='state': 
        #query_set(problem.state)
    #    pass
    #else:
    #    pass
        #query_set.order_by("boiler__branch__name","boiler__therame","boiler__name", "start_date")
        #query_set = query_set.extra(order_by = ["branch.name","thermal.name","boiler.name", "deviation.start_date"])
    
    #print query_set[first_row: last_row+1].query
    '''problems = query_set.values('id','start_date',
                               'boiler__branch__name',
                               'boiler__thermalArea__name',
                               'boiler__name',
                               'resource__name',
                               'state__name')[first_row: last_row+1]'''
    #print problems
    
    data = {}
    try:
        a = []
        for problem in problems:
            o = {'ID': problem['id'],
               'start_date': unicode(problem['start_date']),
               'branch': unicode(problem['boiler__branch__name']),
               'thermal': unicode(problem['boiler__thermalArea__name']),
               'company_object': unicode(problem['boiler__name']),
               'resource': unicode(problem['resource__name']),
               'state': unicode(problem['state__name'])}
            a.append(o)
            
        data = {'data' : a}

    except Exception as ex:
        print ex
    
    return data
    #ParameterDeviationProblem.objects.filter(Q(water_consumption__boiler = boilers) || Q()) 

# -*- coding: utf-8 -*-

import logging
import traceback
import sys
import logging
from jsonrpc import jsonrpc_method

from django.template.loader import render_to_string
from django.core import serializers
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.query_utils import Q

from dailyreport.deviation.models import ParameterDeviationProblem,\
    ParameterDeviationProblemComment, ParameterDeviationProblemState,\
    DeviationResponcible, DeviationConcerned,\
    ParameterDeviationProblemCommentAdmin, ParameterDeviationProblemCause
from dailyreport.utils.date_utils import get_today, string_to_date, get_now
from dailyreport.company_object.utils import get_boilers
from dailyreport.deviation.utils import look_for_problems, close_problem,\
    create_problem
from dailyreport.water.models import WaterConsumption, WaterConsumptionCategory
from dailyreport.utils import qooxdoo_utils
from dailyreport.company_object.models import Resource, BoilerHouse
import simplejson

_logger = logging.getLogger(__name__)

@jsonrpc_method('deviation.getProblems', authenticated=True, safe=True)
def get_problems(request, first_row, last_row, company_objects, bookmarks,
                    filter_settings, sort_by=None, sort_order=None):
    """
    Получить список проблем
    """
    try:
        _logger.info(u"[deviation.getProblems()] - Получить список проблем, пользователем: %s"%
                     unicode(request.user.username))
        
        boilers = get_boilers(request.user, company_objects, bookmarks)

        if len(boilers)>0:
            qs = ParameterDeviationProblem.objects.select_related().filter(boiler__in = boilers)            
            
            # Has start date
            if qooxdoo_utils.get_item(filter_settings, 'startDate') != None:
                from_date = string_to_date(qooxdoo_utils.get_item(filter_settings, 'startDate'))
                qs = qs.filter(start_date = from_date)

            if qooxdoo_utils.get_item(filter_settings, 'state','id') > 0:
                qs = qs.filter(state__id = qooxdoo_utils.get_item(filter_settings, 'state','id'))

            if qooxdoo_utils.get_item(filter_settings, 'cause','id') > 0:
                qs = qs.filter(Q(cause__id = qooxdoo_utils.get_item(filter_settings, 'cause','id'))
                               | Q (cause__id=None))
        
        qs = qs.order_by("boiler__branch__name",
                    "boiler__thermalArea__name",
                    "boiler__name", 'start_date', 'cause__name')
        

        problems = serializers.serialize("json",
                                         qs[first_row: last_row+1],
                                         relations={'boiler'    :   {'relations' : ('thermalArea','branch')},
                                                    'resource'  :   {},
                                                    'state'     :   {},
                                                    'cause'     :   {},
                                                    'responsible':  {},
                                                    'concerned' :   {},
                                                    'water'     :   {},
                                                    'fuel'      :   {},
                                                    'electricity':  {}
                                                    })
        return problems
    
    except Exception as ex:
        _logger.error(u"[deviation.getProblems()] - Не удалось получить список проблем пользователю: %(user)s. %(exception)s " %
                      {'user': unicode(request.user.username),
                      'exception': unicode(ex)})
        
        raise ex
    
    

@jsonrpc_method('deviation.getProblemsCount', authenticated=True, safe=True)
def get_problems_count(request, company_objects, bookmarks, filter_settings):
    """
    Получить количество записей.
    
    @param company_objects: Объекты компании
    @param bookmarks: Закладки 
    @param resources: Ресурсы 
    @param states: Состояния
    @param start_date: Дата начала проблемы 
    """
    try:
        boilers = get_boilers(request.user, company_objects, bookmarks)
        number_rows = 0
        
        if len(boilers)>0:
            qs = ParameterDeviationProblem.objects.filter(boiler__in = boilers)            
            
            # Has start date
            if qooxdoo_utils.get_item(filter_settings, 'startDate') != None:
                from_date = string_to_date(qooxdoo_utils.get_item(filter_settings, 'startDate'))
                print from_date
                qs = qs.filter(start_date = from_date)

            if qooxdoo_utils.get_item(filter_settings, 'state','id') > 0:
                qs = qs.filter(state__id = qooxdoo_utils.get_item(filter_settings, 'state','id'))

            if qooxdoo_utils.get_item(filter_settings, 'cause','id') > 0:
                qs = qs.filter(Q(cause__id = qooxdoo_utils.get_item(filter_settings, 'cause','id'))
                               | Q (cause__id=None))
            
            number_rows = qs.count()
            
        return {'count': number_rows}
    except:
        traceback.print_exc(file=sys.stdout)
        raise
        

@jsonrpc_method('deviation.getDeviationById', authenticated=True, safe=True)    
def get_deviation_by_id(request, deviation_id):
    """
    """
    query_set = ParameterDeviationProblem.objects.filter(id = deviation_id)
    serialized = serializers.serialize('json', query_set, 
                           relations={  'boiler'    :   {'relations' : ('thermalArea','branch')},
                                        'resource'  :   {},
                                        'state'     :   {},
                                        'cause'     :   {},
                                        'responsible':  {},
                                        'concerned' :   {},
                                        'water'     :   {},
                                        'fuel'      :   {},
                                        'electricity':  {}
                                         })
    return serialized

@jsonrpc_method('deviation.closeDeviation', authenticated=True, safe=True)    
def close_deviation(request, deviation_id, comment_data):
    """
    
    """
    problem = ParameterDeviationProblem.objects.get(id=deviation_id)
    
    if problem.state.name == settings.DEVIATION_PROBLEM_STATE_CLOSED:
        raise Exception(u"Проблема уже закрыта")
    
    state_closed = ParameterDeviationProblemState.objects.get(name=settings.DEVIATION_PROBLEM_STATE_CLOSED)
    problem.close_date = get_now()
    problem.state = state_closed
    problem.save()

    comment_author = User.objects.get(username = qooxdoo_utils.get_item(comment_data,'author','userName'))
    
    comment = ParameterDeviationProblemComment()
    comment.author = comment_author
    comment.date = qooxdoo_utils.get_item(comment_data,'date')
    comment.text = qooxdoo_utils.get_item(comment_data,'text')
    comment.deviation = problem
    comment.save()
    

@jsonrpc_method('deviation.getDeviation', authenticated=True, safe=True)
def get_deviation(request, company_object_id, resource_name, on_date):
    """
    Получить проблему по котельной по ресурсу на дату.
    """
    #[settings.RESOURCE_TYPE_WATER, settings.RESOURCE_TYPE_ELECTRICITY, settings.RESOURCE_TYPE_FUEL]
    #[settings.DEVIATION_PROBLEM_STATE_OPEN]
    try:    
    
        query_set = ParameterDeviationProblem.objects.select_related().filter(boiler__id = company_object_id,
                                                        resource__name = resource_name,
                                                        state__name = settings.DEVIATION_PROBLEM_STATE_OPEN,
                                                        start_date__lte = on_date)
        serialized = serializers.serialize('json', query_set, relations=('boiler','resource','state','cause','responsible', 'concerned'))
        return serialized
    except Exception as ex:
        print ex
        traceback.print_exc(file=sys.stdout)
        _logger.error(unicode(ex))
    
    return []

@jsonrpc_method('deviation.getDeviationComments', authenticated=True, safe=True)
def get_deviation_comments(request, deviation_id):
    """
    
    """
    try:
        query_set = ParameterDeviationProblemComment.objects.filter(deviation__id = deviation_id)
        serialized = serializers.serialize('json', query_set, relations=('author'), excludes=('deviation'))
        return serialized
    except Exception as ex:
        print ex
        _logger.error(unicode(ex))
        
    return None

@jsonrpc_method('deviation.validate', authenticated=True, safe=True)
def validate_deviation(request,company_object_id, event_date, resource, fuel_info_id, water_category_id, value):
    """
    
    """
    try: 
        if resource == settings.RESOURCE_TYPE_WATER:
            problems = ParameterDeviationProblem.objects.filter(boiler__id = company_object_id,
                                                        resource__name = resource,
                                                        state__name = settings.DEVIATION_PROBLEM_STATE_OPEN,
                                                        start_date__lte = event_date)
            
            # Если есть уже проблема по котельной - возвращаем ее
            if len(problems) > 0:
                return False
            
            consumption = WaterConsumption.objects.get(boiler__id = company_object_id,
                                         date = event_date, category__id = water_category_id)
            
            # Если есть привышение более чем на 5 процентов, тогда создаем или получем проблему
            if value - consumption.plan_day > 0 and (value - consumption.plan_day)/consumption.plan_day > 0.05:
                return False
        else:
            pass
    except Exception as ex:
        print ex
        traceback.print_exc(file=sys.stdout)
        
    #print company_object_id
    #print date
    #print resource 
    
    return True

@jsonrpc_method('deviation.saveDeviation', authenticated=True, safe=True)
def save_deviation(request, deviation_data):
    """
    """
    try:
        deviation_id = qooxdoo_utils.get_item(deviation_data,'id')
        problem = None
        
        if deviation_id == 0:
            problem = ParameterDeviationProblem()
            problem.boiler = BoilerHouse.objects.get(id=qooxdoo_utils.get_item(deviation_data,'boiler','id'))
            problem.state = ParameterDeviationProblemState.objects.get(name=qooxdoo_utils.get_item(deviation_data,'state', 'name'))
            problem.start_date = qooxdoo_utils.get_item(deviation_data,'startDate')
            problem.resource = Resource.objects.get(name = qooxdoo_utils.get_item(deviation_data,'resource', 'name'))
            
            cause_name = qooxdoo_utils.get_item(deviation_data, 'cause', 'name')
            if cause_name is not None:
                problem.cause = ParameterDeviationProblemCause.objects.get(name = cause_name)
            
            water_category = WaterConsumptionCategory.objects.get(boiler = problem.boiler, active = True)
            consumption = WaterConsumption.objects.get(category = water_category,
                                                       date = qooxdoo_utils.get_item(deviation_data,'startDate'))
            problem.water = consumption
            problem.save()
            
            problem = ParameterDeviationProblem.objects.get(boiler = problem.boiler, state = problem.state, start_date = problem.start_date, resource = problem.resource)
            
            for item in DeviationResponcible.objects.all():
                problem.responsible.add(item.responcible)
            
            for item in DeviationConcerned.objects.all():
                problem.concerned.add(item.concerned)
            
            problem.save()
            
            # Добавляем комментарии
            for item in qooxdoo_utils.get_item(deviation_data,'comments'):
                comment_author = User.objects.get(username = qooxdoo_utils.get_item(item,'author','userName'))
                comment = ParameterDeviationProblemComment()
                comment.author = comment_author
                comment.date = qooxdoo_utils.get_item(item,'date')
                comment.text = qooxdoo_utils.get_item(item,'text')
                comment.deviation = problem
                comment.save()
        else:
            dev = ParameterDeviationProblem.objects.get(id = deviation_id)
            dev.state = ParameterDeviationProblemState.objects.get(name=qooxdoo_utils.get_item(deviation_data,'state', 'name'))
            
            cause_name = qooxdoo_utils.get_item(deviation_data, 'cause', 'name')
            if cause_name:
                dev.cause = ParameterDeviationProblemCause.objects.get(name = cause_name)
            else:
                dev.cause = None

            dev.save()
                
            comments = ParameterDeviationProblemComment.objects.filter(deviation__id = deviation_id)
            
            for item in qooxdoo_utils.get_item(deviation_data,'comments'):
                if not qooxdoo_utils.has_key(item,'id'):
                    comment_author = User.objects.get(username = qooxdoo_utils.get_item(item,'author','userName'))

                    comment = ParameterDeviationProblemComment()

                    comment.author = comment_author
                    comment.date = qooxdoo_utils.get_item(item,'date')
                    comment.text = qooxdoo_utils.get_item(item,'text')
                    comment.deviation = dev
                    comment.save()

    except Exception as ex:
        _logger.error(unicode(ex))
    
    return {}

@jsonrpc_method('deviation.saveComment', authenticated=True, safe=True)
def save_comment(request, comment_data):
    
    try:
        problem = ParameterDeviationProblem.objects.get(id=qooxdoo_utils.get_item(comment_data,'deviation','id'))
        comment_author = User.objects.get(username = qooxdoo_utils.get_item(comment_data,'author','userName'))
        
        comment = ParameterDeviationProblemComment()
        comment.author = comment_author
        comment.date = qooxdoo_utils.get_item(comment_data,'date')
        comment.text = qooxdoo_utils.get_item(comment_data,'text')
        comment.deviation = problem
        comment.save()
    except Exception as ex:
        _logger.error(unicode(ex))

    return True

@jsonrpc_method('deviation.getCauses', authenticated=True, safe=True)
def get_causes(request):
    try:
        return serializers.serialize('json', ParameterDeviationProblemCause.objects.all())
    except Exception as ex:
        _logger.error(ex)
        raise ex

@jsonrpc_method('deviation.getStates', authenticated=True, safe=True)
def get_states(request):
    try:
        return serializers.serialize('json', ParameterDeviationProblemState.objects.all())
    except Exception as ex:
        _logger.error(ex)
        raise ex
    
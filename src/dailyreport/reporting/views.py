# -*- coding: utf-8 -*-
import time
import datetime
import logging

from django.http import HttpResponse, HttpResponseBadRequest,\
    HttpResponseNotFound
from django.contrib.auth.decorators import login_required, permission_required
from django.core import serializers
from django.db.models.query_utils import Q

from django.template.context import RequestContext
from django.template.loader import select_template, get_template,\
    render_to_string
from django.shortcuts import render_to_response

from jsonrpc import jsonrpc_method
from dailyreport.reporting.models import CompositeconsumptionReport,\
    electro_query, DeviationsReport
from dailyreport.company_object.models import Branch, ThermalArea, BoilerHouse, BoilerBookmark
from dailyreport.utils.date_utils import get_period_dates, string_to_date,\
    string_to_date2, string_to_datetime
from dailyreport.deviation.models import ParameterDeviationProblem
from dailyreport.company_object.utils import get_boilers
from dailyreport.utils import qooxdoo_utils
from dailyreport.reporting.utils import render_to_pdf
import os
from django.conf import settings
from dailyreport.consumption.models import Environment
from django.db.models.aggregates import Avg
from dailyreport.water.models import WaterConsumption
import pytz
from dateutil.parser import parse

_logger = logging.getLogger(__name__)


SUPPORTED_REPORTS = {u"Рапорт о работе котельных": ('water_consumption_report', 'date')}

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def ping(request):
    """
    Номера подсетей:    
    Арсеньев          168.111
    Анучино           168.112
    Яковлевка         168.114

    Артем             168.121
    Надеждинское      168.122
    Хасан             168.123
    Шкотово           168.124

    Горные Ключи      168.131
        
    Дальнегорск       168.141
    Кавалерово        168.142
    Горнореченск      168.143
    Ольга             168.144
    Терней            168.145
    Чугуевка          168.113
        
    Лесозаводск       168.151
    Дальнереченск     168.152
    Северный          168.153
        
    Михайловка        168.161
    Пограничный       168.162
    Покровка          168.163
    Новошахтинск      168.164
    Липовцы           168.165

    Находка           168.171
        
    Партизанск        168.181
    Влад-Алекс.       168.182
    Лазовский         168.183
        
    Спасск            168.191
    Камень-Рыболов    168.192
    Хороль            168.193
    """
    ip = get_client_ip(request)
    print ip
    subnet = ip.split('.')[2]
    
    #Branch.objects.filter(subnet = subnet)
    #ThermalArea.objects.filter(subnet = subnet)
    
    return HttpResponse(subnet)

@jsonrpc_method('test.getValue')
def test_service(request, value):
    """
    Метод для юнит тестов клиентского приложения
    """
    print value
    return {'value': value}

def index( request ):
    """"""
    return HttpResponse('Page not found') 

@login_required
def consumption(request):
    """
    
    """
    try:
        if not request.user.is_authenticated():
            return HttpResponse("<h1>Вы не авторизованы!</h1>")
        
        boilers = request.GET['boiler'].split(',')
            
        report_start_date = parse(request.GET['startDate']).date()
    
        #time_zone = pytz.timezone(settings.TIME_ZONE)
        #date_format = '%Y-%m-%d %H:%M:%S %ZZZZ'
        #report_start_date = string_to_datetime(request.GET['startDate'], time_zone, date_format).date()
        
        is_water =  False
        is_fuel = False
        is_electricity = False
        #print request.GET
        
        if request.GET['water'] == 'true':
            is_water = True
            #print type(request.GET['water'])
            #print is_water
            
        if request.GET['fuel'] == u'true':
            is_fuel = True
            #print is_fuel
            
        if request.GET['electricity'] == u'true':
            is_electricity = True
            #print is_electricity
            
        try:
            report_end_date = parse(request.GET['startDate']).date() #string_to_datetime(request.GET['endDate'], time_zone, date_format).date()
        except:
            report_end_date = report_start_date
        
        #print request.GET
        #y,m,d = time.strptime(end_date, "%Y-%m-%d")[0:3]
        #report_end_date = datetime.date(y,m,d)
        
        date_list = get_period_dates(report_start_date, report_end_date)
    
        if (report_end_date - report_start_date).days <= 0: 
            date_list = [report_start_date]
        
        #composite_report_tmpl = get_template("compositereport/report.html")
        header = render_to_string('compositereport/report_header.html',{ 'has_water'        : is_water,
                                                                         'has_fuel'         : is_fuel,
                                                                         'has_electricity'  : is_electricity})
        
        #boilers = BoilerHouse.objects.filter(branch__id = 1).values_list('id', flat=True).order_by('branch__name','thermalArea__name','name')
        thermals_id = BoilerHouse.objects.select_related().filter(id__in=boilers).values_list('thermalArea__id', flat=True).distinct()
        branches_id = BoilerHouse.objects.select_related().filter(id__in=boilers).values_list('branch__id', flat=True).distinct()
        branches = Branch.objects.filter(id__in=branches_id).order_by('name')
    
        data_text = ""
        for date_item in date_list:
            #print date_item
            #data_text = data_text + render_to_string('compositereport/date_section.html', {'date': date_item })
            for branch in branches:
                #print "BRANCH " + unicode(branch.id) +" "+ time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
                
                thermals = ThermalArea.objects.filter(id__in=thermals_id, branch__id=branch.id).order_by('name')
                for thermal in thermals:
                
                    #print "Thermal " + unicode(thermal.id) + ">> " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
                    boilers_id = BoilerHouse.objects.select_related().filter(thermalArea__id = thermal.id, id__in=boilers, enabled=True).values_list('id', flat=True).order_by('branch__name','thermalArea__name','order_index','name')
                    #boilers_id = thermal.boilerhouse_set.values_list('id', flat=True).order_by('branch__name','thermalArea__name','name')
                    #print "Thermal " + unicode(thermal.id) + ">> " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
                    
                    for boiler_id in boilers_id:
                        data = CompositeconsumptionReport.objects.get_boiler_data(boiler_id, date_item)
                        #print data
                        data_text = data_text + render_to_string('compositereport/boiler.html', {'lines'            : data,
                                                                                                 'report_delimiter' :",",
                                                                                                 'rows_number'      : len(data),
                                                                                                 'date'             : date_item,
                                                                                                 'has_water'        : is_water,
                                                                                                 'has_fuel'         : is_fuel,
                                                                                                 'has_electricity'  : is_electricity})
                    
                    data = CompositeconsumptionReport.objects.get_thermal_totals(boilers_id, date_item, branch.name, thermal.name)
                    data_text = data_text + render_to_string('compositereport/totals/thermal.html', 
                                                             {'lines'            : data,
                                                              'report_delimiter' : ",",
                                                              'rows_number'      : len(data),
                                                              'date'             : date_item,
                                                              'has_water'        : is_water,
                                                              'has_fuel'         : is_fuel,
                                                              'has_electricity'  : is_electricity })
                
                boilers_id = BoilerHouse.objects.select_related().filter(branch__id = branch.id, id__in=boilers, enabled=True).values_list('id', flat=True).order_by('branch__name','thermalArea__name','order_index','name')    
                data = CompositeconsumptionReport.objects.get_branch_totals(boilers_id, date_item, branch.name)
                data_text = data_text + render_to_string('compositereport/totals/branch.html', {'lines'            : data,
                                                                                                'report_delimiter' :",",
                                                                                                'rows_number'      : len(data),
                                                                                                'date'             : date_item,
                                                                                                'has_water'        : is_water,
                                                                                                'has_fuel'         : is_fuel,
                                                                                                'has_electricity'  : is_electricity })
                
                #print "BRANCH " + unicode(branch.id) +" "+ time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    
        bottom = render_to_string('compositereport/report_bottom.html')
    
        #body = render_to_string('compositereport/body.html', {'text': data_text})
        my_data_dictionary = {'report_title'    : u"Ежедневный отчет о расходе топлива, воды и тепловой энергии",
                            'header_section'    : header,
                            'body_section'      : data_text,
                            'bottom_section'    : bottom,
                            'has_water'         : is_water,
                            'has_fuel'          : is_fuel,
                            'has_electricity'   : is_electricity}
        
        context = RequestContext(request, my_data_dictionary)
        template = get_template('compositereport/report.html')
        response = HttpResponse(template.render(context), content_type='application/vnd.ms-excel; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=Composite Report %(start)s - %(end)s.xls' % {'start': str(report_start_date), 'end': str(report_end_date)}
        
        return response
        #return HttpResponse(template.render(context))
    except Exception as ex:
        print ex
        return HttpResponse(u"Ошибка.")

def water_consumption_report(args):
    """
    Отчет по воде
    
    """
    data = {}
    items = []
    report_date = parse(args['date']).date()
    for branch in Branch.objects.all():
        items.append({'name' : branch.name, 'is_branch' : True})
        
        for thermal in ThermalArea.objects.filter(branch__id = branch.id):
            
            outdoor_temp_avg = Environment.objects.filter(date = report_date,
                                    boiler__thermalArea__id = thermal.id,
                                    outdoor_temp_actual__gt=-273.0).aggregate(Avg('outdoor_temp_actual'))
            
            temp_avg = WaterConsumption.objects.filter(date = report_date,
                                                       category__name = u"Общий расход",
                                                       category__active = True,
                                                       category__boiler__thermalArea__id = thermal.id,
                                                       backward_temperature_actual__gt = -273.0,
                                                       farward_temperature_actual__gt = -273.0,
                                                       backward_temperature_estimated__gt = -273.0,
                                                       farward_temperature_estimated__gt = -273.0) \
                                        .aggregate(Avg('backward_temperature_actual'),
                                                   Avg('farward_temperature_actual'),
                                                   Avg('backward_temperature_estimated'),
                                                   Avg('farward_temperature_estimated'))

            items.append({'name': thermal.name,
                          'outdoor_temp_actual'             : outdoor_temp_avg['outdoor_temp_actual__avg'],
                          'backward_temperature_actual'     : temp_avg['backward_temperature_actual__avg'],
                          'farward_temperature_actual'      : temp_avg['farward_temperature_actual__avg'],
                          'backward_temperature_estimated'  : temp_avg['backward_temperature_estimated__avg'],
                          'farward_temperature_estimated'   : temp_avg['farward_temperature_estimated__avg']})
    
    data['items'] = items
    data['date'] = report_date  
    return (data, 'water/temperature_report.html')

@login_required
def deviation_report(request):
    """
    Отчет по воде
    """
    import json
    
    company_objects = request.GET['companyObjects']
    bookmarks = request.GET['bookmarks']
    
    boilers = get_boilers(request.user, json.loads(company_objects), json.loads(bookmarks))

    if len(boilers)>0:
        qs = ParameterDeviationProblem.objects.select_related().filter(boiler__in = boilers)            

        # Has start date
        if request.GET['startDate'] !=  'null':
            from_date = parse(request.GET['startDate']).date() #string_to_date2(request.GET['startDate'])
            qs = qs.filter(start_date = from_date)

        if request.GET['state'] > 0:
            qs = qs.filter(state__id = request.GET['state'])

        if request.GET['cause'] > 0:
            qs = qs.filter(Q(cause__id = request.GET['cause'])
                           | Q (cause__id=None))
    
    deviations_id = qs.values_list('id', flat=True)
    
    data = DeviationsReport.objects.get_deviations(deviations_id)
    
    params = {'report_title' : u'Список отклонений', 'items' : data, 'report_delimiter':","}
    context = RequestContext(request,params)
    template = get_template('deviation/deviation.html')
    
    #return HttpResponse(template.render(context))
    
    response = HttpResponse(template.render(context), content_type='application/vnd.ms-excel; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=Deviations_Report.xls'
    return response

@login_required()
def open_report(request, output_format):
    
    if output_format not in ['html','pdf','xls']:
        return HttpResponse(u"Неизвестный формат")

    if not request.GET.has_key('name'):
        return HttpResponseNotFound("Not found!")
    
    if not SUPPORTED_REPORTS.has_key(request.GET['name']):
        return HttpResponseNotFound(u"Такого отчета не существует!")
    
    descr = SUPPORTED_REPORTS[request.GET['name']]
    handler = descr[0]
    args = {}    
    
    for item in descr[1:]:
        if not request.GET.has_key(item):    
            return HttpResponseBadRequest(u"Параметр запроса не указан: %s" % item )
        
    args = dict( [ item,request.GET[item] ] for item in descr[1:] )
    data, template_name = eval(handler)(args)
    
    if output_format == 'pdf':
        data.update({'to_pdf': True,
                     'font_path' : settings.REPORTING_FONTS_LOCATION,
                     'report_name' : request.GET['name']})
        
        return render_to_pdf(template_name, data)

    elif output_format == 'html':
        data.update({'to_pdf': False,
                     'font_path' : settings.REPORTING_FONTS_LOCATION,
                     'report_name' : request.GET['name']})
        return render_to_response(template_name, data)
    
    elif output_format == 'xls':
        data.update({'to_pdf': False,
                     'font_path' : settings.REPORTING_FONTS_LOCATION,
                     'report_name' : request.GET['name']})
        
        context = RequestContext(request, data)
        template = get_template(template_name)
        
        response = HttpResponse(template.render(context), content_type='application/vnd.ms-excel; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=Report.xls'
        return response

def electro(request, year, month):
    if not request.user.is_authenticated():
        return HttpResponse("<h1>Вы не авторизованы!</h1>")
    electro_query()
    my_data_dictionary = {}
    
    context = RequestContext(request,my_data_dictionary)
    template = get_template('water/water_report.html')
    return HttpResponse(template.render(context)) #,content_type='application/vnd.ms-excel; charset=utf-8')
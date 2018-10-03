# -*- coding: utf-8 -*-
from django.db import models
from django.db import connection
from django.db import connections
import os.path
from dailyreport.utils.date_utils import get_month_last_day

# Путь к файлам с sql-запросами
REPORT_QUERIES_PATH = os.path.join(os.path.dirname(__file__),'queries')

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()]

def electro_query(year=0, month=0):
    
    d = os.path.dirname(os.path.join(__file__))
    query_file = open(os.path.join(d,'electro_query.sql'),'r')
    cursor = connections['electro'].cursor()
    cursor.execute(query_file.read())
    return dictfetchall(cursor)

class CompositeconsumptionReportManager(models.Manager):
    def get_boiler_data(self, boiler_id, date):
        """
        Получить данные для сводного отчета по котельной
        """
        queries_path = os.path.join(os.path.dirname(__file__),'queries')
        queries_path = os.path.join(queries_path,'composite','boiler.sql')
        
        query_file = open(queries_path,'r')
        day_coef = float(date.day)/float(get_month_last_day(date))
        
        cursor = connection.cursor()
        cursor.execute(query_file.read(), {'my_date': date, 'my_boiler': boiler_id, 'day_coef': day_coef})
        query_file.close()
        
        return dictfetchall(cursor)
    
    def get_thermal_totals(self, boilers, date, branch_name, thermal_name):
        """
        """
        queries_path = os.path.join(os.path.dirname(__file__),'queries')
        queries_path = os.path.join(queries_path,'composite','thermal.sql')
        
        query_file = open(queries_path,'r')
        day_coef = float(date.day)/float(get_month_last_day(date))
                
        cursor = connection.cursor()
        query = query_file.read()
        cursor.execute(query, {'my_date': date, 'my_boiler': tuple(boilers), 'thermal' :thermal_name, 'branch': branch_name, 'day_coef': day_coef})
        query_file.close()
        return dictfetchall(cursor)
    
    def get_branch_totals(self, boilers, date, branch_name):
        """
        """
        queries_path = os.path.join(os.path.dirname(__file__),'queries')
        queries_path = os.path.join(queries_path,'composite','branch.sql')
        
        query_file = open(queries_path,'r')
        day_coef = float(date.day)/float(get_month_last_day(date))
        
        cursor = connection.cursor()
        query = query_file.read()
        cursor.execute(query, {u'my_date': date, u'my_boiler': tuple(boilers),'branch': branch_name, 'day_coef': day_coef})
        query_file.close()
        
        return dictfetchall(cursor)

class CompositeconsumptionReport(models.Model):

    objects = CompositeconsumptionReportManager()
        
    date = models.DateField(verbose_name=u'Дата', help_text=u'')
    
    branch = models.CharField(verbose_name=u'Филиал', help_text=u'Филиал',
                              max_length=100, blank=False)
    thermal = models.CharField(verbose_name=u'Тепловой район', help_text=u'Тепловой район',
                               max_length=100, blank=False)
    boiler = models.CharField(verbose_name=u'Объект', help_text=u'Объект',
                              max_length=300, blank=False)
    # ТОПЛИВО
    fuel_type = models.CharField(verbose_name=u'Вид топлива', help_text=u'Вид используемого топлива',
                                 max_length=100, blank=True, default = "")
    fuel_mark = models.CharField(verbose_name=u'Марка топлива', help_text=u'Марка используемого топлива',
                                 max_length=100, blank=True, default = "")
    
    fuel_actual_eqv = models.FloatField(verbose_name=u'Фактический ТЭ', help_text=u'Фактический топливный эквивалент', default = 0.0)
    fuel_plan_eqv = models.FloatField(verbose_name=u'Плановый ТЭ', help_text=u'Плановый топливный эквивалент', default = 0.0)
    
    # ОКРУЖАЮЩАЯ СРЕДА
    actual_outdoor_temp = models.FloatField(verbose_name=u'ТНВ фактическая, °C', help_text=u'Температура наружного воздуха фактическая, °C', default = 0.0) 
    plan_outdoor_temp = models.FloatField(verbose_name=u'ТНВ плановая, °C', help_text=u'Температура наружного воздуха плановая, °C', default = 0.0)
    
    # ОСТАТКИ
    first_day_remains = models.FloatField(verbose_name=u'Остаток топл. на 1-е число месяца, ТНТ', help_text=u'Остаток топл. на 1-е число месяца, ТНТ', default = 0.0)
    
    # ПОСТУПЛЕНИЯ
    income_today = models.FloatField(verbose_name=u'За сутки, ТНТ', help_text=u'Приход топлива за сутки, ТНТ', default = 0.0)
    income_month = models.FloatField(verbose_name=u'За месяц, ТНТ', help_text=u'Приход топлива за месяц, ТНТ', default = 0.0)
    
    # РАСХОДЫ
    actual_fuel_consumption_ideal = models.FloatField(verbose_name=u'Факт за сутки, ТУТ', help_text=u'Фактический расход топлива за сутки, ТУТ', default = 0.0)
    plan_fuel_consumption_ideal = models.FloatField(verbose_name=u'План за сутки, ТУТ', help_text=u'Плановый расход топлива за сутки, ТУТ', default = 0.0)
    
    fuel_consumption_actual_day = models.FloatField(verbose_name=u'Факт за сутки, ТНТ', help_text=u'Фактический расход топлива за сутки, ТНТ', default = 0.0)
    fuel_consumption_plan_day = models.FloatField(verbose_name=u'План за сутки, ТНТ', help_text=u'Плановый дневной расход топлива за сутки, ТНТ', default = 0.0)
    fuel_consumption_diff_day = models.FloatField(verbose_name=u'', help_text=u'', default = 0.0)
    
    fuel_consumption_actual_month = models.FloatField(verbose_name=u'',help_text=u'', default = 0.0)
    fuel_consumption_plan_month = models.FloatField(verbose_name=u'',help_text=u'', default = 0.0)
    fuel_consumption_diff_month = models.FloatField(verbose_name=u'',help_text=u'', default = 0.0)

    # ВОДА
    water_consumption_category_name = models.CharField(verbose_name=u'Категория расхода воды',help_text=u'Категория расхода воды',max_length=100, blank=True)
    water_consumption_actual_day = models.FloatField(verbose_name=u'Факт за сутки, м³', help_text=u'Факт за сутки, м³',default = 0.0)
    water_consumption_plan_day = models.FloatField(verbose_name=u'План за сутки, м³', help_text=u'План за сутки, м³',default = 0.0)

    water_consumption_actual_month = models.FloatField(verbose_name=u'Факт за месяц, м³', help_text=u'Факт за месяц, м³', default = 0.0)
    water_consumption_plan_month = models.FloatField(verbose_name=u'План за месяц, м³', help_text=u'План за месяц, м³', default = 0.0)
    
    water_consumption_diff_day = models.FloatField(verbose_name=u'Отклонение за сутки, м³', help_text=u'Отклонение за сутки, м³', default = 0.0)
    water_consumption_diff_month = models.FloatField(verbose_name=u'Отклонение за месяц, м³', help_text=u'Отклонение за месяц, м³', default = 0.0)
    
    # ЭЛЕКТРИЧЕСТВО
    electricity_consumption_actual_day = models.FloatField(verbose_name=u'Факт суточного потребления, кВтч', help_text=u'Факт суточного потребления электроэнергии, кВтч', default = 0.0)
    electricity_consumption_plan_day = models.FloatField(verbose_name=u'План среднесуточного потребления, кВтч', help_text=u'План среднесуточного потребления электроэнергии, кВтч', default = 0.0)
    electricity_consumption_plan_month = models.FloatField(verbose_name=u'План на месяц, кВтч', help_text=u'План потребления электр. на месяц, кВтч', default = 0.0)
    
    electricity_consumption_actual_sum_period = models.FloatField(verbose_name=u'Фактическое потребление с начала месяца, кВтч', help_text=u'Фактическое потребление электроэнергии с начала месяца, кВтч', default = 0.0)
    electricity_consumption_plan_sum_period = models.FloatField(verbose_name=u'Плановое потребление с начала месяца, кВтч', help_text=u'Плановое потребление электроэнергии с начала месяца, кВтч', default = 0.0)
    electricity_consumption_diff_period_percent = models.FloatField(verbose_name=u'Отклонение с начала месяца, %', help_text=u'Отклонение фактического расхода от планового с начала месяца, %', default = 0.0)
    
    
    class Meta:
        verbose_name = u'Сводный отчет'
        ordering = ['date']
        db_table = "compositereport"

class DeviationsReportManager(models.Manager):
    
    def get_deviations(self, deviations_id):
        """
        """
        queries_path = os.path.join(REPORT_QUERIES_PATH ,'deviation','deviations.sql')
        query_file = open(queries_path,'r')
        
        cursor = connection.cursor()
        query = query_file.read()
        cursor.execute(query, {u'deviation_ids': tuple(deviations_id)})
        query_file.close()
        return dictfetchall(cursor)

class DeviationsReport(models.Model):
    objects = DeviationsReportManager() 

    class Meta:
        abstract = True
        
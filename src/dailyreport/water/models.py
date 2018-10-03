# -*- coding: utf-8 -*-

import reversion
import traceback
import sys
import logging
import os
import imputil

from django.db import models
from django.db.models import Sum
from django.contrib import admin
from django.contrib.auth.models import User

from dailyreport.utils.date_utils import get_month_last_day, get_range, get_month_day
from dailyreport.company_object.models import BoilerHouse

_logger = logging.getLogger(__name__)

# Путь к файлам с sql-запросами
REPORT_QUERIES_PATH = os.path.join(os.path.dirname(__file__),'queries')

def module_exists(module_name):
    print module_name
    a = [item for item in sys.modules.keys()]
    a.sort()
    for i in a: print i
    
    for line in traceback.format_stack():
        print line.strip()
        
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True

#print "!!!!!!!!!" +  unicode(module_exists('DatasetSourceDate'))
#print ">>>>>>>>>>>" +  unicode(module_exists('dailyreport.consumption.models.DatasetSourceDate'))
from dailyreport.consumption.models import DatasetSourceDate
from dailyreport.consumption.models import DatasetSourcePeriod

#import django.utils.importlib

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()]

class WaterConsumptionCategory(models.Model):
    """
    Информация о категории расхода по воде. Каждая котельная имеет 
    собственный набор категорий расхода воды.
    Если категория не актуальная, тогда active = False
    """
    created = models.DateTimeField(u'Дата создания', auto_now_add = True)
    creator = models.ForeignKey(User,
                        verbose_name=u'Кто создал',
                        blank=True, null=True,
                        related_name = "+",)
    
    edited = models.DateTimeField(u'Дата редактирования', auto_now = True)
    editor = models.ForeignKey(User,
                        verbose_name=u'Кто редактировал',
                        blank=True, null=True,
                        related_name = "+")
    
    boiler = models.ForeignKey(BoilerHouse, verbose_name=u'Котельная')    
    name = models.CharField(u'Наименование категории', max_length=100)
    
    active = models.BooleanField(u'Используется', default=True)
    parent = models.ForeignKey('WaterConsumptionCategory', verbose_name=u'Родительская категория',
                                null=True)
    
    
    class Meta:
        verbose_name = u'Категория расхода воды'
        ordering = ['boiler__branch__name','boiler__thermalArea__name','boiler__order_index','boiler__name','name']
        db_table = "water_consuption_category"
    
    class DescriptorMeta:
        source = False
        fields = ('name')
        
    def __unicode__(self):
        return unicode(self.boiler) + ": " + self.name  
    
    def save(self, save_revision = False, *args, **kwargs):
        
        #if save_revision == True:
        #    with reversion.create_revision():
        #        super(WaterConsumptionCategory, self).save( *args, **kwargs)
        #else:
        super(WaterConsumptionCategory, self).save( *args, **kwargs)


class WaterConsumptionManager(models.Manager):
    """
    
    """
    
    def get_consumption_data(self, boilers, from_date, to_date, aggregation_type):
        """
        
        """
        if aggregation_type not in ['enterprise','thermal','branch',None]:
            raise ValueError(u"Неизвестный тип аггрегации")
        
        query_path = ""
        if aggregation_type == 'enterprise':
            query_path = os.path.join(REPORT_QUERIES_PATH,'consumption','aggregate_by_enterprise.sql')
        elif aggregation_type == 'branch':
            query_path = os.path.join(REPORT_QUERIES_PATH,'consumption','aggregate_by_branch.sql')
        elif aggregation_type == 'thermal':
            query_path = os.path.join(REPORT_QUERIES_PATH,'consumption','aggregate_by_thermal.sql')
        else: #None
            query_path = os.path.join(REPORT_QUERIES_PATH,'consumption','without_aggregation.sql')

        query_file = open(query_path,'r')
        
        cursor = connection.cursor()
        cursor.execute(query_file.read(), {'boilers': boilers, 'from_date':from_date, 'to_date':to_date})
        query_file.close()
        
        return dictfetchall(cursor)

 
class WaterConsumption(DatasetSourceDate):
    """
    Ежедневный расход воды.
    
    Дневной расход - 
    Дневной план - 
    Месячный план расхода - 
    Разница между фактическим и плановым дневным значением - 
    Разница между суммами фактических и плановых дневных значений -  
    """
    objects = WaterConsumptionManager()
        
    category = models.ForeignKey(WaterConsumptionCategory, verbose_name = u"Категория расхода воды")
    
    plan_day = models.FloatField(u'План за сутки, м3',
                        default=0.0, null=False,
                        help_text=u'Плановый расход воды за сутки, м3')
    
    actual_day = models.FloatField(u'Факт за сутки, м3',
                        default=0.0, null=False,
                        help_text=u'Фактический расход воды за сутки, м3')
    
    diff_day = models.FloatField(u'Отклонение за сутки, м3',
                        default=0.0, null=False,
                        help_text=u'Отклонение расхода воды за сутки, м3')
    
    actual_month = models.FloatField(u'Факт за месяц, м3',
                        default=0.0, null=False,
                        help_text=u'Фактический расход за месяц (накопительное), м3')
    
    plan_month = models.FloatField(u'План на месяц, м3',
                        default=0.0, null=False,
                        help_text=u'Плановый расход воды на месяц, м3')
    
    diff_month = models.FloatField(u'Отклонение за месяц, м3',
                        default=0.0, null=False,
                        help_text=u'Отклонение расхода воды за месяц, м3')

    farward_temperature_estimated = models.FloatField(u'Температура прямой (расчетная)',
                                               default=-273.0, null=False,
                                               help_text=u'Температура прямой (расчетная)')
    
    backward_temperature_estimated = models.FloatField(u'Температура обратной (расчетная)',
                                                default=-273.0, null=False,
                                                help_text=u'Температура обратной (расчетная)')
    
    farward_temperature_actual = models.FloatField(u'Температура прямой (фактическая)',
                                               default=-273.0, null=False,
                                               help_text=u'Температура прямой (фактическая)')
    
    backward_temperature_actual = models.FloatField(u'Температура обратной (фактическая)',
                                                default=-273.0, null=False,
                                                help_text=u'Температура обратной (фактическая)')
    
    farward_temperature_diff = models.FloatField(u'Отклонение прямой',
                                                default=0.0, null=False,
                                                help_text=u'Отклонение прямой')
    backward_temperature_diff = models.FloatField(u'Отклонение обратной',
                                                default=0.0, null=False,
                                                help_text=u'Отклонение обратной')
    
    class Meta:
        verbose_name = u'Расход воды'
        ordering = ['date','boiler__branch__name','boiler__thermalArea__name','boiler__order_index','boiler__name']
        db_table = "water_consumption"
         
    class DescriptorMeta:
        source = True   # Данные являются источником набора данных
        date = True     # Данные за определенную дату
        fields = ('plan_day',
                'actual_day',
                'diff_day',
                'actual_month',
                'plan_month',
                'diff_month',
                'farward_temperature_estimated',
                'farward_temperature_actual',
                'farward_temperature_diff',
                'backward_temperature_estimated',
                'backward_temperature_actual',
                'backward_temperature_diff')

    def __unicode__(self):
        
        if self.boiler and self.boiler.name: 
            return u"Расход воды по " + self.boiler.name + u" на " +unicode(self.date)
        else:
            return u"Расход воды на " + unicode(self.date)
    
    def get_fields(self):
        return self._meta.fields
    
    def get_month_plan(self):
        """
        Получить плановое значние расхода на месяц и среднесуточное
        """
        
        if self.date.day != 1:
            first_day = get_month_day(self.date, 1)
            consumption = None

            try:
                # расход воды в первый день
                consumption = WaterConsumption.objects.get(date=first_day,
                                                            category__id = self.category.id)
            except WaterConsumption.DoesNotExist:
                _logger.info("The month plan doesn't exist on " + unicode(self.date))
                #traceback.print_exc(file=sys.stdout)
                #consumption = WaterConsumption(creator = self.editor,
                #                              date = first_day,
                #                              boiler = self.boiler,
                #                              category = self.category)
                #consumption.save(force_insert = True, save_revision=True)
                pass
            
            except WaterConsumption.MultipleObjectsReturned:
                traceback.print_exc(file=sys.stdout)
            
                is_first = True
                items = WaterConsumption.objects.filter(date = self.date,
                                      category__id = self.category.id)
                for item in items:
                    if is_first==True:
                        consumption = item
                        is_first=False
                    else:
                        item.delete()
            
            if consumption == None:
                return (0.0, 0.0)
            
            month = consumption.plan_month
            avg = round(month / float(get_month_last_day(self.date)), 3)
            
            return (month, avg)

        return (0.0, 0.0)
    
    def update_period(self):
        """
        Обновить все записи периода.
        """
        days = get_month_last_day(self.date)
        records = WaterConsumption.objects.exclude(date = self.date).filter(category__id = self.category.id)
        
        for record in records:
            print record.date
            #record.editor = self.editor
            record.save(force_update=True)
            
    def save(self, save_revision=False, *args, **kwargs):
        # количество дней в месяце  
        days = get_month_last_day(self.date)
        
        if self.category == None:
            raise WaterConsumption.DoesNotExist("Категория расхода воды не указана.")
        
        if self.date.day == 1:
            self.actual_month = self.actual_day
            self.plan_day = round(self.plan_month/float(days), 3)
        else:
            
            # диапазон дат с начала месяца по текущий день 
            date_range = get_range(self.date, -1)
            
            # фактический расход за период
            total_actual = WaterConsumption.objects.filter(date__range=date_range,
                             boiler__id = self.boiler.id,
                             category__id = self.category.id).aggregate(actual_month=Sum('actual_day')) 
            
            if total_actual['actual_month'] == None:
                total_actual['actual_month'] = 0
            
            self.actual_month = total_actual['actual_month'] + self.actual_day

            # Плановые дневные и месячные значения            
            month_plan, day_plan = self.get_month_plan()
            self.plan_month = month_plan
            self.plan_day = day_plan
            
        # вычисляем разницы
        self.diff_day = round(self.actual_day - self.plan_day, 3)
        self.diff_month = round(self.actual_month - (self.plan_day * self.date.day), 3)
        
        self.farward_temperature_diff = self.farward_temperature_actual - self.farward_temperature_estimated
        self.backward_temperature_diff = self.backward_temperature_actual - self.backward_temperature_estimated
        
        #if save_revision == True:
        #    with reversion.create_revision():
        #        super(WaterConsumption,self).save( *args, **kwargs)
        #else:
        super(WaterConsumption,self).save( *args, **kwargs)
        
        #water_consumption_changed.send(WaterConsumption, entity=self)



class WaterConsumptionPeriodic(DatasetSourcePeriod):
    """
    Расход воды за период.
    """
    category = models.ForeignKey(WaterConsumptionCategory, verbose_name = u"Категория расхода воды")

    plan = models.FloatField(u'План, м3',
                        default=0.0, null=False,
                        help_text=u'Плановый расход воды за период, м3')
    
    actual = models.FloatField(u'Факт, м3',
                        default=0.0, null=False,
                        help_text=u'Фактический расход воды за период, м3')

    class Meta:
        verbose_name = u'Расход воды за период'
        ordering = ['start','boiler__branch__name','boiler__thermalArea__name','boiler__order_index','boiler__name']
        db_table = "water_consumption_periodic"
         
    class DescriptorMeta:
        source = False
        date = False
        fields = ('plan',
                'actual')

    def __unicode__(self):
        return u"%(boiler)s | %(category)s | %(start)s - %(end)s" % {'boiler': unicode(self.boiler),
                                                                     'category': unicode(self.category),
                                                                     'start': unicode(self.start),
                                                                     'end': unicode(self.end)} 
    
    def update_categories(self):
        """
        Обновить значения родительских категорий        
        """
    
    def save(self, save_revision=False, *args, **kwargs):
        #if save_revision == True:
        #    with reversion.create_revision():
        #        super(WaterConsumptionPeriodic,self).save( *args, **kwargs)
        #else:
        super(WaterConsumptionPeriodic,self).save( *args, **kwargs)
    

class WaterConsumptionAdmin(admin.ModelAdmin):
    pass

class WaterConsumptionPeriodicAdmin(admin.ModelAdmin):
    pass

class WaterConsumptionCategoryAdmin(admin.ModelAdmin):
    pass

#reversion.register(WaterConsumptionCategory)
#reversion.register(WaterConsumption)
#reversion.register(WaterConsumptionPeriodic)
admin.site.register(WaterConsumptionCategory, WaterConsumptionCategoryAdmin)
admin.site.register(WaterConsumption, WaterConsumptionAdmin)
admin.site.register(WaterConsumptionPeriodic, WaterConsumptionPeriodicAdmin)
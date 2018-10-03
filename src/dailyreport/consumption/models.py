# -*- coding: utf-8 -*-

import reversion
import traceback
import sys

from django.db import models
from django.db.models import Sum
from django.contrib import admin

from dailyreport.core.models import HistoryModel
from dailyreport.utils.date_utils import get_range, get_month_day, get_month_last_day
from dailyreport.company_object.models import BoilerHouse

class DatasetSourceDate(HistoryModel):
    """
    Базовый класс модели для всех моделей содержащих данные по отчетности
    """
    date = models.DateField(u'Дата')
    boiler = models.ForeignKey(BoilerHouse, verbose_name=u"Котельная")
    
    class Meta:
        abstract = True
    
    class DescriptorMeta:
        # указывает на то, что данная модель является источником данных 
        source = False
        # Указывает на то, что данная модель привязана к дате (True) или нет (False) 
        date = True
        
class DatasetSourcePeriod(HistoryModel):
    """
    Базовый класс модели для всех моделей содержащих данные по отчетности
    """
    start = models.DateField(u'Дата начала')
    end = models.DateField(u'Дата окончания')
    boiler = models.ForeignKey(BoilerHouse, verbose_name=u"Котельная")
    
    class Meta:
        abstract = True
    
    class DescriptorMeta:
        # указывает на то, что данная модель является источником данных 
        source = False
        # Указывает на то, что данная модель привязана к дате (True) или нет (False)
        date = False

class Environment(DatasetSourceDate):
    """
    Показатели окружающей среды
    """
    # Температура наружного воздуха
    outdoor_temp_actual = models.FloatField(u'Температура наружного воздуха факт.',
                                             default=-273.0, null=False)
    outdoor_temp_plan = models.FloatField(u'Температура наружного воздуха план.',
                                           default=-273.0, null=False)
    
    class Meta:
        verbose_name = u'Показатели окружающей среды'
        ordering = ['date']
        db_table = "environment"
    
    class DescriptorMeta:
        source = True
        fields = ('outdoor_temp_actual',
               'outdoor_temp_plan')
        
    def get_fields(self):
        return self._meta.fields
    
    def update_period(self):
        """
        Обновить все записи периода.
        """
        records = Environment.objects.exclude(date=self.date).filter(boiler__id = self.boiler.id)

        for record in records:
            #record.editor = self.editor
            record.save(force_update=True)
    
    def get_month_plan(self):
        """
        Получить плановое значние расхода на месяц и среднесуточное
        """
        if self.date.day != 1:
            first_day = get_month_day(self.date, 1)
            environment = None

            try:
                # расход воды в первый день
                environment = Environment.objects.get(date=first_day,
                                                     boiler__id = self.boiler.id)
            except Environment.DoesNotExist:
                traceback.print_exc(file=sys.stdout)
                #environment = Environment(creator = self.editor,
                #                          date = first_day,
                #                          boiler = self.boiler)
                #environment.save(force_insert = True, save_revision=True)
                
            except Environment.MultipleObjectsReturned:
                traceback.print_exc(file=sys.stdout)
            
                is_first = True
                items = Environment.objects.filter(date = first_day,
                                      boiler__id = self.boiler.id)
                for item in items:
                    if is_first==True:
                        environment = item
                        is_first=False
                    else:
                        item.delete()

            if environment == None:
                return 0.0
              
            month = environment.outdoor_temp_plan
            return month

        return 0.0
    
    def save(self, save_revision=False, *args, **kwargs):
        if self.date.day == 1:
            pass
        else:
            self.outdoor_temp_plan = self.get_month_plan()
                    
        #if save_revision == True:
        #    with reversion.create_revision():
        #        super(Environment, self).save( *args, **kwargs)
        #else:
        super(Environment, self).save( *args, **kwargs)



class PowerPerformance(DatasetSourceDate):
    """
    Показатели производительности котельной
    """
    
    # Показания УУТЭ (узла учета тепловой энергии)
    energy_value = models.FloatField(u'Количество ТЭ за сутки по показаниям УУТЭ, Гкал', default=0.0,
                                     null=False, help_text=u'Количество ТЭ за сутки по показаниям УУТЭ, Гкал')
    
    # Показания УУТЭ (узла учета тепловой энергии)
    energy_value_month = models.FloatField(u'Количество ТЭ по показаниям УУТЭ (накопительно), Гкал',
                                           default=0.0, null=False,
                                           help_text=u'Количество ТЭ по показаниям УУТЭ (накопительно), Гкал')
    
    class Meta:
        verbose_name = u'Показатели производительности'
        ordering = ['date']
        db_table = "power_performance"
    
    class DescriptorMeta:
        source = True
        fields = ('energy_value', 'energy_value_month')
    
    def update_period(self):
        """
        Обновить все записи периода.
        """
        records = PowerPerformance.objects.exclude(date=self.date).filter(boiler__id = self.boiler.id)

        for record in records:
            #record.editor = self.editor
            record.save(force_update=True)
    
    def save(self, save_revision=False,  *args, **kwargs):
        
        # Если первый день месяца, тогда:
        #  - сумма потребления фактическая и плановая за период 
        # равна текущим значениям 
        # 
        # Количество дней в месяце
        days_number = get_month_last_day(self.date)
        
        if self.date.day == 1:
            self.energy_value_month = self.energy_value
        else:
            # пара значений даты начала и пердыдущего дня месяца
            actual_month_range = get_range(self.date, -1)
            
            # Сумма потребления с начала месяца до вчерашнего дня
            energy_sum = PowerPerformance.objects.filter(date__range=actual_month_range,
                boiler__id=self.boiler.id).aggregate(consumption_sum=Sum('energy_value'))

            if energy_sum['consumption_sum'] == None:
                energy_sum['consumption_sum']=0

            self.energy_value_month = energy_sum['consumption_sum'] + self.energy_value
        
        #if save_revision == True:
        #    with reversion.create_revision():
        #        super(PowerPerformance, self).save( *args, **kwargs)
        #else:
        super(PowerPerformance, self).save( *args, **kwargs)

class PowerPerformanceAdmin(admin.ModelAdmin):
    pass
class EnvironmentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Environment, EnvironmentAdmin)
admin.site.register(PowerPerformance, PowerPerformanceAdmin)









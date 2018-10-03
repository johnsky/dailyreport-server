# -*- coding: utf-8 -*-

import reversion
import traceback
import sys

from django.db import models
from django.db.models import Sum
from django.contrib import admin
from django.contrib.auth.models import User
 
from dailyreport.consumption.models import DatasetSourceDate
from dailyreport.utils.date_utils import get_range, get_month_day, get_month_last_day

class ElectricityConsumption(DatasetSourceDate):
    """
    Расход электричества по котельной на дату
    """   
    plan_month = models.FloatField(u'План на месяц, кВтч',
                                   default=0.0, null=False,
                                   help_text=u'Плановый расход электроэнергии на месяц, кВтч')
    
    plan_day = models.FloatField(u'План среднесуточного потребления электроэнергии, кВтч ',
                                default=0.0, null=False, editable=False)
    
    actual_day = models.FloatField(u'Факт суточного потребления электр., кВтч',
                                    default=0.0, null=False)
    
    diff_period_percent = models.FloatField(u'Отклонение фактического потребления от планового с начала отчетного месяца, %',
                                           default=0.0, editable=False, null=False)
    
    plan_sum_period = models.FloatField(u'План потребление электроэнергии с начала отчетного месяца, кВтч',
                                        default=0.0, editable=False, null=False)
    
    actual_sum_period = models.FloatField(u'Фактическое потребление электроэнергии с начала отчетного месяца, кВтч',
                                          default=0.0, editable=False, null=False)
        
    def get_fields(self):
        return self._meta.fields

    class Meta:
        verbose_name = u'Расход электричества'
        ordering = ['date']
        db_table = "electicity_consumption"
    
    class DescriptorMeta:
        source = True
        date = True
        fields = ('plan_month',
                'plan_day',
                'actual_day',
                'diff_period_percent',
                'plan_sum_period',
                'actual_sum_period')
    
    def __unicode__(self):
        return u"Electricity consumption " + self.boiler.name + u" on " +unicode(self.date)
    
    def get_month_plan(self):
        """
        Получить плановое значние расхода на месяц и среднесуточное
        """
        if self.date.day != 1:
            first_day = get_month_day(self.date, 1)
            consumption = None

            try:
                # расход воды в первый день
                consumption = ElectricityConsumption.objects.get(date=first_day,
                                                                 boiler__id = self.boiler.id)
            except ElectricityConsumption.DoesNotExist:
                traceback.print_exc(file=sys.stdout)
                #consumption = ElectricityConsumption(creator = self.editor,
                #                              date = first_day,
                #                              boiler = self.boiler)
                #consumption.save(force_insert = True, save_revision=True)
                
            except ElectricityConsumption.MultipleObjectsReturned:
                traceback.print_exc(file=sys.stdout)

                is_first = True
                items = ElectricityConsumption.objects.filter(date = self.date,
                                      boiler__id = self.boiler.id)
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
        records = ElectricityConsumption.objects.exclude(date=self.date).filter(boiler__id = self.boiler.id)

        for record in records:
            #record.editor = self.editor
            record.save(force_update=True)
    
    def save(self, save_revision=False,*args, **kwargs):
        
        # Если первый день месяца, тогда:
        #  - сумма потребления фактическая и плановая за период 
        # равна текущим значениям 
        # 
        # Количество дней в месяце
        days_number = get_month_last_day(self.date)
        if self.date.day == 1:
            self.plan_day = round(self.plan_month / days_number, 3)
            self.plan_sum_period = self.plan_day
            self.actual_sum_period = self.actual_day
        else:
            # пара значений даты начала и пердыдущего дня месяца
            actual_month_range = get_range(self.date, -1)
            
            # Сумма потребления с начала месяца до вчерашнего дня
            actual_sum = ElectricityConsumption.objects.filter(date__range=actual_month_range,
                boiler__id=self.boiler.id).aggregate(consumption_sum=Sum('actual_day'))

            if actual_sum['consumption_sum'] == None:
                actual_sum['consumption_sum']=0
            
            # среднесуточные значения и плановые месячные
            month, avg = self.get_month_plan()
            self.plan_day = avg
            self.plan_month = month
            
            # сумма равна сумме сегоднешнего значения и суммы всех значений с первого дня месяца
            # по вчерашнее число
            self.plan_sum_period = round((self.plan_month / days_number) * self.date.day, 3) 
            self.actual_sum_period = actual_sum['consumption_sum'] + self.actual_day
            
        # Вычислить отклонение в процентах планового и фактического значений за период
        if self.plan_sum_period > 0:
            delta = ((self.actual_sum_period*100.0)/self.plan_sum_period) - 100.0
            self.diff_period_percent = round(delta, 3)
        
        #if save_revision == True:
        #    with reversion.create_revision():
        #        super(ElectricityConsumption,self).save( *args, **kwargs)
        #else:
        super(ElectricityConsumption,self).save( *args, **kwargs)

        #    electricity_consumption_changed.send(ElectricityConsumption, entity=self)

class ElectricityConsumptionAdmin(admin.ModelAdmin):
    pass

# Регистрируем объкт длоя получения истории по нему
#reversion.register(ElectricityConsumption)
admin.site.register(ElectricityConsumption, ElectricityConsumptionAdmin)
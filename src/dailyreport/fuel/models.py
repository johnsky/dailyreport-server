# -*- coding: utf-8 -*-
import reversion
import traceback
import sys
import logging

from django.db import models
from django.db.models import Sum
from django.contrib import admin
from django.contrib.auth.models import User

from dailyreport.consumption.models import DatasetSourceDate
from dailyreport.company_object.models import BoilerHouse, Period
from dailyreport.utils.date_utils import get_range, get_month_day, get_month_last_day, get_month_range, get_range_revers, contains

_logger=logging.getLogger(__name__)

class FuelInfo(models.Model):
    """
    Информация о топливе. 
    Такая информация для каждой котельной указывается отдельно. 
    Если информация не актуальная active=False
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
    type = models.CharField(u'Вид отплива', max_length=100, default="")
    active = models.BooleanField(u'Используется', default=True)    
    
    class Meta:
        verbose_name = u'Иформация о топливе'
        ordering = ['boiler__branch__name','boiler__thermalArea__name','boiler__order_index','boiler__name','type']
        db_table = "fuel_info"
    
    class DescriptorMeta:
        source = False
        date = False
        fields = ('type')
        
    def __unicode__(self):
        return unicode(self.boiler) + ": " + self.type

    def save(self, save_revision = False, *args, **kwargs):
        #if save_revision == True:
        #    with reversion.create_revision():
        #        super(FuelInfo, self).save( *args, **kwargs)
        #else:
        super(FuelInfo, self).save( *args, **kwargs)


class FuelIncome(DatasetSourceDate):
    """
    Поступление топлива для определенной котельной на отчетную дату
    """
    fuel_info = models.ForeignKey(FuelInfo, verbose_name=u"Информация о топливе")
    
    # Приход топлива, т
    today = models.FloatField(u'Приход топлива за сутки, т',
                        default=0.0, null=False)
    month = models.FloatField(u'Приход топлива всего за месяц, т',
                        editable=False, default=0.0, null=False)
    pickup = models.FloatField(u'Самовывоз, т',
                        default=0.0, null=False)
    pickup_sum_period = models.FloatField(u'Самовывоз (накопительно), т',
                        default=0.0, null=False)

    class Meta:
        verbose_name = u'Поступление топлива'
        ordering = ['date']
        db_table = "fuel_income"
        
    
    class DescriptorMeta:
        source = True
        date = True
        fields = ('today',
                'month',
                'pickup', 
                'pickup_sum_period')
    
    
    def update_period(self):
        """
        Обновить все записи периода.
        """
        records = FuelIncome.objects.exclude(date=self.date).filter(fuel_info__id = self.fuel_info.id)
        for record in records:
            #record.editor = self.editor
            record.save(force_update=True)
        
        try:
            obj = FuelRemains.objects.get(date = self.date,
                                  fuel_info__id = self.fuel_info.id)
            obj.save(force_update=True)
        
        except FuelRemains.DoesNotExist:
            #_logger.info("There's not fuel remains on "+ unicode(self.date))
            #traceback.print_exc(file=sys.stdout)
            #obj = FuelRemains()
            #obj.date = self.date
            #obj.fuel_info = self.fuel_info
            #obj.boiler = self.boiler
            #obj.creator = self.editor
            #obj.save(save_revision=True, force_insert=True)
            pass
           
        except FuelRemains.MultipleObjectsReturned:
            #traceback.print_exc(file=sys.stdout)
            is_first = True
            items = FuelRemains.objects.filter(date = self.date,
                                  fuel_info__id = self.fuel_info.id)
            for item in items:
                if is_first==True:
                    is_first=False
                    item.save(force_update=True)
                else:
                    item.delete()
        
    def save(self, save_revision=False, *args, **kwargs):

        if self.fuel_info == None:
            raise FuelIncome.DoesNotExist("Информация о топливе не указана.")
        
        if self.date.day == 1:
            self.month = self.today
        else:
            date_range = get_range(self.date,-1)
            aggregation = FuelIncome.objects.filter(date__range=date_range,
                             fuel_info__id = self.fuel_info.id).aggregate(month=Sum('today'), pickup=Sum('pickup'))
            
            if aggregation['month'] == None:
                aggregation['month'] = 0.0
            
            if aggregation['pickup'] == None:
                aggregation['pickup'] = 0.0
                
            self.month = aggregation['month'] + self.today
            self.pickup_sum_period = aggregation['pickup'] + self.pickup
        
        #if save_revision == True:
        #    with reversion.create_revision():
        #        super(FuelIncome, self).save( *args, **kwargs)
        #else:
        super(FuelIncome, self).save( *args, **kwargs)


class FuelRemains(DatasetSourceDate):
    """
    Остатки топлива по котельной на отчетную дату
    """
    
    fuel_info = models.ForeignKey(FuelInfo, verbose_name=u"Информация о топливе")
    
    # Остаток топлива на отчетную дату, тонн
    tonnes = models.FloatField(u'Остаток топлива на отчетную дату, т',
                      default=0.0, editable=False, null=False,
                      help_text=u"Остаток топлива на отчетную дату, т")
    
    days = models.FloatField(u'Остаток топлива на отчетную дату, в днях',
                      default=0.0, editable=False, null=False,
                      help_text=u"Остаток топлива на отчетную дату, в днях")
    
    first_day_month = models.FloatField(u'Остаток топлива на 1-е число месяца, т',
                      default=0.0, null=False,
                      help_text=u"Остаток топлива на 1-е число месяца, т")
    
    class Meta:
        verbose_name = u'Остатки топлива'
        ordering = ['date']
        db_table = "fuel_remain"
         
    class DescriptorMeta:
        source = True
        date = True
        fields = ('tonnes',
                'days',
                'first_day_month')

    def calc_remain_tonnes(self, initial, income, consumption, pickup):
        """
        Рассчитать остаток в тоннах.
        <Остаток на 1е число месяца> + <Поступления за месяц> - <Фактический расход за месяц> - <Самовывоз>
        
        @param initial: остаток на первое число месяца 
        @param income: поступления
        @param consumption: расход
        @param pickup: самовывоз
        """
        
        remains = initial + income - consumption - pickup
        return remains
    
    def update_period(self):
        """
        Обновить все записи периода.
        """
        days = get_month_last_day(self.date)
        month_range = [get_month_day(self.date,2), get_month_day(self.date, days)] 
        
        records = FuelRemains.objects.filter(date__range = month_range,
                                                    fuel_info__id = self.fuel_info.id)
        for record in records:
            #record.editor = self.editor
            record.save(force_update=True)
            
    def save(self, save_revision=False, *args, **kwargs):
        
        if self.fuel_info == None:
            raise FuelRemains.DoesNotExist("Информация о топливе не указана.")
        
        first_day = get_month_day(self.date, 1)
        range = get_range(self.date)
        
        if self.date.day == 1:
            pass
        else:
            try:
                obj = FuelRemains.objects.get(date = first_day,
                                                fuel_info__id = self.fuel_info.id)
                self.first_day_month = obj.first_day_month
            except FuelRemains.DoesNotExist:
                #traceback.print_exc(file=sys.stdout)
                #obj = FuelRemains()
                #obj.date = first_day
                #obj.fuel_info = self.fuel_info
                #obj.boiler = self.boiler
                #obj.creator = self.editor
                #obj.save(save_revision=True, force_insert=True)
                #self.first_day_month = obj.first_day_month
                pass
                
            except FuelRemains.MultipleObjectsReturned:
                #traceback.print_exc(file=sys.stdout)
                items = FuelRemains.objects.filter(date = first_day,
                                                fuel_info__id = self.fuel_info.id)
                is_first = True
                for item in items:
                    if is_first==True:
                        self.first_day_month = item.first_day_month
                        is_first=False
                    else:
                        item.delete()
                                                
        fc = FuelConsumption.objects.filter(date__range = range,
                             fuel_info__id = self.fuel_info.id).aggregate(actual=Sum('actual_day'))

        if fc['actual'] == None:
            fc['actual'] = 0.0
        
        fi = FuelIncome.objects.filter(date__range=range,
                                       fuel_info__id = self.fuel_info.id).aggregate(income=Sum('today'), pickup=Sum('pickup'))

        if fi['income'] == None:
            fi['income'] = 0.0
    
        if fi['pickup'] == None:
            fi['pickup'] = 0.0
        
        self.tonnes = round(self.calc_remain_tonnes(self.first_day_month,
                                       fi['income'],
                                       fc['actual'], 
                                       fi['pickup']), 3)
        self.days = 0
        
        #if save_revision == True:
        #    with reversion.create_revision():
        #        super(FuelRemains, self).save( *args, **kwargs)
        #else:
        super(FuelRemains, self).save( *args, **kwargs)   
        
        
            # отправляем сигнал о завершении
        #    fuel_remain_changed.send(FuelRemains, entity=self)




class FuelConsumption(DatasetSourceDate):
    """
    Расход топлива по котельной на отчетную дату по виду топлива.
    """
    fuel_info = models.ForeignKey(FuelInfo, verbose_name=u"Информация о топливе")
    
    # Марка топлива
    mark = models.CharField(u'Марка топлива', max_length=50, default="")
    
    # Топливный эквивалент 
    actual_eqv = models.FloatField(u'Фактический ТЭ', default=0.0,
                                   help_text=u'Фактический топливный эквивалент')
    plan_eqv = models.FloatField(u'Плановый ТЭ', default=0.0,
                                 help_text=u'Плановый топливный эквивалент')
    
    # Экономия(+)/перерасход(-)
    diff_day = models.FloatField(u'Экономия(-)/перерасход(+) за сутки',
                     default=0.0, editable=False,null=False,
                     help_text=u'Экономия(-)/перерасход(+) за сутки')
    
    diff_month = models.FloatField(u'Экономия(-)/перерасход(+) за месяц',
                     default=0.0, editable=False,null=False,
                     help_text=u'Экономия(-)/перерасход(+) за месяц')
    
    correct = models.FloatField(u'Корректировка за месяц, т',
                     default=0.0,
                     help_text=u'Корректировка за месяц, т')
                     
    # Расход топлива
    actual_day = models.FloatField(u'Расход фактический за сутки, т', default=0.0,
                     help_text=u'Расход топлива фактический за сутки, т')
    plan_day = models.FloatField(u'Расход плановый за сутки, т', default=0.0,
                     help_text=u'Расход топлива плановый за сутки, т')
    
    plan_month_sum = models.FloatField(u'Расход плановый за месяц (накопительно), т', default=0.0,
                     editable=False)
    
    actual_month = models.FloatField(u'Расход фактический за месяц, т', default=0.0,
                     editable=False, help_text=u'Расход топлива фактический за месяц, т')
    plan_month = models.FloatField(u'Расход плановый за месяц, т', default=0.0,
                     editable=False, help_text=u'Расход топлива плановый за месяц, т')    
    
    real_plan_day = models.FloatField(u'План с учетом ТЭ и ТНВ за сутки, т', default=0.0,null=False,
                     help_text=u'План с учетом ТЭ и ТНВ за сутки, т')
    
    real_plan_sum = models.FloatField(u'План c учетом фактической ТЭ и ТНВ за месяц, т', default=0.0,null=False,
                     help_text=u'План c учетом фактической ТЭ и ТНВ за месяц, т')
    
    correct_changed = False
     
    class Meta:
        verbose_name = u'Расход топлива'
        ordering = ['date']
        db_table = "fuel_consumption"
         
    class DescriptorMeta:
        source = True
        date = True
        fields = ('mark',
                    'actual_eqv',
                    'plan_eqv',
                    'diff_day',
                    'diff_month',
                    'actual_day',
                    'plan_day',
                    'actual_month',
                    'plan_month',
                    'real_plan_day',
                    'real_plan_sum',
                    'correct')
        
    def __unicode__(self):
        return u"Расход топлива по " +self.boiler.name + u" на " +unicode(self.date)
    
    def get_fields(self):
        return self._meta.fields
    
    def get_plan(self, days):
        """
        Получить плановое значние расхода на месяц и среднесуточное.
        Плановые значения указываются 1-го числа каждого месяца.
        """
        
        if self.date.day != 1:
            first_day = get_month_day(self.date, 1)
            consumption = None

            try:
                # расход топлива в первый день
                consumption = FuelConsumption.objects.get(date=first_day,
                                                            fuel_info__id = self.fuel_info.id)
            except FuelConsumption.DoesNotExist:
                #consumption = FuelConsumption(creator = self.editor,
                #                              date = first_day,
                #                              boiler = self.boiler,
                #                              fuel_info = self.fuel_info)
                #consumption.save(force_insert = True, save_revision=True)
                pass
            
            except FuelConsumption.MultipleObjectsReturned:
                #traceback.print_exc(file=sys.stdout)
                items = FuelConsumption.objects.filter(date = first_day,
                                                fuel_info__id = self.fuel_info.id)
                is_first = True
                for item in items:
                    if is_first==True:
                        consumption = item
                        is_first=False
                    else:
                        item.delete()
             
            if consumption == None:
                return (0.0, 0.0, 0.0)
            
            month = consumption.plan_month
            
            avg = 0.0
            if days > 0:
                avg = round(month / float(days), 3)
            
            plan_eqv = consumption.plan_eqv
            #actual_eqv = consumption
            
            return (month, avg, plan_eqv)

        return (0.0, 0.0, 0.0)
    
    def update_period(self):
        """
        Обновить все записи периода.
        """
        records = FuelConsumption.objects.exclude(date = self.date).filter(fuel_info__id=self.fuel_info.id)
        
        for record in records:
            #record.editor = self.editor
            if self.correct_changed:
                record.correct = self.correct
            record.save(force_update=True)
            
        try:
            obj = FuelRemains.objects.get(date = self.date,
                                  fuel_info__id = self.fuel_info.id)
            
            obj.save(force_update=True)
        except FuelRemains.DoesNotExist:
            traceback.print_exc(file=sys.stdout)
            #obj = FuelRemains()
            #obj.date = self.date
            #obj.fuel_info = self.fuel_info
            #obj.boiler = self.boiler
            #obj.creator = self.editor
            #obj.save(save_revision=True, force_insert=True)
            pass
        
        except FuelRemains.MultipleObjectsReturned:
            traceback.print_exc(file=sys.stdout)
            
            is_first = True
            items = FuelRemains.objects.filter(date = self.date,
                                  fuel_info__id = self.fuel_info.id)
            for item in items:
                if is_first==True:
                    item.save(force_update=True)
                    is_first=False
                else:
                    item.delete()
    
    def get_plan_period(self):
        """
        Получить плановый период для текущей даты и количество дней в периоде.
        
        - Если ни один период не начинается в текущем месяце, тогда начало периода совпадает с началом месца
        - Если ни один период не заканчивается в текущем месяце, тогда окончание периода совпадает с окончанием месяца
        - Если существует несколько периодов, которые пересекаются на текущую дату, первый из них будет удален                
        """

        period = None
        days = 0
        start_date=end_date = None
        
        try:
            # Найти период, который включает текущую дату
            period = self.boiler.periods.get(start__lte = self.date, end__gte = self.date)
            #print periods.query
        except Period.DoesNotExist:
            # Если период не найден, нужно убедиться есть ли период заканчивающийся в этом месяце
            # или период начинающийся в этом месяце
            days = get_month_last_day(self.date)
            # Все периоды, которые начинаются в месяце соответствующем дате
            s = self.boiler.periods.filter(start__month = self.date.month, start__year = self.date.year)
            # Все периоды, которые заканчиваются в месяце соответствующем дате
            e = self.boiler.periods.filter(end__month = self.date.month, end__year = self.date.year)
            
            start_date, end_date = get_month_range(self.date.year, self.date.month)
            
            # Если есть периоды, которые начинаются в текущем месяце,
            # тогда дата окончания периода равна 'дата начала' - 1
            if len(s)>0:
                end_date = get_month_day(self.date, s[0].start.day-1)
                days = 0 #end_date.day
            
            if len(e)>0:
                start_date = e[0].end
                days = 0 #end_date.day - start_date.day + 1
            
        except Period.MultipleObjectsReturned:
            items = self.boiler.periods.filter(start__lte = self.date, end__gte = self.date)

            is_first = True
            # Удаляем пересекающиеся периоды, кроме первого
            for item in items:
                if is_first==True:
                    period = item
                    is_first=False
                else:
                    item.delete()

        if period != None:
            # период первого месяца с даты начала периода, до последнего дня месяца
            start_period = get_range_revers(period.start)
            #print start_period
            # период последнего месяца с даты начала, до даты окончания периода
            end_period = get_range(period.end)
            #print end_period
            
            # Если дата расхода содержится в первом месячном периоде
            if contains(start_period, self.date):
                start_date = start_period[0]
                end_date = start_period[1]
                days = start_period[1].day - start_period[0].day + 1
            
            # Если дата расхода содержится в последнем месячном периоде
            elif contains(end_period, self.date):
                start_date = end_period[0]
                end_date = end_period[1]
                days = end_date.day 
            else:
                days = get_month_last_day(self.date)
                start_date, end_date = get_month_range(self.date.year, self.date.month)
                        
        return (start_date, end_date, days)

          
    def save(self, save_revision=False, *args, **kwargs):
        # количество дней в месяце  
        start_date,end_date,days = self.get_plan_period()
        
        if self.fuel_info == None:
            raise FuelConsumption.DoesNotExist("Информация о виде топлива не указана.")
        
        # На первое число месячное значение равно дневному
        if self.date.day == 1:
            self.actual_month = self.actual_day
            self.real_plan_sum = self.real_plan_day
            
            if days > 0:
                self.plan_day = round(self.plan_month/ float(days), 3)
            else:
                self.plan_day = 0.0
            self.plan_month_sum = self.plan_day
            
        else:
            # диапазон дат с начала месяца по текущий день 
            date_range = get_range(self.date, -1)
            
            aggregation = FuelConsumption.objects.filter(date__range=date_range,
                             fuel_info__id=self.fuel_info.id).aggregate(actual_sum=Sum('actual_day'),
                                                                        real_sum=Sum('real_plan_day'),
                                                                        plan_sum=Sum('plan_day'))
            for key in aggregation.keys():
                if aggregation[key] == None:
                    aggregation[key] = 0
                    
            #if aggregation['actual_sum'] == None:
            #    aggregation['actual_sum'] = 0
            
            #if aggregation['real_sum'] == None:
            #    aggregation['real_sum'] = 0
            
            print aggregation 
            self.actual_month = aggregation['actual_sum'] + self.actual_day
            self.real_plan_sum = aggregation['real_sum'] + self.real_plan_day
            
            # Плановые дневные и месячные значения            
            month_plan,day_plan, plan_eqv = self.get_plan(days)
            self.plan_month = month_plan
            self.plan_eqv = plan_eqv

            if days > 0:
                self.plan_day = day_plan
            else:
                self.plan_day = 0.0
            
            self.plan_month_sum = round(aggregation['plan_sum']+self.plan_day, 3)
            
        # Проверка того, что была сделана корректировка
        self.correct_changed = False
        if self.pk is not None:
            orig = FuelConsumption.objects.get(pk=self.pk)
            if orig.correct != self.correct:
                self.correct_changed = True
        elif self.correct != 0.0:
            self.correct_changed = True
            
        # вычисляем разницы
        self.diff_day = round(self.actual_day - self.real_plan_day, 3)
        self.diff_month = round(self.actual_month + self.correct - self.real_plan_sum, 3)
       
        #if save_revision == True:
        #    with reversion.create_revision():
        #        super(FuelConsumption, self).save(*args, **kwargs)
        #else:
        super(FuelConsumption, self).save(*args, **kwargs)
        
        records = FuelConsumption.objects.exclude(date = self.date).filter(fuel_info__id=self.fuel_info.id)



class FuelInfoAdmin(admin.ModelAdmin):
    pass
class FuelConsumptionAdmin(admin.ModelAdmin):
    pass
class FuelRemainsAdmin(admin.ModelAdmin):
    pass
class FuelIncomeAdmin(admin.ModelAdmin):
    pass

#reversion.register(FuelIncome)
#reversion.register(FuelRemains)
#reversion.register(FuelConsumption)
#reversion.register(FuelInfo)

admin.site.register(FuelInfo, FuelInfoAdmin)
admin.site.register(FuelConsumption, FuelConsumptionAdmin)
admin.site.register(FuelRemains, FuelRemainsAdmin)
admin.site.register(FuelIncome, FuelIncomeAdmin)
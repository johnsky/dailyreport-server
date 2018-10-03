# -*- coding: utf-8 -*-

import datetime
import reversion

from django.db import models
from django.contrib import admin
from django.conf import settings

from dailyreport.core.models import HistoryModel
from dailyreport.utils.date_utils import current_year


def start_period():
    """
    Начало периода
    """
    year = current_year()
    return datetime.date(year, 10, 1)

def end_period():
    """
    Окончание периода
    """
    year = current_year()
    return datetime.date(year+1, 5, 31)



class Period(HistoryModel):
    start = models.DateField(u'Дата начала', default=start_period())
    end = models.DateField(u'Дата окончания', default=end_period())

    def __unicode__(self):
        return unicode(self.start) + u" - " + unicode(self.end)
    
    class Meta:
        verbose_name = u'Период'
        verbose_name_plural = u'Периоды'
        ordering = ['start']
        db_table = "period"
        
    def save(self, *args, **kwargs):
        #with reversion.create_revision():
        super(Period, self).save( *args, **kwargs)



class Resource(HistoryModel):
    """
    Ресурсы поставляемые поставщиком.
    Вода, Топливо, Свет
    """
    RESOURCE_NAME_CHOICES = ((settings.RESOURCE_TYPE_WATER, settings.RESOURCE_TYPE_WATER),
                             (settings.RESOURCE_TYPE_ELECTRICITY, settings.RESOURCE_TYPE_ELECTRICITY),
                             (settings.RESOURCE_TYPE_FUEL, settings.RESOURCE_TYPE_FUEL))
    
    name = models.CharField(u"Наименование", max_length=50, blank=False,choices=RESOURCE_NAME_CHOICES )
    
    class Meta:
        verbose_name = u'Ресурс'
        verbose_name_plural = u'Ресурсы'
        ordering = ['name']
        db_table = "resource"
    
    def __unicode__(self):
        return unicode(self.name)
        
    def save(self, *args, **kwargs):
        #with reversion.create_revision():
        super(Resource, self).save( *args, **kwargs)



class Provider(HistoryModel):
    """
    Поставщик услуг для объекта компании
    """
    resource = models.ManyToManyField(Resource, verbose_name = u"Ресурсы", null=True)
    name = models.CharField(u"Наименование", max_length=300, blank=False)
    
    class Meta:
        verbose_name = u'Поставщик'
        verbose_name_plural = u'Поставщики услуг'
        ordering = ['name']
        db_table = "provider"
    
    def __unicode__(self):
        return unicode(self.name)
        
    def save(self, *args, **kwargs):
        #with reversion.create_revision():
        super(Provider, self).save( *args, **kwargs)



class CompanyObjectType(HistoryModel):
    """
    Тип объектов компании:
        - Филиал
        - Тепловой район
        - Котельная
        - ЦТП
    """
    TYPE_NAME_CHOICES = ((u"Филиал", u"Филиал"),(u"Тепловой район", u"Тепловой район"), (u"Котельная", u"Котельная"), (u"ЦТП",u"ЦТП"), (u"АКБ",u"АКБ"))
    name = models.CharField( max_length=50, blank=False, choices=TYPE_NAME_CHOICES)
    
    def __unicode__(self):
        return unicode(self.start) + u" - " + unicode(self.end)
    
    class Meta:
        verbose_name = u'Тип объекта'
        verbose_name_plural = u'Типы объектов'
        ordering = ['name']
        db_table = "company_object_type"
        
    def save(self, *args, **kwargs):
        #with reversion.create_revision():
        super(CompanyObjectType, self).save( *args, **kwargs)



class CompanyObject(HistoryModel):
    """
    Объект компании
    """
    name = models.CharField( max_length=300, blank=False)
    address = models.CharField(u"Адрес котельной", max_length=300, blank=True)
    order_index = models.PositiveIntegerField(verbose_name=u'Индекс в списке', default=0)
    type = models.ForeignKey(CompanyObjectType, verbose_name=u'Тип объекта', null=True)
    parent = models.ForeignKey('CompanyObject', verbose_name=u'Ссылка на родительский объект', null=True)
    
    def __unicode__(self):
        return unicode(self.name)
    
    class Meta:
        verbose_name = u'Объект'
        verbose_name_plural = u'Объекты'
        ordering = ['name']
        db_table = "company_object"
        
    def save(self, *args, **kwargs):
        #with reversion.create_revision():
        super(CompanyObject, self).save( *args, **kwargs)

class Branch(HistoryModel):
    """
    Филиал. Содержит тепловые районы, в тепловых районах находятся котельные.
    """
    name = models.CharField( max_length=300, blank=False)
    #enabled = models.BooleanField(u'Действующий', default=True)
    #subnet = models.PositiveSmallIntegerField(u'Подсеть', default=0)

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = u'Филиал'
        verbose_name_plural = u'Филиалы'
        ordering = ['name']
        db_table = "branch"
    
    def save(self, *args, **kwargs):
       super(Branch, self).save( *args, **kwargs)


# ========== ТЕПЛОВОЙ РАЙОН ==============
class ThermalArea(HistoryModel):
    """
    Тепловой район. Содержит в себе котельные.
    """
    name = models.CharField(max_length=300, blank=False)
    branch = models.ForeignKey( Branch, verbose_name=u'Филиал', blank=False)
    order_index = models.PositiveIntegerField(verbose_name=u'Индекс в списке', default=0)
    
    #enabled = models.BooleanField(u'Действующий', default=True)
    #subnet = models.PositiveSmallIntegerField(u'Подсеть', default=0)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        verbose_name = u'Тепловой район'
        ordering = ['name', 'order_index']
        db_table = "thermal"
    

    
class BoilerHouse(HistoryModel):
    """
    Объект котельной
    """
    TYPE_NAME_CHOICES = ((u"Котельная", u"Котельная"), (u"ЦТП",u"ЦТП"), (u"АКБ",u"АКБ"))
    
    branch = models.ForeignKey(Branch, verbose_name=u"Филиал", blank=False)
    thermalArea = models.ForeignKey(ThermalArea, verbose_name=u"Тепловой район", blank=False)
    
    address = models.CharField(u"Адрес котельной", max_length=300, blank=True)
    name = models.CharField(u"Наименование", max_length=300, blank=False)
    # Недействующие котельные не отображаются в отчетах, в тепловых районах
    # и для них не создаются данные по расходам
    enabled = models.BooleanField(u'Действующая', default=True)
    order_index = models.PositiveIntegerField(verbose_name=u'Индекс в списке', default=0)

    periods = models.ManyToManyField(Period, verbose_name=u"Периоды",null=True,blank=True)
    #providers = models.ManyToManyField(Provider, verbose_name=u"Поставщики", null=True, blank=True)
    
    #type = models.CharField(max_length=50, blank=False, choices=TYPE_NAME_CHOICES, default=u"Котельная")
    #parent = models.ForeignKey('BoilerHouse', verbose_name=u"Котельная", null=True, blank=True)
    
    #start_date = models.DateField(u'Дата начала', auto_now_add=True) #default = '2011-10-15')
    #end_date = models.DateField(u'Дата окончания', auto_now_add=True) #, default = '2011-10-15')
    
    report_deviation = models.BooleanField(u'Сообщать об отклонениях', default=True) 
    
    def __unicode__(self):
        #return u'Филиал: ' + self.branch.name + u', тепловой р-н: ' + self.thermalArea.name +  '( ' +self.name +' )'
        _name = u"%(branch)s | %(thermal)s | %(name)s" % dict(branch=unicode(self.branch.name),thermal=unicode(self.thermalArea.name),name=unicode(self.name))
        return _name

    class Meta:
        verbose_name = u'Котельная'
        verbose_name_plural = u'Котельные'
        ordering = ["branch__name", "thermalArea__name", 'name', 'order_index']
        db_table = "boiler"    
    
    def save(self, *args, **kwargs):
        if (self.type==u"ЦТП" and self.parent==None) or (self.type!=u"ЦТП" and self.parent!=None):
             raise ValidationError(u"Только ЦТП должно быть привязано к котельной.")
                
        #with reversion.create_revision():
        super(BoilerHouse, self).save( *args, **kwargs)


class BoilerBookmark(HistoryModel):
    """
    Закладка для котельной
    """
    name = models.CharField(u"Наименование", max_length=300, blank=False)
    boiler = models.ManyToManyField(BoilerHouse, null=True, blank=True)
    
    def __unicode__(self):
        return unicode(self.name)
    
    class Meta:
        verbose_name = u'Закладка'
        ordering = ['name']
        db_table = "bookmark"

# Добавляем в админку
class PeriodAdmin(admin.ModelAdmin):
    pass
class ResourceAdmin(admin.ModelAdmin):
    pass
class BranchAdmin(admin.ModelAdmin):
    pass
class ThermalAreaAdmin(admin.ModelAdmin):
    pass
class BoilerHouseAdmin(admin.ModelAdmin):
    pass
class BoilerBookmarkAdmin(admin.ModelAdmin):
    pass
class CompanyObjectTypeAdmin(admin.ModelAdmin):
    pass
class ProviderAdmin(admin.ModelAdmin):
    pass
class CompanyObjectAdmin(admin.ModelAdmin):
    pass


admin.site.register(Provider, ProviderAdmin)
admin.site.register(CompanyObjectType, CompanyObjectTypeAdmin)
admin.site.register(CompanyObject, CompanyObjectAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(ThermalArea, ThermalAreaAdmin)
admin.site.register(BoilerHouse, BoilerHouseAdmin)
admin.site.register(BoilerBookmark, BoilerBookmarkAdmin)



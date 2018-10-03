# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from dailyreport.company_object.models import Branch, ThermalArea, BoilerHouse
from permissions.models import Role

class Position(models.Model):
    """    
    Должности сотрудников.
    """
    name = models.CharField(u'Название должности', max_length=100)
    
    class Meta:
         verbose_name = u'Должность'
         verbose_name_plural = u'Должности'
         ordering = ['name']
         db_table = "positions"
    
    def __unicode__(self):
        return unicode(self.name)

class UserProfile(models.Model):
    """
    Профиль пользователя приложения
    В нем хранится версия клиентского приложения пользователя, которое  
    использовалось в последний раз.
    
    Будет добавлена информация об активности пользователя (дата последней
    активности, действия, характеристика активности)
    
    """
    
    user = models.ForeignKey(User, verbose_name=u"Пользователь")
    #position = models.ForeignKey(Position, verbose_name=u"Должность", null=True)
    #boilers = models.ManyToManyField(BoilerHouse,
    #                                verbose_name='Котельные', blank=True, null=True)
    branch = models.ForeignKey(Branch, verbose_name='Филиал пользователя', blank=True, null=True)
    #thermals = models.ManyToManyField(ThermalArea,
    #                                verbose_name='Тепловые районы', blank=True, null=True)
    
    misc_info = models.TextField(u'Дополнительная информация',default="", blank=True)
    client_version = models.CharField(u'Версия клиента', max_length=10, default='0.0.0')

    #last_active = models.DateTimeField(null=True, blank=True)
    #last_action = models.CharField(max_length=250, default='') 
    #def _activity(self):
    #   '''returns a value between 0 and 100
    #   indicating the useractivity'''
    #   today = datetime.date.today()
    #   if self.last_active is None:
    #       return 0
    #   if self.last_active >= today:
    #       #just in case
    #       return 100
    #   else:
    #       diff = today - self.last_active
    #       if diff.days < 87:
    #           activity_ = int(((diff.days/87.)-1.585)**10)
    #       else:
    #           activity_ = 0
    #       return activity_

    #activity = property(_activity)
    
    class Meta:
         verbose_name = u'Профиль пользователя'
         verbose_name_plural = u'Профили пользователей'
         ordering = ['user__username']
         db_table = "user_profile"
         
    def __unicode__(self):
        return unicode(self.user)


class PositionAdmin(admin.ModelAdmin):
    pass
# Enable django admin access
class UserProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Position, PositionAdmin)
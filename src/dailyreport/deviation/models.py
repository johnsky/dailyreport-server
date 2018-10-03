# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

from dailyreport.water.models import WaterConsumption
from dailyreport.fuel.models import FuelConsumption
from dailyreport.electricity.models import ElectricityConsumption
from dailyreport.company_object.models import Branch, ThermalArea, BoilerHouse,\
    Resource
from dailyreport.utils.date_utils import get_today

class ParameterDeviationProblemState(models.Model):
    """
    Состояние проблемы.
    """
    name = models.CharField(u'Название', max_length=50)
    
    class Meta:
        verbose_name = u'Состояние проблемы'
        verbose_name_plural = u'Состояния проблемы'
        ordering = ['name']
        db_table = "deviation_state"
        
    def __unicode__(self):
        return unicode(self.name)

class ParameterDeviationProblemCause(models.Model):
    """
    Причина отклонения параметра
    """
    name = models.CharField(u'Название', max_length=70)
    description = models.CharField(u'Описание', max_length=200)
    
    class Meta:
        verbose_name = u'Причина проблемы'
        verbose_name_plural = u'Причины проблем'
        ordering = ['name']
        db_table = "deviation_cause"
    
    def __unicode__(self):
        return unicode(self.name)
    
class ParameterDeviationProblemComment(models.Model):
    """
    Комментарий по проблеме
    """
    author = models.ForeignKey(User,
                               verbose_name = u'Автор комментария')  
    
    date = models.DateTimeField(u'Время добавления', auto_now = True)
    
    text = models.TextField(u'Текст')
    
    deviation = models.ForeignKey('ParameterDeviationProblem',
                                  verbose_name = u'Проблема, по которой комментарий',
                                  related_name = 'comments')
    
    class Meta:
        verbose_name = u'Комментарий по проблеме'
        verbose_name_plural = u'Комментарии по проблемам'
        ordering = ['deviation__start_date','date','author__username']
        db_table = "deviation_comment"

    def __unicode__(self):
        return "%(author)s,  %(date)s" % {'author':unicode(self.author.username), 'date':unicode(self.date)}
    
class ParameterDeviationProblem(models.Model):
    """
    Проблема связанная с отклонением фактического значения параметра
    от планового.    
    """
    boiler = models.ForeignKey(BoilerHouse,
                               verbose_name=u"Котельная")
    
    resource = models.ForeignKey(Resource,
                               verbose_name=u"Ресурс")
    
    state = models.ForeignKey(ParameterDeviationProblemState,
                              verbose_name = u'Состояние проблемы')
    
    cause = models.ForeignKey(ParameterDeviationProblemCause,
                              verbose_name = u'Причина аварии', null=True, blank = True)
    
    created = models.DateTimeField(auto_now_add = True)
    
    start_date = models.DateField(u'Дата возникновения')
    
    close_date = models.DateField(u'Дата закрытия', null=True, blank = True)

    responsible = models.ManyToManyField(User,
                                         verbose_name = u'Ответственные лица',
                                         related_name = 'responsible',
                                         db_table='responsible_to_deviation')
    concerned = models.ManyToManyField(User,
                                       verbose_name = u'Заинтересованные лица',
                                       related_name = 'concerned',
                                       db_table='concerned_with_deviation')
    
    water = models.ForeignKey(WaterConsumption,
                                          verbose_name = u'Суточный расход воды',
                                          null=True, blank = True)
    fuel = models.ForeignKey(FuelConsumption,
                                         verbose_name= u'Суточный расход топлива',
                                         null=True, blank = True)
    electricity = models.ForeignKey(ElectricityConsumption,
                                         verbose_name= u'Суточный расход электричества',
                                         null=True, blank = True)
    
    class Meta:
        verbose_name = u'Проблемаs'
        verbose_name_plural = u'Проблемы'
        ordering = ["boiler__branch__name",
                    "boiler__thermalArea__name",
                    "boiler__name",
                    "start_date",
                    "resource__name",
                    "state__name"]
        db_table = "deviation"
        
    def __unicode__(self):
        return "%(companyObject)s - %(resource)s (%(start_date)s)" % {'start_date':unicode(self.start_date),
                                                              'companyObject' : unicode(self.boiler),
                                                              'resource' : unicode(self.resource)}
    
    
    def get_consumption(self):
        """
        Наименование ресурса по которому произошло отклонение
        """
        if self.water:
            return self.water 
        elif self.fuel:
            print self.fuel
            return self.fuel
        elif self.electricity:
            return self.electricity
        else:
            raise Exception(u"Ресурс по которому произошло отклонение не укзан.")
        
        return None
    
    def set_consumption(self, obj):
        """
        """
        if isinstance(obj, WaterConsumption):
            self.water = obj
        # 
        elif isinstance(obj, FuelConsumption): 
            self.fuel = obj
        # 
        elif isinstance(obj, ElectricityConsumption):
            self.electricity = obj
        # 
        else:
            raise Exception(u"Тип объекта не поддерживается.")


class DeviationResponcible(models.Model):
    """
    
    """
    branch = models.ForeignKey(Branch,
                                 verbose_name= u'Филиал',
                                 null=True)
    thermal = models.ForeignKey(ThermalArea,
                                 verbose_name= u'Тепловой район',
                                 null=True,
                                 blank=True)
    responcible = models.ForeignKey(User,
                                 verbose_name= u'Ответственное лицо')
    
    class Meta:
        verbose_name = u'Ответственное лицо'
        verbose_name_plural = u'Ответственные лица'
        ordering = ['branch__name', 'responcible__username']
        db_table = "deviation_responcible"

    def __unicode__(self):
        return "%(branch)s, %(responcible)s" % {'responcible': unicode(self.responcible.username),
                                                 'branch': unicode(self.branch.name)}
        
class DeviationConcerned(models.Model):
    
    concerned = models.ForeignKey(User,
                                 verbose_name= u'Заинтересованный')
    class Meta:
        verbose_name = u'Заинтересованное лицо'
        verbose_name_plural = u'Заинтересованные лица'
        ordering = ['concerned__username']
        db_table = "deviation_concerned"

    def __unicode__(self):
        return "%(concerned)s" % {'concerned': unicode(self.concerned.username)}

        
class DeviationConcernedAdmin(admin.ModelAdmin):
    pass
class DeviationResponcibleAdmin(admin.ModelAdmin):
    pass
class ParameterDeviationProblemAdmin(admin.ModelAdmin):
    pass
class ParameterDeviationProblemCommentAdmin(admin.ModelAdmin):
    pass
class ParameterDeviationProblemCauseAdmin(admin.ModelAdmin):
    pass
class ParameterDeviationProblemStateAdmin(admin.ModelAdmin):
    pass

admin.site.register(DeviationConcerned, DeviationConcernedAdmin)
admin.site.register(DeviationResponcible, DeviationResponcibleAdmin)
admin.site.register(ParameterDeviationProblem, ParameterDeviationProblemAdmin)
admin.site.register(ParameterDeviationProblemComment,ParameterDeviationProblemCommentAdmin)
admin.site.register(ParameterDeviationProblemCause,ParameterDeviationProblemCauseAdmin)
admin.site.register(ParameterDeviationProblemState, ParameterDeviationProblemStateAdmin)

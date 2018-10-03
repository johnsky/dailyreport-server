# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.db.models.base import Model
from django.db.models import Q

import reversion
import logging

from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group

from dailyreport.company_object.models import BoilerHouse
from dailyreport.core.models import HistoryModel
 
from permissions.utils import has_permission, grant_permission
from permissions.models import Role
from django.db.models.fields import BooleanField, FloatField,CharField

import traceback
import sys

def get_entity(actor, on_date, model_class, boiler_obj, water_category_obj, fuel_info_obj):
    """
    Создать или получить объект, контролируя чтобы присутствовал только один объект в базе. 
    Реализованный механизм дает сбои, когда оба объекта создаются одновременно. 
    
        @param actor: тот, кто выполняет действие 
        @param boiler_obj: идентификатор котельной
        @param on_date: на дату (объект даты)
        @param model: класс модели (класс наследник DailyReportingBase)
        
        @return: возвращает объект созданной модели
    """ 
    _entity = None
    #logging.getLogger(__name__).debug(u"Получить сущность " + unicode(model_class) 
    #                                  + u"; На дату: " + unicode(on_date) 
    #                                  + u"; Котельная: " + unicode(boiler_obj.id) 
    #                                  + u"; Расход воды :" + unicode(fuel_info_obj) 
    #                                  + u"; Категория воды: " + unicode(water_category_obj))
    
    #try:
    try:
        #logging.getLogger(__name__).debug(u"Получить сущность " + unicode(model_class) + u"; На дату: " + unicode(on_date) + u"; Котельная: " + unicode(boiler_obj.id) +
        #                                  u"; Расход воды :" + unicode(fuel_info_obj) + u"; Категория воды: " + unicode(water_category_obj))
        # Топливо
        if model_class.__name__ in ['FuelIncome','FuelRemains','FuelConsumption']:
            if fuel_info_obj == None:
                return None

            _entity = model_class.objects.get(fuel_info=fuel_info_obj, date=on_date)
        # Вода
        elif model_class.__name__ == 'WaterConsumption':
            if water_category_obj == None:
                return None
            
            _entity = model_class.objects.get(category=water_category_obj, date=on_date)
        else:
            _entity = model_class.objects.get(boiler=boiler_obj, date=on_date)

    # если запись не существует
    except model_class.DoesNotExist as dex:
        logging.getLogger(__name__).debug(dex)
        #print dex
        # Топливо
        if model_class.__name__ in ['FuelIncome','FuelRemains','FuelConsumption']:
            # Если нет информации о топливе возвращаем None
            if fuel_info_obj == None:
                logging.getLogger(__name__).debug("Cannot create new instance of " + model_class.__name__ + ", fuel info is None.")
                return None
            
            logging.getLogger(__name__).debug("Create new instance of " + model_class.__name__)
            _entity = model_class()
            _entity.boiler = fuel_info_obj.boiler
            _entity.creator = actor
            _entity.date = on_date
            _entity.fuel_info = fuel_info_obj

        # Вода
        elif model_class.__name__ == 'WaterConsumption':
            # Если не указана информация о воде - None
            if water_category_obj == None:
                logging.getLogger(__name__).debug("Cannot create new instance of " + model_class.__name__ + ", water consumption category is None.")
                return None
            
            logging.getLogger(__name__).debug("Create new instance of " + model_class.__name__)
            _entity = model_class()
            _entity.boiler = water_category_obj.boiler
            _entity.creator = actor
            _entity.date = on_date
            _entity.category = water_category_obj

        else:
            #print model_class
            logging.getLogger(__name__).debug("Create new instance of " + model_class.__name__)
            _entity = model_class()
            _entity.boiler = boiler_obj 
            _entity.creator = actor
            _entity.date = on_date
            
        _entity.save(force_insert=True)
        
    # если существует несоколько записей
    except model_class.MultipleObjectsReturned as mex:
        logging.getLogger(__name__).debug(mex)
        #print mex
        
        is_first = True
        items = []

        # Расход топлива
        if model_class.__name__ in ['FuelIncome','FuelRemains','FuelConsumption']:
            items = model_class.objects.filter(fuel_info=fuel_info_obj, date=on_date)
        # Расход воды
        elif model_class.__name__ == 'WaterConsumption':
            items = model_class.objects.filter(category=water_category_obj, date=on_date)
        # Другой расход
        else:
            items = model_class.objects.filter(boiler=boiler_obj, date=on_date)

        for item in items:
            if is_first==True:
                _entity = item
                is_first=False
            else:
                item.delete()
    #except Exception as ex:
    #    print ex    
    
    return _entity

class DatasetField(HistoryModel):
    """
    Поле набора данных.
    
    Права доступа(просмотр, создание, удаление, редактирование) к
    полю даются на основании разрешений.
    """
    name = models.CharField(u'Пользовательское название', max_length=300)
    description = models.CharField(u'Описание поля', max_length=300, default="")
    internal_name = models.CharField(u'Наименование поля(внутреннее)', max_length=300, default="")
    model_field_name = models.CharField(u'Поле модели', max_length=300)
    model_content_type = models.ForeignKey(ContentType)
    index = models.IntegerField(u'Индекс поля', default=0)
    validate = models.BooleanField(u'Проверяется при вводе', default = False) 
    
    def __unicode__(self):
        return u"Поле (%s): " % unicode(self.id) + self.model_content_type.name +"." + self.model_field_name
    
    def gen_internal_name(self):
        import hashlib
        m = hashlib.md5()
        m.update("%(field)s_%(model)s_%(id)s" % {'field':self.model_field_name,'model':self.model_content_type.model,'id':self.id})
        return m.hexdigest()
     
    class Meta:
        verbose_name = u"Поле набора данных"
        verbose_name_plural = u"Поля наборов данных"
        ordering = ['model_content_type__name','index']
        db_table = "dataset_field"        
        
    def save(self, save_revision=False, *args, **kwargs):
        """
        Сохранить поле набора данных.
        Если сущность не создана, для нее по умолчанию будут созданы разрешения:
            Для разработчика - ВСЕ
            Для менеджера - ВСЕ
            Для администратора - ВСЕ
        """
        i_need_permission = False
        
        if self.id == None:
            i_need_permission = True
        
        if self.internal_name:
            self.internal_name = self.gen_internal_name()
        
        #if save_revision:
        #    with reversion.create_revision():
        #        super(DatasetField,self).save(*args, **kwargs)
        #else:
        super(DatasetField,self).save(*args, **kwargs)
        
        # Если нужно создать роли - создаем их. Для новой сущности доступ имеется только 
        # для тех, кто является менеджером, разработчиком или администратором
        if i_need_permission == True:
            # Разрешения для менеджера
            grant_permission(self, 
                 Role.objects.get(name=settings.ROLE_MANAGER_NAME), settings.PERMISSION_EDIT_NAME)
            
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_MANAGER_NAME), settings.PERMISSION_VIEW_NAME)
            
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_MANAGER_NAME), settings.PERMISSION_DELETE_NAME)
            
            # Разрешения для разработчика
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_DEVELOPER_NAME), settings.PERMISSION_EDIT_NAME)
            
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_DEVELOPER_NAME), settings.PERMISSION_VIEW_NAME)
            
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_DEVELOPER_NAME), settings.PERMISSION_DELETE_NAME)
            
            # Разрешения для администратора
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_ADMIN_NAME), settings.PERMISSION_EDIT_NAME)

            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_ADMIN_NAME), settings.PERMISSION_VIEW_NAME)
            
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_ADMIN_NAME), settings.PERMISSION_DELETE_NAME)
            
    def set_value(self, actor, date, value, boiler_obj, water_category_obj, fuel_info_obj):
        """
        Редактирование значение поля. 
            @param actor: тот, кто выполняет редактирование
            @param boiler_obj: объект котельной (BoilerHouse)
            @param date: дата отчета (в строковом формате)
            @param value: Значение
        """
        if not has_permission(self, actor, settings.PERMISSION_EDIT_NAME):
            raise PermissionDenied(u"Пользователь " + unicode(actor) + u" - не имеет права на запись поля " + self.name)

        if value != None:
            
            try:
                # создаем или получаем объект данных
                model = self.model_content_type.model_class()
                entity = get_entity(actor, date, model, boiler_obj, water_category_obj, fuel_info_obj) 
                
                if entity == None:
                    return
                    
                # устанавливаем значение
                setattr(entity, self.model_field_name, value)
                entity.save(save_revision=True)
                
                if hasattr(entity, 'update_period'):
                    logging.getLogger(__name__).debug(u"Начинаем обновление периода для " + unicode(entity))
                    entity.update_period()
                    logging.getLogger(__name__).debug(u"Закончено обновление периода для " + unicode(entity))
                
                
            except Exception as ex:
                traceback.print_exc(file=sys.stdout)
        else:
            raise ValueError("Недопустимое значение (None).")

    def get_value(self, actor, on_date, boiler_obj, water_category_obj, fuel_info_obj, model_instance = None):
        """
        Получить значение поля. Поле может зависеть от вида топлива и категории затрат по воде.
        """
        # создаем или получаем объект данных
        model = self.model_content_type.model_class()
        #print ">>>>>>>>" + unicode(model) + " "+ unicode(boiler_obj.id)
        if model_instance != None:
            entity = model_instance
        else:
            entity = get_entity(actor, on_date, model, boiler_obj, water_category_obj, fuel_info_obj)
        
        # Если сущность не существует для данного поля набора данных (DatasetField),
        # тогда возвращаем пустое значение в зависимости от типа данных
        # указанного поля модели (model_content_type, model_field_name)
        if entity == None:
            model_class = self.model_content_type.model_class()
            field = self.get_field()
            
            if isinstance(field, BooleanField):
                return (False, None)

            if isinstance(field, FloatField):
                return (0.0,None)
            
            if isinstance(field, CharField):
                return ("", None)

        field_value = getattr(entity, self.model_field_name)
        
        return (field_value, entity)
    
    def get_field(self):
        """
        Получить объект поля модели (один из потомков класса Field), имя которого 
        соответствует имени указанное в model_field_name данного класса.
        
        @return: объект (потомок models.Field)         
        """
        
        fields = self.model_content_type.model_class()._meta.fields
        
        for field in fields:
            if field.name == self.model_field_name:
                return field
        
        return None
    
    def get_model_class(self):
        """
        Получить класс модели (не экземпляр)
        """
        return self.model_content_type.model_class()

    def get_field_path(self):
        """
        Получить путь для поля в формате <class model name>.<field>
        """
        path = "%(cn)s.%(fld)s" % dict(fld = self.get_field().name, cn = self.get_model_class().__name__)
        return path
    
    def get_related_datasets(self):
        return self.dataset_set.all()
    

class Dataset(HistoryModel):
    """
    Класс для отчета по расходу ресурсов. Содержит структуру полей, которую можно редактировать.
    При создании отчета автоматически создается разрешение (permission).
    
    Каждый отчет строится по дате и котельным. По умолчанию отчет включает в себя поля:
    id котельной(первый столбец), дату отчета, наименование котельной.
    """
    name = models.CharField(u'Название набора данных', max_length=300)
    description = models.CharField(u'Описание', max_length=300)
    fields = models.ManyToManyField(DatasetField)
    
    def __unicode__(self):
        return u"Набор данных (%s): " % unicode(self.id) + self.name 
    
    class Meta:
        verbose_name = u'Набор данных'
        ordering = ['name']  
        db_table = "data_proxy"

    def save(self, save_revision=False, *args, **kwargs):
        """
        Сохранить поле набора данных.
        Если сущность не создана, для нее по умолчанию будут созданы разрешения:
            Для разработчика - ВСЕ
            Для менеджера - ВСЕ
            Для администратора - ВСЕ
        
        """
        i_need_permission = False
        
        if self.id == None:
            i_need_permission = True
        
        #if save_revision:
        #    with reversion.create_revision():
        #        super(Dataset, self).save( *args, **kwargs)
        #else:
        super(Dataset, self).save( *args, **kwargs)
    
        # Если нужно создать роли - создаем их. Для новой сущности доступ имеется только 
        # для тех, кто является менеджером, разработчиком или администратором
        if i_need_permission == True:
            # Разрешения для менеджера
            grant_permission(self, 
                 Role.objects.get(name=settings.ROLE_MANAGER_NAME), settings.PERMISSION_EDIT_NAME)
            
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_MANAGER_NAME), settings.PERMISSION_VIEW_NAME)
            
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_MANAGER_NAME), settings.PERMISSION_DELETE_NAME)
            
            # Разрешения для разработчика
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_DEVELOPER_NAME), settings.PERMISSION_EDIT_NAME)
            
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_DEVELOPER_NAME), settings.PERMISSION_VIEW_NAME)
            
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_DEVELOPER_NAME), settings.PERMISSION_DELETE_NAME)
            
            # Разрешения для администратора
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_ADMIN_NAME), settings.PERMISSION_EDIT_NAME)

            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_ADMIN_NAME), settings.PERMISSION_VIEW_NAME)
            
            grant_permission(self,
                 Role.objects.get(name=settings.ROLE_ADMIN_NAME), settings.PERMISSION_DELETE_NAME)

reversion.register(Dataset)


class ValidateExpression(models.Model):
    """
    
    
    """
    pass
    


# enable django-admin access 
class DatasetFieldAdmin(admin.ModelAdmin):
    pass
class DatasetAdmin(admin.ModelAdmin):
    pass

admin.site.register(Dataset, DatasetAdmin)
admin.site.register(DatasetField, DatasetFieldAdmin)



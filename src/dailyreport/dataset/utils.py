# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from dailyreport.dataset.models import Dataset, DatasetField
from dailyreport.company_object.models import BoilerHouse, BoilerBookmark, ThermalArea, Branch
from dailyreport.company_object.utils import get_boilers
from permissions.utils import has_permission
import datetime
#from argparse import ArgumentError
from dailyreport.fuel.models import FuelConsumption, FuelInfo
from dailyreport.water.models import WaterConsumption, WaterConsumptionCategory 


def add_field(dataset, field):
    """
    Добавляет поле в набор данных
    """
    pass

def get_models_content_types():
        """
        Список объектов ContentType моделей, которые могут быть источниками
        данных.
        """
        content_types = []
        
        for content_type in list(ContentType.objects.filter(Q(app_label='consumption') |
                                                            Q(app_label='water') |
                                                            Q(app_label='fuel') |
                                                            Q(app_label='electricity')).order_by('name')):
            if hasattr(content_type.model_class(), 'DescriptorMeta')==True and content_type.model_class().DescriptorMeta.source == True:
                content_types.append(content_type)
        
        return content_types

def get_model_fields(content_type):
    """
    Список полей модели, которые можно использовать в наборах данных.

    @param content_type: контент тайп модели 
    """
    
    available_fields =[]
    
    if content_type.app_label not in ('consumption','water','fuel','electricity'):
        return available_fields
    
    model = content_type.model_class()
    model_instance = model()         
    
    for field in model_instance._meta.fields:
        if field.name in model.DescriptorMeta.fields:
            available_fields.append(field)
    
    return available_fields

def get_dataset_fields(dataset, actor):
    """
    Получить список полей набора данных
    """
    fields = []
    for field in dataset.fields.all().order_by('index'):
        if has_permission(field, actor, settings.PERMISSION_EDIT_NAME) or has_permission(field, actor, settings.PERMISSION_VIEW_NAME):
            fields.append(field)
             
    return fields

def get_datasets(actor, permission_name=settings.PERMISSION_VIEW_NAME):
    """
    Получить список наборов данных, которые пользователь
    может хотя бы просматривать.
    Используется для получения информации об отчете и полях содержащихся в нем.

        @param actor: объекта типа User, тот кто пытается получить доступ к объекту
        @return: объекты Dataset
    """
    datasets = []    
    if actor==None:
        return datasets

    for dataset in Dataset.objects.all():
        if has_permission(dataset, actor, settings.PERMISSION_VIEW_NAME):
            datasets.append(dataset)

    return datasets

def has_water_category(dataset, actor):
    """
    Нужно отображать категорию расхода воды?
    """
    for field in get_dataset_fields(dataset, actor):
        clazz = field.get_model_class()
        # Есть ли поле, которое зависит от категории расхода воды
        if clazz == WaterConsumption or clazz == WaterConsumptionCategory: 
            return True
    return False

def has_fuel_info(dataset, actor):
    """
    Нужно ли отображать информацию о топливе?
    """
    for field in get_dataset_fields(dataset, actor):
        clazz = field.get_model_class()
        # Есть ли поле, которое зависит от информации о топливе
        if clazz == FuelConsumption or clazz == FuelInfo:
            return True        
    return False

def get_dataset_rows_number(dataset, actor, date_range, boilers=[], fuel_infos=[], water_categories=[]):
    """
    Получить количество рядов в запросе.
    
    Количество рядов строится исходя из того: сколько котельных, какую информацию по ним показывать.
    
    @param boilers: котельные (тип BoilerHouse)
    @param actor: пользователь (User)
    
    """

    if has_permission(dataset, actor, settings.PERMISSION_VIEW_NAME)== False and \
        has_permission(dataset, actor, settings.PERMISSION_EDIT_NAME)== False:
        return 0

    rows_number = 0    
    date_begin = date_range[0]
    date_end = date_range[1]
    
    # разница в днях
    delta = date_end - date_begin
    
    if delta.days < 0 or delta.days > 31:
        #raise ArgumentError(u"Неверный диапазон дат: дата окончания меньше даты начала или диапазон больше 31 дня.")
        return 0
    
    if len(boilers) < 1:
        #raise ArgumentError(u"Нет ни одной котельной, для которой нужно сформировать данные.")
        return 0
    
    has_fuel = has_fuel_info(dataset, actor)
    has_water = has_water_category(dataset, actor)  
    
    delta = delta.days
    while delta >= 0:
        for boiler in boilers:
            if has_fuel == False and has_water == False:
                rows_number = rows_number + 1
            else:
                if has_fuel:
                    c = FuelInfo.objects.filter(boiler = boiler, active = True).count()
                    rows_number = rows_number + c
                     
                if has_water:
                    c = WaterConsumptionCategory.objects.filter(boiler = boiler, active = True).count()
                    rows_number = rows_number + c

        delta = delta - 1

    return rows_number

def get_row_data(dataset, actor, on_date, boiler, has_fuel, has_water):
    """
    Данные для одной котельной.
    
    @param dataset: Набор данных (Dataset)
    @param actor: Тот кто получает запрашивает данные (User)
    @param date: дата
    @param boiler: котельная (BoilerHouse)
    @param has_fuel: содержит данные о топливе
    @param has_water: содержит данные о воде
    """
    if boiler == None or actor == None or dataset == None or on_date == None:
        return []
    
    rows_data = []
    
    water_categories = []
    fuel_infos = []
    
    if has_water:
        # Актуальные виды расходов по воде
        water_categories = list(WaterConsumptionCategory.objects.filter(boiler = boiler,
                                active = True).order_by('name'))
    if has_fuel:
        # Актуальные виды расхода топлива
        fuel_infos = list(FuelInfo.objects.filter(boiler = boiler,
                                active = True).order_by('type'))
    
    # Текщая строка
    line = 0
    # Всего количество строк
    lines = max(len(fuel_infos), len(water_categories)) 
    if lines == 0:
        lines = 1
    
    water_category = None
    fuel_info = None

       
    # Заполняем строки данными
    while line < lines:
        cache = {}
        row_data = [boiler.id, on_date, boiler.name] 

        # Если есть параметры по воде, получаем категорию
        if has_water:
            try:
                water_category =  water_categories.pop()
            except IndexError:
                pass
            
            if water_category != None:
                row_data.extend([water_category.id, water_category.name])
            else:
                row_data.extend([0, ""])
            
        # Если есть параметры по топливу, получаем информацию о топливе 
        if has_fuel:
            try:
                fuel_info = fuel_infos.pop()
            except IndexError:
                pass
            
            if fuel_info != None:
                row_data.extend([fuel_info.id, fuel_info.type])
            else:
                row_data.extend([0, ""])
            
        # dataset_field - объект класса DatasetField
        # Заполняем значения полей 
        for dataset_field in get_dataset_fields(dataset, actor):
            field_value = None

            if cache.has_key(dataset_field.model_content_type) and cache.get(dataset_field.model_content_type) != None:
                field_value, entity = dataset_field.get_value(actor, on_date, boiler, water_category, fuel_info, cache.get(dataset_field.model_content_type))
            else:
                field_value, entity = dataset_field.get_value(actor, on_date, boiler, water_category, fuel_info)
                cache[dataset_field.model_content_type] = entity
            
            row_data.append(field_value)
        
        rows_data.append(row_data)
        line = line + 1
    
    return rows_data

def get_data(dataset, actor, date_range, boilers):
    """
    Получить данные по отчету на указанный диапазон дат, для котельных.
    
    Если в наборе данных присутствует поле из расхода топлива, нужно добавить
    поля с информацией о топливе (FID, Вид топлива).
    
    Если в наборе данных присутствует поле из расхода топлива, нужно добавить
    поле с информацией о воде (WID, Категория расхода воды).
    
        Параметры:
            @param actor: тот кто получает доступ к отчету, просматривает его и пр.
            @param date_range: диапазон дат начала и окончания
            @param boilers: котельные по которым заполняется отчет(объекты BoilerHouse)

            @return: массив данных для набора данных
    """
    
    if has_permission(dataset, actor, settings.PERMISSION_VIEW_NAME)== False and \
        has_permission(dataset, actor, settings.PERMISSION_EDIT_NAME)== False:
        return []
    
    date_begin = date_range[0]
    date_end = date_range[1]
    
    dataset_data = []

    # разница в днях
    delta = date_end - date_begin
  
    if delta.days < 0 or delta.days > 31:
        #raise ArgumentError(u"Неверный диапазон дат: дата окончания меньше даты начала или диапазон больше 31 дня.")
        return []

    if len(boilers) < 1:
        #raise ArgumentError(u"Нет ни одной котельной, для которой нужно сформировать данные.")
        return []

    delta = delta.days
    day_shift = 0
    
    has_fuel_inf = has_fuel_info(dataset, actor)
    has_water_cat = has_water_category(dataset, actor)
    
    # по всем датам
    while day_shift <= delta:
        on_date = date_begin + datetime.timedelta(days=day_shift)

        # для всех котельных
        for boiler_obj in boilers:
            # данные для одной котельной - 2х мерный массив
            row_data = get_row_data(dataset, actor, on_date, boiler_obj, has_fuel_inf, has_water_cat)
            
            dataset_data.extend(row_data)
        day_shift = day_shift + 1
        
    return dataset_data

def get_fields(dataset, actor):
    """
    Получить заголовок отчета для указанного пользователя.
    Метаданные содержат структуру для каждого поля показанного в отчёте пользователю.
        [{'name'  : ' <Наименование заголовка столбца>',
           'id'             : <Идентификатор модели DatasetField>,
           'renderer'       : '<Вид обработчика для представления содержимого>',
           'editor'         : '<Редактор содержимого, который также выполняет валидацию данных>',
           'editable'       : <Редактируем элемент или нет>,
           'visible'        : <Видимый или не видимый элемент>},...]
        
        
        @param dataset: набор данных (Dataset)
        @param actor: тот кто запрашивает заголовок (User)
        
        @return: словарь с ключами 'names' и 'meta'
    """
    
    if has_permission(dataset, actor, settings.PERMISSION_VIEW_NAME)== False and \
        has_permission(dataset, actor, settings.PERMISSION_EDIT_NAME)== False:
        return []
    
    meta = []

    # field  - object of DatasetField
    fields = get_dataset_fields(dataset, actor)
    
    if len(fields) < 1:
        return []

    meta.extend(
              # Идентификатор котельной
              [
               {'name'          : 'ID',
               'id'             : 'ID',
               'renderer'       : 'string',
               'editor'         : 'textbox',
               'editable'       : False,
               'visible'        : False,
               'validate'       : False,
               'resource'       : ""},
               
               # Дата 
               {'name'          : u'Дата',
               'id'             : 'Date',
               'renderer'       : 'string',
               'editor'         : 'textbox',
               'editable'       : False,
               'visible'        : True,
               'validate'       : False,
               'resource'       : ""},
               
               # Наименование котельной
               {'name'          : u'Котельная',
               'id'             : 'Boiler',
               'renderer'       : 'string',
               'editor'         : 'textbox',
               'editable'       : False,
               'visible'        : True,
               'validate'       : False,
               'resource'       : ""}])
    
    # Присутствует поле определяющее расход по воде
    if has_water_category(dataset, actor):
        meta.extend([
                 # Идентификатор расхода воды
                 {'name'            : u'WID',
                   'id'             : 'WID',
                   'renderer'       : 'string',
                   'editor'         : 'textbox',
                   'editable'       : False,
                   'visible'        : False,
                   'validate'       : False,
                   'resource'       : ""},
                 # Наименовение 
                 {'name'           : u'Категория расхода воды',
                  'id'             : 'WCID',
                  'renderer'       : 'string',
                  'editor'         : 'textbox',
                  'editable'       : False,
                  'visible'        : True,
                  'validate'       : False,
                  'resource'       : ""}])
        
    # Присутствует поле определяющее расход по топливу
    if has_fuel_info(dataset, actor):
        meta.extend([
                 # Идентификатор расхода воды
                 {'name'            : u'FID',
                   'id'             : 'FID',
                   'renderer'       : 'string',
                   'editor'         : 'textbox',
                   'editable'       : False,
                   'visible'        : False,
                   'validate'       : False,
                   'resource'       : ""},
                 
                 # Вид топлива 
                 {'name'           : u'Вид топлива',
                  'id'             : 'FTID',
                  'renderer'       : 'string',
                  'editor'         : 'textbox',
                  'editable'       : False,
                  'visible'        : True,
                  'validate'       : False,
                  'resource'       : ""}             
                 ])
    
    for field in fields:
        # проверяем разрешение пользователя
        can_edit = has_permission(field, actor, settings.PERMISSION_EDIT_NAME)
        can_view = has_permission(field, actor, settings.PERMISSION_VIEW_NAME)
        
        if can_view or can_edit:
            from django.db.models import BooleanField, CharField, FloatField, ForeignKey
            
            #объект поля модели, потомок класса Field
            
            field_field = field.get_field()
            resource_name = ""
            if field.get_model_class().__name__ in ['FuelIncome','FuelRemains','FuelConsumption']:
                resource_name = settings.RESOURCE_TYPE_FUEL
            
            elif field.get_model_class().__name__ == 'WaterConsumption':
                resource_name = settings.RESOURCE_TYPE_WATER
            
            elif field.get_model_class().__name__ == 'ElectricityConsumption':
                resource_name = settings.RESOURCE_TYPE_ELECTRICITY
            
            field_name = ""
            if field.name == "":
                field_name = field_field.verbose_name
            else:
                field_name = field.name

            field_id = field.id
            need_validation = field.validate
            
            if isinstance(field_field, BooleanField):
                meta.append({'name'             : field_name,
                               'id'             : field_id,
                               'renderer'       : 'boolean',
                               'editor'         : 'checkbox',
                               'editable'       : can_edit,
                               'visible'        : can_view,
                               'validate'       : need_validation,
                               'resource'       : resource_name})
            elif isinstance(field_field, CharField):
                # renderer   - string
                # editor     - textbox
                meta.append({'name'             : field_name,
                               'id'             : field_id,
                               'renderer'       : 'string',
                               'editor'         : 'textbox',
                               'editable'       : can_edit,
                               'visible'        : can_view,
                               'validate'       : need_validation,
                               'resource'       : resource_name})
            elif isinstance(field_field, FloatField):
                # renderer   - number
                # editor     - textbox
                meta.append({'name'             : field_name,
                               'id'             : field_id,
                               'renderer'       : 'number',
                               'editor'         : 'textbox',
                               'editable'       : can_edit,
                               'visible'        : can_view,
                               'validate'       : need_validation,
                               'resource'       : resource_name})
            elif isinstance(field_field, ForeignKey):
                # renderer   - string
                # editor     - textbox
                meta.append({'name'             : field_name,
                               'id'             : field_id,
                               'renderer'       : 'string',
                               'editor'         : 'textbox',
                               'editable'       : can_edit,
                               'visible'        : can_view,
                               'validate'       : need_validation,
                               'resource'       : resource_name})
            else:
                # renderer   - string
                # editor     - textbox
                meta.append({'name'             : field_name,
                               'id'             : field_id,
                               'renderer'       : 'string',
                               'editor'         : 'textbox',
                               'editable'       : can_edit,
                               'visible'        : can_view,
                               'validate'       : need_validation,
                               'resource'       : resource_name})

    return meta
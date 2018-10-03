# -*- coding: utf-8 -*-

from jsonrpc import jsonrpc_method
from models import Dataset, DatasetField
from django.core import serializers
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from permissions.models import Role, ObjectPermission, Permission
from permissions.utils import has_permission, has_role, has_local_role, get_role,\
    get_roles

from dailyreport.dataset.utils import get_datasets, get_fields, get_data, get_boilers, get_dataset_fields
from dailyreport.utils.date_utils import get_today, get_month_day, get_month_last_day

from dailyreport.company_object.models import BoilerHouse
from dailyreport.fuel.models import FuelInfo
from dailyreport.water.models import WaterConsumptionCategory

from datetime import datetime
import traceback
import sys
import logging
from dailyreport.utils import qooxdoo_utils

_logger = logging.getLogger(__name__)

@jsonrpc_method('dataset.getDatasets', authenticated=True, safe=False)
def get_user_datasets(request):
    """
    Получить список наборов данных доступных для данного пользователя
    """
    user_datasets = get_datasets(request.user, settings.PERMISSION_VIEW_NAME)
    return serializers.serialize("json", user_datasets)

@jsonrpc_method('dataset.getFields', authenticated=True, safe=False)
def get_dataset_fields_meta(request, dataset_id):
    """
    Получить метаданные колонок для набора данных. 
    Метаданные содержат наименования колонок и пометки о том, можно ли их редактировать.
    
    @param dataset_id: идентификатор набора данных
    """
    user_datasets = get_datasets(request.user, settings.PERMISSION_VIEW_NAME)
    
    for dataset in user_datasets:
        if dataset.id == dataset_id:
            meta = get_fields(dataset, request.user)
            return {'meta':meta}
    return {'meta': None}


@jsonrpc_method('dataset.setDatasetFields', authenticated=True, safe=False)
def set_dataset_fields(request, dataset_id, fields):
    """
    Установить поля набора данных    
    @param dataset_id: идентификатор набора данных
    @param fields: Поля набора данных 
    """
    
    dataset = Dataset.objects.get(id=dataset_id)
    dataset.fields.clear()
    dataset.editor = request.user
    
    for item in fields:
        if qooxdoo_utils.get_item(item, 'id') == 0:
            pass
            #field = DatasetField()
            #field.name = item['$$user_name']
            #field.description = item['$$user_description']
            #field.creator = request.user
            #field.model_field_name = 
            #field.model_content_type = 
        else:
            field = DatasetField.objects.select_related().get(id = qooxdoo_utils.get_item(item, 'id'))
            field.editor = request.user
            field.name = qooxdoo_utils.get_item(item,'name')
            field.description = qooxdoo_utils.get_item(item,'description')
            field.index = qooxdoo_utils.get_item(item,'index')
            field.save()

            dataset.fields.add(field)

    dataset.save()
    
    return None

@jsonrpc_method('dataset.getData', authenticated=True, safe=False)
def get_dataset_data(request, dataset_id, start_date, end_date, company_objects, bookmarks):
    """
    Получить данные набора данных
    @param dataset_id: идентификатор набора данных
    """
    try:
        user_datasets = get_datasets(request.user, settings.PERMISSION_VIEW_NAME)
        date_range = (datetime.strptime(start_date, settings.DATE_FORMAT).date(),
                      datetime.strptime(end_date, settings.DATE_FORMAT).date())

        boilers = get_boilers(request.user, company_objects, bookmarks)
        
        if len(boilers)>0:
            for dataset in user_datasets:
                if dataset.id == dataset_id:
                    data = get_data(dataset, request.user, date_range, boilers)
                    return {'data': data}

    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
        _logger.error(u"[dataset.getData] - Ошибка при получении набора данных: " + unicode(ex))
        return {'data': [], 'message': ""}
    
    return {'data': []}

@jsonrpc_method('dataset.canEdit', authenticated=True, safe=True)
def can_edit_dataset(request, dataset_id):
    """
    Может ли пользователь редактировать набор данных.

    @param dataset_id: идентификатор набора данных
    """
    try:
        admin_role = Role.objects.get(name=settings.ROLE_ADMIN_NAME)
        if has_role(request.user, admin_role):
            #logging.getLogger(__name__).info(u"Пользователь является администратором, может редактировать набор данных!")
            return {'canEdit': True}
        
        for dataset in get_datasets(request.user, settings.PERMISSION_EDIT_NAME):
            if dataset.id == dataset_id:
                return {'canEdit': True}
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
        return {'canEdit': False, 'message': unicode(ex)}
 
    return {'canEdit': False, 'message': u"У вас нет прав редактировать набор данных"}

@jsonrpc_method('dataset.setData', authenticated=True, safe=False)
def set_dataset_data(request, field_id, on_date, company_object_id, water_category_id, fuel_info_id, value):
    """
    Установить новое значениче для указанной колонки.
    
    @param on_date: Дата 
    @param field_id: идентификатор колонки
    @param company_object_id: Идентификатор объекта 
    @param water_category_id: Идентификатор категории расхода воды
    @param fuel_info_id: Идентификатор информации о топливе
    @param value: новое значение
    
    @return: Возвращает объект
    """

    try:
        field = DatasetField.objects.get(id=field_id)
        # Дата на которую нужно заполнить значение
        my_date = datetime.strptime(on_date, settings.DATE_FORMAT).date()
        today = get_today()
        
        # Проверка разрешения установления значения
        if not has_permission(field, request.user, settings.PERMISSION_EDIT_NAME):
            return {'success': False, 'message': u"У вас недостаточно прав для редактирования."}

        set_value = False
        
        user_roles = get_roles(request.user)
        admin = Role.objects.get(name = settings.ROLE_ADMIN_NAME)
        manager = Role.objects.get(name = settings.ROLE_MANAGER_NAME)
        developer = Role.objects.get(name = settings.ROLE_DEVELOPER_NAME)
        editor = Role.objects.get(name = settings.ROLE_EDITOR_NAME)
        
        # Если пользователь выполняет одну из ролей он может выполнять
        # редактирование в любое время
        if admin in user_roles or manager in user_roles or developer in user_roles:  
            set_value = True
        
        # Если пользователь редактор - может в трехдневный срок редактировать данные
        elif editor in user_roles and (today - my_date).days < 4 and (today - my_date).days >= 0:
            set_value = True 

        if set_value:
            
            # Дополнительная проверка разрешения выполнять корректировку.
            if field.model_field_name == 'correct':
                # Даты в которые поле доступно для редактирования
                editable_on_date = (get_month_day(today, 10),   
                         get_month_day(today, 20),
                         get_month_day(today,get_month_last_day(today)) )
                
                if my_date not in editable_on_date:
                     return {'success': False, 'message': u"Корректировку можно делать только 10-го, 20-го и в последний день месяца"}
            
            # Информация о топливе
            fuel_info_obj = None
            if fuel_info_id > 0:
                fuel_info_obj = FuelInfo.objects.get(id=fuel_info_id)
    
            # Информация о воде
            water_category_obj = None
            if water_category_id > 0:
                water_category_obj = WaterConsumptionCategory.objects.get(id=water_category_id)
            
            # Котельная
            boiler = BoilerHouse.objects.get(id=company_object_id)
            # Установить значение
            field.set_value(request.user, my_date, value, boiler, water_category_obj, fuel_info_obj)
        else:
            return {'success': False, 'message': u"Редактирование доступно только в трехдневный срок."}
        
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
        _logger.error(u"[dataset.setData] - Не удалось сохранить значение: " + unicode(ex))
        
        return {'success': False, 'message': u"Не удалось сохранить значение " + unicode(ex)}
    
    return {'success': True, 'message' : u'Значение сохранено.'}

@jsonrpc_method('dataset.getFieldsByDatasetId', authenticated=True, safe=False)
def get_dataset_fields_detials(request, dataset_id):
    """
    Получить список всех полей для определенного наболра данных
    @param dataset_id: идентификатор набора данных
    """
    dataset = Dataset.objects.get(id = dataset_id)
    return serializers.serialize("json", dataset.fields.all())


@jsonrpc_method('dataset.getDatasetFieldPermissions', authenticated=True, safe=False)
def get_data_field_permissions(request, field_id):
    """
    Получить список разрешений для ролей, для указанного поля.
    
    @param field_id:  
    """

    content_type = ContentType.objects.get(app_label='dataset',model='datasetfield')
    
    data = []
    view_perm = Permission.objects.get(name=settings.PERMISSION_VIEW_NAME)
    edit_perm = Permission.objects.get(name=settings.PERMISSION_EDIT_NAME)
    
    if content_type != None:
        roles = Role.objects.all()

        for role in roles:
            view = ObjectPermission.objects.filter(role=role,
                                            content_type=content_type,
                                            content_id=field_id,
                                            permission = view_perm).count()
            
            edit = ObjectPermission.objects.filter(role=role,
                                            content_type=content_type,
                                            content_id=field_id,
                                            permission =edit_perm).count()

            can_edit = True if edit > 0 else False
            can_view = True if view > 0 else False
                 
            data.append([role.id,
                         role.name,
                         can_edit, 
                         can_view])
            
    return {'permissions': data} 

@jsonrpc_method('dataset.setDatasetFieldPermissions', authenticated=True, safe=False)
def set_dataset_field_permissions(request, field_id, data):
    """
    Получить список разрешений для ролей, для указанного поля набора данных.
    
    @param field_id:
    @param data: массив данных. [[<ROLE_ID>,<ROLE_NAME>,<CAN_EDIT>,<CAN_VIEW>],...] 
       ROLE_ID - идентификатор роли
       ROLE_NAME - наименование роли
       CAN_EDIT - может ли редактировать - булево
       CAN_VIEW - модет ли просматривать - булево
    """
    try:
        content_type = ContentType.objects.get(app_label='dataset',model='datasetfield')
    
        view_perm = Permission.objects.get(name=settings.PERMISSION_VIEW_NAME)
        edit_perm = Permission.objects.get(name=settings.PERMISSION_EDIT_NAME)
        
        if content_type != None:
            for item in data:
                role = Role.objects.get(id=item[0])
                # can edit
                if item[2]:
                    obj_edit_perm, created = ObjectPermission.objects.get_or_create(role=role,
                                                content_type=content_type,
                                                content_id=field_id,
                                                permission = edit_perm)
                else:
                    ObjectPermission.objects.filter(role=role,
                                                content_type=content_type,
                                                content_id=field_id,
                                                permission = edit_perm).delete()
                # can view
                if item[3]:
                    obj_view_perm, created = ObjectPermission.objects.get_or_create(role=role,
                                                content_type=content_type,
                                                content_id=field_id,
                                                permission = view_perm)
                else:
                    ObjectPermission.objects.filter(role=role,
                                                content_type=content_type,
                                                content_id=field_id,
                                                permission = view_perm).delete()
                
        
        return {'saved': True}            
    except Exception, ex:
        return {'saved': False}

@jsonrpc_method('dataset.getDatasetPermissions', authenticated=True, safe=False)
def get_dataset_permissions(request, dataset_id):
    """
    Получить список разрешений для ролей, для указанного набора данных.
    
    @param dataset_id:  
    """
    content_type = ContentType.objects.get(app_label='dataset',model='dataset')

    data = []
    view_perm = Permission.objects.get(name=settings.PERMISSION_VIEW_NAME)
    edit_perm = Permission.objects.get(name=settings.PERMISSION_EDIT_NAME)
    
    if content_type != None:
        roles = Role.objects.all()

        for role in roles:
            view = ObjectPermission.objects.filter(role=role,
                                            content_type=content_type,
                                            content_id=dataset_id,
                                            permission = view_perm).count()
            
            edit = ObjectPermission.objects.filter(role=role,
                                            content_type=content_type,
                                            content_id=dataset_id,
                                            permission =edit_perm).count()

            can_edit = True if edit > 0 else False
            can_view = True if view > 0 else False
                 
            data.append([role.id,role.name, can_edit,can_view]) 
    return {'permissions': data}            

@jsonrpc_method('dataset.setDatasetPermissions', authenticated=True, safe=False)
def set_dataset_permissions(request, dataset_id, data):
    """
    Установить разрешения для указанного набора данных.
    
    @param dataset_id:
    @param data: массив данных. [[<ROLE_ID>,<ROLE_NAME>,<CAN_EDIT>,<CAN_VIEW>],...] 
       ROLE_ID - идентификатор роли
       ROLE_NAME - наименование роли
       CAN_EDIT - может ли редактировать - булево
       CAN_VIEW - модет ли просматривать - булево
    """
    try:
        content_type = ContentType.objects.get(app_label='dataset',model='dataset')
        
        view_perm = Permission.objects.get(name=settings.PERMISSION_VIEW_NAME)
        edit_perm = Permission.objects.get(name=settings.PERMISSION_EDIT_NAME)
        
        if content_type != None:
            for item in data:
                print item
                role = Role.objects.get(id=item[0])            
                # can edit
                if item[2]:
                    obj_edit_perm, created = ObjectPermission.objects.get_or_create(role=role,
                                                content_type=content_type,
                                                content_id=dataset_id,
                                                permission = edit_perm)
                else:
                    ObjectPermission.objects.filter(role=role,
                                                content_type=content_type,
                                                content_id=dataset_id,
                                                permission = edit_perm).delete()
                # can view
                if item[3]:
                    
                    obj_view_perm, created = ObjectPermission.objects.get_or_create(role=role,
                                                content_type=content_type,
                                                content_id=dataset_id,
                                                permission = view_perm)
                else:
                    ObjectPermission.objects.filter(role=role,
                                                content_type=content_type,
                                                content_id=dataset_id,
                                                permission = view_perm).delete()
                
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
        _logger.error(u"[dataset.setDatasetPermissions] - Ошибка " + unicode(ex))
        
        return {'saved': False}
    
    return {'saved': True}            



@jsonrpc_method('dataset.getAvailableFields', authenticated=True, safe=False)
def get_all_fields(request, dataset_id):
    """
    Получить список всех доступных полей
    """
    
    field_ids = Dataset.objects.select_related().all().values_list('fields__id', flat=True)
    fields = DatasetField.objects.exclude(id__in = field_ids)
    #print serializers.serialize("json", fields)
    return serializers.serialize("json", fields)

@jsonrpc_method('dataset.validateValue', authenticated=True, safe=True)
def validate_field_data(request, dataset_field_id):
    """
    Проверить новое значение поля
    """
    import validate
    dataset_field = DatasetField.objects.get(dataset_field_id)
    result = validate.validation(dataset_field)
    
    return True


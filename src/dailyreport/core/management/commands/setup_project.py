# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

from dailyreport.dataset.utils import get_models_content_types, get_model_fields
from dailyreport.dataset.models import DatasetField, Dataset
from dailyreport.deviation.models import ParameterDeviationProblem ,\
    ParameterDeviationProblemState
from dailyreport.company_object.models import Resource

from permissions.utils import register_role, register_permission, add_role,\
    get_global_roles
from permissions.models import Role


_logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    
    """
    args = ''
    help = 'It setups project with initial data.'

    def handle(self, *args, **options):
        
        _logger.info("Setup @Permissions layer")
        self.create_permissions()
        self.create_groups()
        self.create_roles()
        self.create_role_principal_relation()
        
        _logger.info("Setup @Data layer")
        self.create_resources()
        self.create_default_fuel_types()
        self.create_default_water_categories()
    
        _logger.info("Setup @Services layer")
        self.create_parameter_deviation_states()
    
        _logger.info("Push initial data")
        self.push_data()

    def create_groups(self):
        """
        Создать нужные группы
        """
        Group.objects.get_or_create(name = settings.DEVELOPERS_GROUP_NAME)
        Group.objects.get_or_create(name = settings.MANAGERS_GROUP_NAME)
        Group.objects.get_or_create(name = settings.ADMINS_GROUP_NAME)
        Group.objects.get_or_create(name = settings.VIEWERS_GROUP_NAME)
        Group.objects.get_or_create(name = settings.EDITORS_GROUP_NAME)        
        
    def create_roles(self):
        """
        Создать роли используемые в приложении
        """
        register_role(settings.ROLE_DEVELOPER_NAME)
        register_role(settings.ROLE_ADMIN_NAME)
        register_role(settings.ROLE_MANAGER_NAME)
        register_role(settings.ROLE_EDITOR_NAME)
        register_role(settings.ROLE_VIEWER_NAME)
        
        logging.getLogger(__name__).info(u"Созданы роли: Разработчик, Администратор, Менеджер, Редактор, Обозреватель.")
    
    def create_permissions(self):
        """
        Создать разрешения
        """
        content_types = [Dataset, DatasetField]

        register_permission(settings.PERMISSION_VIEW_NAME,
                            settings.PERMISSION_VIEW_NAME, content_types)
        register_permission(settings.PERMISSION_EDIT_NAME,
                            settings.PERMISSION_EDIT_NAME, content_types)
        register_permission(settings.PERMISSION_CREATE_NAME,
                            settings.PERMISSION_CREATE_NAME, content_types)
        register_permission(settings.PERMISSION_DELETE_NAME,
                            settings.PERMISSION_DELETE_NAME, content_types)

        logging.getLogger(__name__).info(u"Созданы разрешения: Просмотр, Редактировать, Создать, Удалить.")

    def create_role_principal_relation(self):
        """
        """

        group = Group.objects.get(name = settings.DEVELOPERS_GROUP_NAME)
        print group
        if len(get_global_roles(group)) == 0:
            role = Role.objects.get(name = settings.ROLE_DEVELOPER_NAME)
            add_role(group, role)

        group = Group.objects.get(name = settings.ADMINS_GROUP_NAME)
        print group
        if len(get_global_roles(group)) == 0:
            role = Role.objects.get(name = settings.ROLE_ADMIN_NAME)
            add_role(group, role)

        group = Group.objects.get(name = settings.MANAGERS_GROUP_NAME)
        print group
        if len(get_global_roles(group)) == 0:
            role = Role.objects.get(name = settings.ROLE_MANAGER_NAME)
            add_role(group, role)

        group = Group.objects.get(name = settings.EDITORS_GROUP_NAME)
        print group
        if len(get_global_roles(group)) == 0:
            role = Role.objects.get(name = settings.ROLE_EDITOR_NAME)
            add_role(group, role)

        group = Group.objects.get(name = settings.VIEWERS_GROUP_NAME)
        print group
        if len(get_global_roles(group)) == 0:
            role = Role.objects.get(name = settings.ROLE_VIEWER_NAME)
            add_role(group, role)


    def create_parameter_deviation_states(self):
        """
        Создать состояния для проблемы по отклонению суточного параметра 
        от планового значения.
        """ 
        obj,created = ParameterDeviationProblemState.objects.get_or_create(name=settings.DEVIATION_PROBLEM_STATE_OPEN)
        obj,created = ParameterDeviationProblemState.objects.get_or_create(name=settings.DEVIATION_PROBLEM_STATE_CLOSED)
   
    def create_resources(self):
        """
        Создать типы ресурсов в системе.
        """
        obj,created = Resource.objects.get_or_create(name=settings.RESOURCE_TYPE_WATER)
        obj,created = Resource.objects.get_or_create(name=settings.RESOURCE_TYPE_ELECTRICITY)
        obj,created = Resource.objects.get_or_create(name=settings.RESOURCE_TYPE_FUEL)
        
    def create_default_water_categories(self):
        """
        Создает категории расхода воды
        """ 
        pass
    
    def create_default_fuel_types(self):
        """
        Создает виды топлива
        """
        pass
    
    def create_dataset_fields(self):
        """
        """
        pass
    
    def create_datasets(self):
        """
        """
        pass
    
    def push_data(self):
        """
        Разворачивает данные.
        Данные могут быть взяты из работающего экземпляра программы.
        """
        pass
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from permissions.utils import register_permission, register_role, register_group
from permissions.models import Permission, Role 
from django.conf import settings
import logging
from django.contrib.contenttypes.models import ContentType
from dailyreport.dataset.models import Dataset, DatasetField

class Command(BaseCommand):
    args = u"Аргуметов не требуется."
    help = u"Создает необходимые для работы приложения роли и разрешения."

    def handle(self, *args, **options):
        content_types = [Dataset, DatasetField]
        #Permission.objects.all().delete()
        #PERMISSIONS
        register_permission(settings.PERMISSION_VIEW_NAME,
                            settings.PERMISSION_VIEW_NAME, content_types)
        register_permission(settings.PERMISSION_EDIT_NAME,
                            settings.PERMISSION_EDIT_NAME, content_types)
        register_permission(settings.PERMISSION_CREATE_NAME,
                            settings.PERMISSION_CREATE_NAME, content_types)
        register_permission(settings.PERMISSION_DELETE_NAME,
                            settings.PERMISSION_DELETE_NAME, content_types)
        logging.getLogger(__name__).info("Созданы разрешения: Просмотр, Редактировать, Создать, Удалить.")

        # ROLES
        #Role.objects.all().delete()
        register_role(settings.ROLE_DEVELOPER_NAME)
        register_role(settings.ROLE_ADMIN_NAME)
        register_role(settings.ROLE_MANAGER_NAME)
        register_role(settings.ROLE_EDITOR_NAME)
        register_role(settings.ROLE_VIEWER_NAME)
        logging.getLogger(__name__).info("Созданы роли: Разработчик, Администратор, Менеджер, Редактор, Обозреватель.")

# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.conf import settings
from dailyreport.user_profile.models import UserProfile
from permissions.models import Role
from permissions.utils import add_role

class Command(BaseCommand):
    """

    """
    args = u"Роль которая будет присвоена профилю: viewer, editor, manager, admin, developer."
    help = u"Создает профили для пользователей, у которых еще нет профилей."

    def handle(self, role_name="viewer", *args, **options):
        user_ids = UserProfile.objects.all().values_list('id', flat=True)
        users = User.objects.exclude(id__in=user_ids)

        managers_group, created = Group.objects.get_entity(name = settings.MANAGERS_GROUP_NAME)
        editors_group, created = Group.objects.get_entity(name = settings.EDITORS_GROUP_NAME)
        viewer_group, created = Group.objects.get_entity(name = settings.VIEWERS_GROUP_NAME)
        dev_group, created = Group.objects.get_entity(name = settings.DEVELOPERS_GROUP_NAME)
        admin_group, created = Group.objects.get_entity(name = settings.ADMINS_GROUP_NAME)
        
        for user in users:
            profile = UserProfile()
            profile.user = user
            profile.save()
            role = None
            
            if role_name == "viewer":
                role = Role.objects.get(name=settings.ROLE_VIEWER_NAME)
                user.groups.add(viewer_group)
                user.save()
                add_role(viewer_group, role)
                
            elif role_name == "manager":
                role = Role.objects.get(name=settings.ROLE_MANAGER_NAME)
                user.groups.add(managers_group)
                user.save()
                add_role(managers_group, role)
                
            elif role_name == "developer":
                role = Role.objects.get(name=settings.ROLE_DEVELOPER_NAME)
                user.groups.add(dev_group)
                user.save()
                add_role(dev_group,role)
                
            elif role_name == "admin":
                role = Role.objects.get(name=settings.ROLE_ADMIN_NAME)
                user.groups.add(admin_group)
                user.save()
                add_role(admin_group,role)
                
            elif role_name == "editor":
                role = Role.objects.get(name=settings.ROLE_EDITOR_NAME)
                user.groups.add(editors_group)
                user.save()
                add_role(editors_group, role)
                
            else:
                role = Role.objects.get(name=settings.ROLE_VIEWER_NAME)
                user.groups.add(viewer_group)
                user.save()
                add_role(viewer_group, role)
            


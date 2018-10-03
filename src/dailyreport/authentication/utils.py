# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User


def get_project_admin_user():
    """
    Получить пользователей-администраторов проекта.
    """
    manager_email = settings.MANAGERS[0][1]
    print manager_email
    manager_user = User.objects.get(email=manager_email)
    print manager_user
    return manager_user

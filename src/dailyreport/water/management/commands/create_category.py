# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.conf import settings
from dailyreport.company_object.models import BoilerHouse
from dailyreport.water.water_utils import initialize_water_categories



class Command(BaseCommand):
    """

    """
    args = u"Роль которая будет присвоена профилю: viewer, editor, manager, admin, developer."
    help = u"Создает профили для пользователей, у которых еще нет профилей."

    def handle(self, id, *args, **options):
        boiler = BoilerHouse.objects.get(id=id)
        
        manager_email = settings.MANAGERS[0][1]
        manager_user = User.objects.get(email=manager_email)
        print boiler
        initialize_water_categories(manager_user, boiler)
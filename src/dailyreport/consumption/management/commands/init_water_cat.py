# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from dailyreport.company_object.models import BoilerHouse
from dailyreport.consumption.models import WaterConsumptionCategory


class Command(BaseCommand):
    """
    
    """
    args = ''
    help = 'Initialize water categories for all boilerhouses.'

    def handle(self, *args, **options):
        manager_email = settings.MANAGERS[0][1]
        manager_user = User.objects.get(email=manager_email)
        
        for boiler in BoilerHouse.objects.all():
            water_category = WaterConsumptionCategory()
            water_category.creator = manager_user
            water_category.boiler = boiler
            water_category.name = u"Общий расход"
            water_category.save(save_revision=True)
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from dailyreport.company_object.models import BoilerHouse
from dailyreport.consumption.models import FuelInfo

class Command(BaseCommand):
    """
    
    """
    args = ''
    help = 'Initialize fuel info for all boilerhouses.'

    def handle(self, *args, **options):
        
        manager_email = settings.MANAGERS[0][1]
        manager_user = User.objects.get(email=manager_email)
        
        for boiler in BoilerHouse.objects.all():
            fuel_info = FuelInfo()
            fuel_info.creator = manager_user
            fuel_info.boiler = boiler
            fuel_info.type = u"Уголь"
            fuel_info.save(save_revision=True)
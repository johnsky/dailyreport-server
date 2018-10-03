# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from dailyreport.company_object.models import BoilerHouse
from dailyreport.consumption.models import FuelInfo, FuelConsumption

class Command(BaseCommand):
    """
    
    """
    args = ''
    help = 'Recalculates fuel consumption plans for all boilers on 1st of the october.'

    def handle(self, *args, **options):
        
        manager_email = settings.MANAGERS[0][1]
        manager_user = User.objects.get(email=manager_email)

        for boiler in BoilerHouse.objects.all():
            print boiler.id
            for item in FuelConsumption.objects.filter(fuel_info__active=True, fuel_info__boiler = boiler, date = '2011-10-01'):
                item.save(force_update=True)
                item.update_period()
                
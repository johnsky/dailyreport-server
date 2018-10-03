# -*- coding: utf-8 -*-

import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType



class Command(BaseCommand):
    """
    
    """
    args = ''
    help = 'It checks deviation of resources daily consumption.'
    
    def handle(self, *args, **options):
        
        # check fuel
        from dailyreport.fuel.models import FuelConsumption
        from dailyreport.utils.date_utils import get_today
        from dailyreport.deviation.models import ParameterDeviationProblem
        from dailyreport.deviation.utils import create_problem
        
        cons =  FuelConsumption.objects.filter(
                 date__lte = get_today() - datetime.timedelta(3)).extra(
                 where=['1-(plan_day/real_plan_day) >=0.05', 'real_plan_day > 0', 'plan_day > 0',
                        "id NOT IN (SELECT fuel_id FROM deviation WHERE fuel_id IS NOT NULL ORDER BY deviation.start_date ASC)"])
        
        for item in cons:
            #print item
            create_problem(item)
        
        
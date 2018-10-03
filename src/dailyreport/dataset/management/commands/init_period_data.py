# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from dailyreport.dataset.utils import get_data
from dailyreport.dataset.models import DatasetField, Dataset
from dailyreport.utils.date_utils import get_today, get_month_range
from dailyreport.company_object.models import BoilerHouse

class Command(BaseCommand):
    """
    
    """
    args = ''
    help = 'Creates data for period.'

    def handle(self, month=0, year=0, dataset_id = 0, *args, **options):
        
        manager_email = settings.MANAGERS[0][1]
        manager_user = User.objects.get(email=manager_email)

        month_range = [] 
        if month == 0:
            today = get_today()
            month_range = get_month_range(today.year, today.month)
        else:
            month_range = get_month_range(int(year), int(month))
        
        boilers = BoilerHouse.objects.all()
        datasets = []
        if dataset_id == 0:
            datasets = Dataset.objects.all()
        else:
            datasets = Dataset.objects.filter(id=dataset_id)
            
        for dataset in datasets:
            print u"GETTING DATA FOR DATASET ID=" + unicode(dataset.id) + ", MONTH RANGE="+unicode(month_range)
            get_data(dataset, manager_user, month_range, boilers)
            print "DATA GETTING WAS COMPLETE."

            
        
        
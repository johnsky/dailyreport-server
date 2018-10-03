# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from dailyreport.utils.date_utils import get_month_range, current_year, current_month
from dailyreport.consumption.models import Period


class Command(BaseCommand):
    """
    
    """
    args = ''
    help = 'Creates neccesary Period records.'

    def handle(self, *args, **options):
        period_range = get_month_range(current_year(), current_month())
        try:
            Period.objects.get(start_date = period_range[0],
                               end_date=period_range[1])
        except Period.DoesNotExist:
            manager_email = settings.MANAGERS[0][1]
            manager_user = User.objects.get(email=manager_email)
            period = Period()
            period.creator = manager_user
            period.start_date = period_range[0]
            period.end_date = period_range[1]
            period.save(save_revision=True)
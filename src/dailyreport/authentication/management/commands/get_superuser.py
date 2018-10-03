# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User



class Command(BaseCommand):
    """
    
    """
    args = ''
    help = 'Creates neccesary Period records.'

    def handle(self, *args, **options):
        
        manager_email = settings.MANAGERS[0][1]
        print manager_email
        manager_user = User.objects.get(email=manager_email)
        print manager_user
# -*- coding: utf-8 -*-
import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

_logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    
    """
    args = ''
    help = 'Import data from another.'

    def handle(self, *args, **options):
        pass
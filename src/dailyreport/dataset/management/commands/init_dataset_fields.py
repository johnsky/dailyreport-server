# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from dailyreport.dataset.utils import get_models_content_types, get_model_fields
from dailyreport.dataset.models import DatasetField

class Command(BaseCommand):
    """
    
    """
    args = ''
    help = 'Creates fields for all available fields.'

    def handle(self, *args, **options):
        
        manager_email = settings.MANAGERS[0][1]
        manager_user = User.objects.get(email=manager_email)
        
        content_types = get_models_content_types()
        print content_types
        
        for content_type in content_types:
            fields = get_model_fields(content_type)
            index = 0
            
            for field in fields:
                if DatasetField.objects.filter(model_field_name = field.name, model_content_type = content_type).count() == 0:
                    df = DatasetField()
                    df.creator = manager_user
                    df.name = field.verbose_name
                    df.description = field.help_text
                    df.internal_name = field.verbose_name
                    df.model_field_name = field.name
                    df.model_content_type = content_type
                    df.index = index
                    df.save(save_revision=True)
                    print df

                index = index + 1
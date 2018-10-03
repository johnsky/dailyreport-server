# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from dailyreport.dataset.utils import get_models_content_types, get_model_fields
from dailyreport.dataset.models import DatasetField, Dataset
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    """
    
    """
    args = ''
    help = 'Creates datasets and appends fields. The command must be executed after init_fields.'

    def handle(self, *args, **options):
        
        manager_email = settings.MANAGERS[0][1]
        manager_user = User.objects.get(email=manager_email)
        
        
        
        # Расход воды
        water_dataset = Dataset()
        water_dataset.creator = manager_user
        water_dataset.name = u"Ежедневный расход воды"
        water_dataset.description = u"Ежедневный расход воды"
        
        fields = DatasetField.objects.filter(model_content_type__app_label='water',
                                             model_content_type__model='waterconsumption')
        
        water_dataset.save()
        for field in fields:
            water_dataset.fields.add(field)
        
        water_dataset.save(save_revision=True)
        
        # Расход толплива
        fuel_dataset = Dataset()
        fuel_dataset.creator = manager_user
        fuel_dataset.description = u"Ежедневный расход топлива"
        fuel_dataset.name = u"Ежедневный расход топлива"
        
        fields = DatasetField.objects.filter(model_content_type__model__in=['environment','fuelincome','fuelconsumption','fuelremains','powerperformance']).order_by('index')
        
        fuel_dataset.save()
        for field in fields:
            fuel_dataset.fields.add(field)
        
        fuel_dataset.save(save_revision=True)
        
        # Расход электричества
        elect_dataset = Dataset()
        elect_dataset.creator = manager_user
        elect_dataset.description = u"Ежедневный расход электричества"
        elect_dataset.name = u"Ежедневный расход электричества"
        fields = DatasetField.objects.filter(model_content_type__model='electricityconsumption')
        
        elect_dataset.save()
        for field in fields:
            elect_dataset.fields.add(field)
        
        elect_dataset.save(save_revision=True)
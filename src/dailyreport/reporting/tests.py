# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from dailyreport.dataset.models import get_entity
import dailyreport.core.models as _u
import dailyreport.utils.date_utils as _du 

class GetOrCreateTest(TestCase):
    def setUp(self):
        """
        Pre-execution
        """
        # test user
        self.test_user = User.objects.create_user('test', 'test@test.com', '123')
        self.test_user.is_staff = True
        self.test_user.save()
    
    def tearDown(self):
        """
        A test Post-execution 
        """
        
        #Удаляем всех пользователей
        User.objects.all().delete()
        

    def create_boiler(self):
        
        self.branch_obj = Branch.objects.create(name = u"Филиал",
                                                creator = self.test_user)
        self.thermal_area_obj = ThermalArea.objects.create(name = u"Тепловой район",
                                           branch = self.branch_obj,
                                           creator = self.test_user)
        self.boiler_obj = BoilerHouse.objects.create(name = u"Котельная",
                                creator = self.test_user, 
                                thermalArea = self.thermal_area_obj,
                                branch = self.branch_obj)
        
    def test_method(self):
        #self.create_boiler()
        # диапазон дат для которых нужно загрузить данные по отчету
        #date_range = _du.get_month_range(_du.current_year(), _du.current_month())
        #get_entity(self.test_user, self.boiler_obj, on_date, model_class)
        pass

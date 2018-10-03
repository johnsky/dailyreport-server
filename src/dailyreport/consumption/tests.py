# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
from dailyreport.company_object.models import BoilerHouse, ThermalArea, Branch
from dailyreport.consumption.models import Environment, PowerPerformance
from dailyreport.utils.date_utils import get_month_day, get_today

import datetime
import reversion

def create_test_user():
    # test users
    test_user = User.objects.create_user('test', 'test@test.com', '123')
    test_user.is_staff = True
    test_user.save()
    return test_user

def create_test_boiler(user): 
    #Enterprise structure objects
    branch_obj = Branch.objects.create(name = u"Филиал",
                                      creator = user)
    
    thermal_area_obj = ThermalArea.objects.create(name = u"Тепловой район",
                                        branch = branch_obj,
                                        creator = user)


    boiler_obj = BoilerHouse.objects.create(name=u"Котельная",
                                        thermalArea = thermal_area_obj,
                                        branch = branch_obj,
                                        address = u"Адрес котельной",
                                        creator = user)
    return boiler_obj

def get_test_date():
    return get_today()

class EnvironmentTest(TestCase):
    def setUp(self):
        """
        Pre-execution
        """
        self.test_user = create_test_user()
        self.boiler_obj = create_test_boiler(self.test_user)
        
    def tearDown(self):
        """
        Post-execution
        """
        Environment.objects.all().delete()
        User.objects.all().delete()
        BoilerHouse.objects.all().delete()
    
    def test_creation(self):
        obj = Environment.objects.create(creator=self.test_user,
                                                  date=get_test_date(),
                                                  boiler=self.boiler_obj)
        self.assertIsNotNone(obj)

class PowerPerformanceTest(TestCase):
    def setUp(self):
        """
        Pre-execution
        """
        self.test_user = create_test_user()
        self.boiler_obj = create_test_boiler(self.test_user)
        
    def tearDown(self):
        """
        Post-execution
        """
        PowerPerformance.objects.all().delete()
        User.objects.all().delete()
        BoilerHouse.objects.all().delete()
        
    def test_creation(self):
        obj = PowerPerformance.objects.create(creator=self.test_user,
                                              date=get_test_date(),
                                              boiler=self.boiler_obj)
        self.assertIsNotNone(obj)

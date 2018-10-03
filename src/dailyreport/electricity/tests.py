# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from dailyreport.company_object.models import BoilerHouse, ThermalArea, Branch
import datetime
import reversion
from models import ElectricityConsumption
from dailyreport.utils.date_utils import get_month_day, get_today,get_month_last_day

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

class ElectricityConsumptionTest(TestCase):
    def setUp(self):
        """
        Pre-execution
        """
        # test users
        self.test_user = create_test_user()        
        self.boiler_obj = create_test_boiler(self.test_user)
    
    def tearDown(self):
        """
        Post-execution
        """
        User.objects.all().delete()
        BoilerHouse.objects.all().delete()
        ElectricityConsumption.objects.all().delete()
        
    def test_second_day_month_saving(self):
        """
        Test two dates of period saving
        """
        #first date
        test_date1 = datetime.date(2011, 1, 1)
        # new consumption object
        obj1 = ElectricityConsumption(boiler = self.boiler_obj,
                                             date = test_date1,
                                             creator = self.test_user)

        obj1.actual_day = 15
        obj1.plan_month = 310
        obj1.save(force_insert=True)
        
        # second date
        test_date2 = datetime.date(2011, 1, 2)
        obj2 = ElectricityConsumption(boiler = self.boiler_obj,
                                      date = test_date2,
                                      creator = self.test_user)

        obj2.actual_day = 16
        obj2.save(force_insert=True)
        
        #check first date
        self.assertEquals(obj1.actual_day, 15)
        self.assertEquals(obj1.actual_sum_period, 15)
        self.assertEquals(obj1.plan_month, 310)
        self.assertEquals(obj1.plan_day, 10)
        self.assertEquals(obj1.plan_sum_period, 10)
        self.assertEquals(obj1.diff_period_percent, 50 )
        
        # check second date
        self.assertEquals(obj2.actual_day, 16)
        self.assertEquals(obj2.actual_sum_period, 31)
        self.assertEquals(obj2.plan_month, 310)
        self.assertEquals(obj2.plan_day, 10)
        self.assertEquals(obj2.plan_sum_period, 20)
        self.assertEquals(obj2.diff_period_percent, 55 )
        
    def test_first_day_month_saving(self):
        """
        Save on first day month
        """
        test_date = datetime.date(2011, 1, 1)
        # new consumption object
        obj = ElectricityConsumption(boiler = self.boiler_obj,
                                             date = test_date,
                                             creator = self.test_user)
        # fill values
        obj.actual_day = 15
        obj.plan_month = 310
        obj.save()
        
        # getting test object 
        test_obj = ElectricityConsumption.objects.get(id=obj.id)

        #
        self.assertEquals(test_obj.actual_day, 15)
        self.assertEquals(test_obj.actual_sum_period, 15)
        self.assertEquals(test_obj.plan_month, 310)
        self.assertEquals(test_obj.plan_day, 10)
        self.assertEquals(test_obj.plan_sum_period, 10)
        self.assertEquals(test_obj.diff_period_percent, 50 )
        
    def test_period_update(self):
        """
        Save on first day month
        """
        date1 = datetime.date(2011, 1, 1)
        date2 = datetime.date(2011, 1, 3)
        
        # new consumption object
        obj = ElectricityConsumption(boiler = self.boiler_obj,
                                             date = date1,
                                             creator = self.test_user)
        # fill values
        obj.actual_day = 15
        obj.plan_month = 310
        obj.save(save_revision=True)
        
        # getting test object 
        obj1 = ElectricityConsumption.objects.get(id=obj.id)

        #
        self.assertEquals(obj1.actual_day, 15)
        self.assertEquals(obj1.actual_sum_period, 15)
        self.assertEquals(obj1.plan_month, 310)
        self.assertEquals(obj1.plan_day, 10)
        self.assertEquals(obj1.plan_sum_period, 10)
        self.assertEquals(obj1.diff_period_percent, 50 )

        obj2 = ElectricityConsumption(boiler = self.boiler_obj,
                                     date = date2,
                                     creator = self.test_user)

        # План на месяц 410
        obj2.actual_day = 17
        obj2.plan_month = 410
        obj2.save(save_revision=True)
        
        #
        self.assertEquals(obj2.actual_day, 17)
        self.assertEquals(obj2.actual_sum_period, 32)
        self.assertEquals(obj2.plan_month, 310)
        self.assertEquals(obj2.plan_day, 10)
        self.assertEquals(obj2.plan_sum_period, 30)
        self.assertEquals(obj2.diff_period_percent, 6.667 )

        # change month plan, expecting that the values 
        # for the period has been updated
        obj1.plan_month = 620
        obj1.save(save_revision=True)
        
        obj1.update_period()
        
        obj2 = ElectricityConsumption.objects.get(boiler = self.boiler_obj,
                                     date = date2)       
        # First day values checking
        self.assertEquals(obj1.actual_day, 15)
        self.assertEquals(obj1.actual_sum_period, 15)
        self.assertEquals(obj1.plan_month, 620)
        self.assertEquals(obj1.plan_day, 20)
        self.assertEquals(obj1.plan_sum_period, 20)
        self.assertEquals(obj1.diff_period_percent, -25 )

        # Second date values checking 
        self.assertEquals(obj2.actual_day, 17)
        self.assertEquals(obj2.actual_sum_period, 32)
        self.assertEquals(obj2.plan_month, 620)
        self.assertEquals(obj2.plan_day, 20)
        self.assertEquals(obj2.plan_sum_period, 60)
        self.assertEquals(obj2.diff_period_percent, -46.667 )
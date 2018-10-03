# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User

from models import FuelIncome, FuelRemains, FuelConsumption, FuelInfo
from dailyreport.company_object.models import BoilerHouse, ThermalArea, Branch, Period
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

class FuelIncomeTest(TestCase):
    """
    Тестирование поступлений топлива
    """
    
    def setUp(self):
        """
        Pre-execution
        """
        self.date1 = datetime.date(2011, 1, 1)
        self.date2 = datetime.date(2011, 1, 2)
        self.date3 = datetime.date(2011, 1, 3)
        
        self.test_user = create_test_user()
        self.boiler_obj = create_test_boiler(self.test_user)
        
        # Fuel infomation first
        self.fuel_info1 = FuelInfo.objects.create(boiler=self.boiler_obj,
                        creator = self.test_user,
                        type = "Coal")
        
        # Fuel infomation second
        self.fuel_info2 = FuelInfo.objects.create(boiler=self.boiler_obj,
                        creator = self.test_user,
                        type = "Coal")        
    def tearDown(self):
        """
        Post-execution
        """
        FuelIncome.objects.all().delete()
        FuelInfo.objects.all().delete()
        User.objects.all().delete()
        BoilerHouse.objects.all().delete()
        
    def test_creation(self):
        """
        
        """
        obj2 = FuelIncome(creator=self.test_user,
                        date=self.date2,
                        boiler=self.boiler_obj,
                        fuel_info = self.fuel_info1) 
        obj2.today = 100.5
        obj2.save()
        
        self.assertEquals(obj2.today, 100.5)
        self.assertEquals(obj2.month, 100.5)
        
        try:
            obj1 = FuelIncome.objects.get(date=self.date1, fuel_info = self.fuel_info1)
            self.fail("FuelIncome object should be created.")
        except FuelIncome.DoesNotExist:
            pass
    
class FuelRemainsTest(TestCase):
    def setUp(self):
        """
        Pre-execution
        """
        self.date1 = datetime.date(2011, 1, 1)
        self.date2 = datetime.date(2011, 1, 2)
        self.date3 = datetime.date(2011, 1, 3)
        
        self.test_user = create_test_user()
        
        # Boiler house
        self.boiler_obj = create_test_boiler(self.test_user)
        
        # Fuel infomation first
        self.fuel_info1 = FuelInfo.objects.create(boiler=self.boiler_obj,
                        creator = self.test_user,
                        type = "Coal")
        
        # Fuel infomation second
        self.fuel_info2 = FuelInfo.objects.create(boiler=self.boiler_obj,
                        creator = self.test_user,
                        type = "Coal")
        
    def tearDown(self):
        """
        Post-execution
        """
        FuelRemains.objects.all().delete()
        FuelInfo.objects.all().delete()
        User.objects.all().delete()
        BoilerHouse.objects.all().delete()
        
    def test_creation(self):
        """
        1. Создаем объект остатоков на первый день месяца (остатки топлива на 1е число месяца = 10.5)
        2. Создаем объект остатков топлива на второй день месяца с первым видом топлива
        3. Создаем объект остатков топлива на второй день со вторым видом топлива
        4. Получаем объект на первый день со вторым видом топлива
        """
        obj1 = FuelRemains.objects.create(boiler=self.boiler_obj,
                                         date=self.date1,
                                         creator=self.test_user,
                                         fuel_info = self.fuel_info1,
                                         first_day_month = 10.5)
        
        self.assertEquals(obj1.first_day_month, 10.5)
        
        obj2 = FuelRemains.objects.create(boiler=self.boiler_obj,
                                         date=self.date2,
                                         creator=self.test_user,
                                         fuel_info = self.fuel_info1)
        
        self.assertEquals(obj2.first_day_month, 10.5)
        
        obj3 = FuelRemains.objects.create(boiler=self.boiler_obj,
                                         date=self.date2,
                                         creator=self.test_user,
                                         fuel_info = self.fuel_info2)
        
        self.assertEquals(obj3.first_day_month, 0)

        #try:
        #    obj4 = FuelRemains.objects.get(date=self.date1, fuel_info = self.fuel_info2)
        #except FuelRemains.DoesNotExist:
        #    self.fail("FuelRemains wasn't created.")

    def test_changing_after_setting_consumption(self):
        """
        Проверка того, что обновляются остатки топлива после введения расхода топлива
        """
        obj2 = FuelRemains(boiler=self.boiler_obj,
                         date=self.date2,
                         creator=self.test_user,
                         fuel_info = self.fuel_info1)
        obj2.first_day_month = 15.5
        obj2.save(save_revision=True, force_insert=True)
        
        cons = FuelConsumption(boiler=self.boiler_obj,
                             date=self.date2,
                             creator=self.test_user,
                             fuel_info = self.fuel_info1)
        cons.actual_day = 3.6
        cons.save(save_revision=True)
        cons.update_period()
        
        obj2 = FuelRemains.objects.get(date=self.date2, fuel_info = self.fuel_info1)
        self.assertEquals(obj2.tonnes, 11.9)

   
class FuelConsumptionTest(TestCase):
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
        FuelConsumption.objects.all().delete()
        FuelInfo.objects.all().delete()
        User.objects.all().delete()
        BoilerHouse.objects.all().delete()
        
    def test_creation(self):
        """
        
        """
        
        info,created = FuelInfo.objects.get_or_create(boiler=self.boiler_obj,
                        creator = self.test_user,
                        type = "Coal")

        obj,created = FuelConsumption.objects.get_or_create(boiler=self.boiler_obj,
                                             date=get_test_date(),
                                             creator=self.test_user,
                                             fuel_info = info)

        obj = FuelConsumption.objects.get(fuel_info = info, date = get_test_date())
        self.assertEquals(info.id, obj.fuel_info.id)
    
    def test_setting_value(self):
        """
        Установить значения в первый день и во второй 
        """
        date1 = datetime.date(2011, 1, 1)
        date2 = datetime.date(2011, 1, 2)
        
        info,created = FuelInfo.objects.get_or_create(boiler=self.boiler_obj,
                        creator = self.test_user,
                        type = "Coal")
        
        obj = FuelConsumption(boiler=self.boiler_obj,
                             date=date1,
                             creator=self.test_user,
                             fuel_info = info)
        obj.actual_day = 5.0
        obj.plan_month = 310.0
        obj.save(save_revision=True)
        
        self.assertEqual(obj.actual_month , 5)
        self.assertEqual(obj.plan_month , 310)
        self.assertEqual(obj.plan_day , 10)
        self.assertEqual(obj.actual_day , 5)
        self.assertEqual(obj.diff_day , 5)
        self.assertEqual(obj.diff_month, -5)
        
        obj1 = FuelConsumption(boiler=self.boiler_obj,
                             date=date2,
                             creator=self.test_user,
                             fuel_info = info)
     
        obj1.actual_day = 11.0
        obj1.save()
        
        self.assertEqual(obj1.actual_month , 16)
        self.assertEqual(obj1.plan_month , 310.0)
        self.assertEqual(obj1.diff_day , 11.0 )
        self.assertEqual(obj1.diff_month, -4.0)
        self.assertEqual(obj1.actual_day , 11.0)
        self.assertEqual(obj1.plan_day , 10.0)
        
    def test_versioning(self):
        #=======================================================================
        # info = FuelInfo(boiler=self.boiler_obj,
        #                creator = self.test_user,
        #                type = "Coal")
        # 
        # info.save(save_revision=True)
        # self.assertEqual(1,len(reversion.get_for_object(info)))
        # 
        # obj = FuelConsumption(boiler=self.boiler_obj,
        #                                     date=get_test_date(),
        #                                     creator=self.test_user,
        #                                     fuel_info = info)
        # obj.save(save_revision=True)
        # 
        # self.assertEqual(1,len(reversion.get_for_object(obj)))
        #=======================================================================
        #print reversion.get_for_object(obj)[0].revision.user
        pass
    
    def test_period_update(self):
        """
        Save on first day month
        """
        date1 = datetime.date(2011, 1, 1)
        date2 = datetime.date(2011, 1, 3)
    
        info,created = FuelInfo.objects.get_or_create(boiler=self.boiler_obj,
                        creator = self.test_user,
                        type = "Coal")
        
        obj = FuelConsumption(boiler=self.boiler_obj,
                             date=date1,
                             creator=self.test_user,
                             fuel_info = info)
        obj.actual_day = 5.0
        obj.plan_month = 310.0
        obj.save(save_revision=True)
        
        self.assertEqual(obj.actual_month , 5)
        self.assertEqual(obj.plan_month , 310)
        self.assertEqual(obj.plan_day , 10)
        self.assertEqual(obj.actual_day , 5)
        self.assertEqual(obj.diff_day , 5)
        self.assertEqual(obj.diff_month, -5)
        
        obj1 = FuelConsumption(boiler=self.boiler_obj,
                             date=date2,
                             creator=self.test_user,
                             fuel_info = info)
     
        obj1.actual_day = 11.0
        obj1.real_plan_day = 1.1
        obj1.save(save_revision=True)
        
        self.assertEqual(obj1.actual_month , 16.0)
        self.assertEqual(obj1.plan_month , 310.0)
        self.assertEqual(obj1.real_plan_day, 1.1)
        self.assertEqual(obj1.real_plan_sum, 1.1)
        self.assertEqual(obj1.diff_day , 9.9)
        self.assertEqual(obj1.diff_month, -14.0)
        self.assertEqual(obj1.actual_day , 11.0)
        self.assertEqual(obj1.plan_day , 10.0)
    
        obj.plan_month = 410.0
        obj.save(save_revision=True)
        obj.update_period()
        
        self.assertEqual(obj.actual_month , 5)
        self.assertEqual(obj.plan_month , 410.0)
        self.assertEqual(obj.plan_day , 13.226)
        self.assertEqual(obj.real_plan_day, 0.0)
        self.assertEqual(obj.real_plan_sum, 0.0)
        self.assertEqual(obj.actual_day , 5)
        self.assertEqual(obj.diff_day , 5)
        self.assertEqual(obj.diff_month, -8.226)
        
        obj1 = FuelConsumption.objects.get(date=date2, fuel_info = info)
        
        self.assertEqual(obj1.actual_month , 16)
        self.assertEqual(obj1.plan_month , 410.0)
        self.assertEqual(obj1.diff_day , 9.9)
        self.assertEqual(obj1.diff_month, -23.678)
        self.assertEqual(obj1.actual_day , 11)
        self.assertEqual(obj1.plan_day , 13.226)
    
    def test_period(self):
        """
        Testing period entity processing
        """
        
        # Период с 15 января 2011 по 1 января 2012
        period1 = Period()
        period1.start = datetime.date(2011,1,15)
        period1.end = datetime.date(2012,1,1)
        period1.save()
        
        # Период с 14 мая 2011 по 10 января 2012
        period2 = Period()
        period2.start = datetime.date(2011,5,14)
        period2.end = datetime.date(2012,10,1)
        period2.save()

        self.boiler_obj.periods.add(period1)
        self.boiler_obj.periods.add(period2)
        
        info,created = FuelInfo.objects.get_or_create(boiler=self.boiler_obj,
                        creator = self.test_user,
                        type = "Coal")
        
        date1 = datetime.date(2011, 1, 20)
        obj = FuelConsumption(boiler=self.boiler_obj,
                             date=date1,
                             creator=self.test_user,
                             fuel_info = info)
        
        obj.save()
        
        #print "PERIOD " + unicode( obj.get_plan_period())
        
        # Период для 
        self.assertEqual(obj.get_plan_period(), (datetime.date(2011,1,15), datetime.date(2011,1,31), 17))

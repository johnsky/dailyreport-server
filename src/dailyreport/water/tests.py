# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from dailyreport.company_object.models import BoilerHouse, ThermalArea, Branch
import datetime
import reversion

from dailyreport.water.models import WaterConsumption, WaterConsumptionCategory 
from dailyreport.utils.date_utils import get_month_day, get_today

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

        
class WaterConsumptionTest(TestCase):
    
    CONSUMPTION_CATEGORY1_NAME = u"WATER CONSUMPTION CATEGORY1"
    CONSUMPTION_CATEGORY2_NAME = u"WATER CONSUMPTION CATEGORY2"
    
    def setUp(self):
        """
        Pre-execution
        """
        self.date1 = datetime.date(2011, 1, 1)
        self.date2 = datetime.date(2011, 1, 2)
        self.date3 = datetime.date(2011, 1, 3)
        
        self.test_user = create_test_user()
        self.boiler_obj = create_test_boiler(self.test_user)

        self.category1 = WaterConsumptionCategory.objects.create(creator=self.test_user,
                                              name = self.CONSUMPTION_CATEGORY1_NAME,
                                              boiler = self.boiler_obj)

        self.category2 = WaterConsumptionCategory.objects.create(creator=self.test_user,
                                              name = self.CONSUMPTION_CATEGORY2_NAME,
                                              boiler = self.boiler_obj)
        
    def tearDown(self):
        """
        Post-execution
        """
        WaterConsumption.objects.all().delete()
        WaterConsumptionCategory.objects.all().delete()
        User.objects.all().delete()
        BoilerHouse.objects.all().delete()
        
    def test_creation(self):
        """
        1
        """
        obj1 = WaterConsumption.objects.create(creator=self.test_user,
                                              date=self.date1,
                                              boiler=self.boiler_obj,
                                              category = self.category1)
        self.assertEqual(obj1.actual_day, 0.0)
        self.assertEqual(obj1.plan_day, 0.0)
        self.assertEqual(obj1.diff_day, 0.0)
        self.assertEqual(obj1.actual_month, 0.0)
        self.assertEqual(obj1.plan_month, 0.0)
        self.assertEqual(obj1.diff_month, 0.0)
        
        obj2 = WaterConsumption.objects.create(creator=self.test_user,
                                              date=self.date3,
                                              boiler=self.boiler_obj,
                                              category = self.category1)
        self.assertEqual(obj2.actual_day, 0.0)
        self.assertEqual(obj2.plan_day, 0.0)
        self.assertEqual(obj2.diff_day, 0.0)
        self.assertEqual(obj2.actual_month, 0.0)
        self.assertEqual(obj2.plan_month, 0.0)
        self.assertEqual(obj2.diff_month, 0.0)
        
        # Проверка создания объекта другой категории воды при том,
        # что объект на первое число не существует
        obj3 = WaterConsumption.objects.create(creator=self.test_user,
                                              date=self.date2,
                                              boiler=self.boiler_obj,
                                              category = self.category2)
        self.assertEqual(obj3.actual_day, 0.0)
        self.assertEqual(obj3.plan_day, 0.0)
        self.assertEqual(obj3.diff_day, 0.0)
        self.assertEqual(obj3.actual_month, 0.0)
        self.assertEqual(obj3.plan_month, 0.0)
        self.assertEqual(obj3.diff_month, 0.0)
        
        # Объект был создан автоматически при создании предыдущего объекта
        """try:
            obj4 = WaterConsumption.objects.get(date=self.date1, category = self.category2)
            
            self.assertEqual(obj4.actual_day, 0.0)
            self.assertEqual(obj4.plan_day, 0.0)
            self.assertEqual(obj4.diff_day, 0.0)
            self.assertEqual(obj4.actual_month, 0.0)
            self.assertEqual(obj4.plan_month, 0.0)
            self.assertEqual(obj4.diff_month, 0.0)
        except WaterConsumption.DoesNotExist:
            self.fail("First day WaterConsumption object wasn't created.")"""

    def test_setting_value(self):
        """
        
        """
        obj1, created = WaterConsumption.objects.get_or_create(creator=self.test_user,
                                                      date=self.date1,
                                                      boiler=self.boiler_obj,
                                                      category = self.category1)
        obj1.actual_day = 8.0
        obj1.plan_month = 310.0
        obj1.save()

        self.assertEqual(obj1.actual_day , 8.0)
        self.assertEqual(obj1.plan_day, 10.0)
        self.assertEqual(obj1.diff_day, -2.0)
        self.assertEqual(obj1.plan_month, 310.0)
        self.assertEqual(obj1.actual_month, 8.0)
        self.assertEqual(obj1.diff_month, -2.0)

        obj2, created = WaterConsumption.objects.get_or_create(creator = self.test_user,
                                              date = self.date3,
                                              boiler = self.boiler_obj,
                                              category = self.category1)
        
        # второй день. Расход дневной = 15, План месячный = 410
        obj2.actual_day = 15.0
        obj2.plan_month = 410.0
        obj2.save()
        
        # План месячниый несмотря на значение 410 должен быть 310, как указано в первый день
        # Тогда плановый дневной расход = 10 
        self.assertEqual(obj2.plan_month , 310.0)
        self.assertEqual(obj2.plan_day , 10.0)
        self.assertEqual(obj2.diff_day , 5.0)
        self.assertEqual(obj2.actual_day, 15.0)
        self.assertEqual(obj2.actual_month, 23.0)
        self.assertEqual(obj2.diff_month, -7.0)
    
    
    def test_versioning(self):
        """
        
        """       
        #------------------------------------- self.category1.name = "TEST NAME"
        #------------------------------ self.category1.save(save_revision=False)
#------------------------------------------------------------------------------ 
        #----------------------------- self.category1.name = "ANOTHER TEST NAME"
        #------------------------------- self.category1.save(save_revision=True)
#------------------------------------------------------------------------------ 
        #--- #self.assertEqual(1, len(reversion.get_for_object(self.category1)))
#------------------------------------------------------------------------------ 
        #--------- obj1= WaterConsumption.objects.create(creator=self.test_user,
                                                      #-------- date=self.date1,
                                                      #- boiler=self.boiler_obj,
                                                      # category = self.category1)
#------------------------------------------------------------------------------ 
        #--------------- self.assertEqual(0,len(reversion.get_for_object(obj1)))
#------------------------------------------------------------------------------ 
        #----------------------- obj2 = WaterConsumption(creator=self.test_user,
                              #-------------------------------- date=self.date1,
                              #------------------------- boiler=self.boiler_obj,
                              #---------------------- category = self.category1)
        #----------------------------------------- obj2.save(save_revision=True)
#------------------------------------------------------------------------------ 
        #-------------- self.assertEqual(1, len(reversion.get_for_object(obj2)))
        pass

    def test_period_update(self):
        """
        Save on first day month
        """
        obj1 = WaterConsumption(creator=self.test_user,
                                          date=self.date1,
                                          boiler=self.boiler_obj,
                                          category = self.category1)
        obj1.actual_day = 8.0
        obj1.plan_month = 310.0
        obj1.save(save_revision=True)
        
        self.assertEqual(obj1.actual_day, 8)
        self.assertEqual(obj1.plan_day, 10)
        self.assertEqual(obj1.diff_day , -2)
        self.assertEqual(obj1.actual_month, 8)
        self.assertEqual(obj1.plan_month , 310)
        self.assertEqual(obj1.diff_month, -2)

        obj2 = WaterConsumption(creator = self.test_user,
                                          date = self.date3,
                                          boiler = self.boiler_obj,
                                          category = self.category1)
        
        # второй день. Расход дневной = 15, План месячный = 410
        obj2.actual_day = 15.0
        obj2.plan_month = 410.0
        obj2.save(save_revision=True)
        
        # План месячниый несмотря на значение 410 должен быть 310, как указано в первый день
        # Тогда плановый дневной расход = 10 
        self.assertEqual(obj2.actual_day, 15)
        self.assertEqual(obj2.plan_day, 10)
        self.assertEqual(obj2.diff_day, 5)
        self.assertEqual(obj2.plan_month, 310)
        self.assertEqual(obj2.actual_month, 23)
        self.assertEqual(obj2.diff_month, -7)

        # изменяем мсячный план
        obj1.plan_month = 520.0
        obj1.save(save_revision=True)
        
        self.assertEqual(obj1.actual_day, 8)
        self.assertEqual(obj1.plan_day, 16.774)
        self.assertEqual(obj1.diff_day , -8.774)
        self.assertEqual(obj1.actual_month, 8.0)
        self.assertEqual(obj1.plan_month , 520)
        self.assertEqual(obj1.diff_month, -8.774)
        
        obj1.update_period()
        
        obj2 = WaterConsumption.objects.get(date = self.date3,
                                          category = self.category1)
        # Плановое значение должно измениться, а вместе с ним и другие значения
        self.assertEqual(obj2.actual_day, 15.0)
        self.assertEqual(obj2.plan_day, 16.774)
        self.assertEqual(obj2.diff_day, -1.774)
        self.assertEqual(obj2.plan_month, 520.0)
        self.assertEqual(obj2.actual_month, 23)
        self.assertEqual(obj2.diff_month, -27.322)
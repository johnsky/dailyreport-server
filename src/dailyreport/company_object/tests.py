# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
from dailyreport.company_object.models import Branch, ThermalArea, BoilerHouse,BoilerBookmark

class BranchTest(TestCase):
    """
    Тестирование филиала
    """
    def setUp(self):
        """
        Pre-execution
        """
        # test users
        self.test_user = User.objects.create_user('test', 'test@test.com', '123')
        self.test_user.is_staff = True
        self.test_user.save()
    
    def tearDown(self):
        """
        Post-execution
        """
        self.test_user.delete()
        
    def test_creation(self):
        self.branch_obj = Branch.objects.create(name = u"Филиал",
                                                creator = self.test_user)
        
        self.assertEqual(self.branch_obj.name, u"Филиал")
        self.branch_obj.delete()


class ThermalAreaTest(TestCase):
    """
    Тестирование теплового узла
    """
    def setUp(self):
        """
        Pre-execution
        """
        # test users
        self.test_user = User.objects.create_user('test', 'test@test.com', '123')
        self.test_user.is_staff = True
        self.test_user.save()
    
        self.branch_obj = Branch.objects.create(name = u"Филиал",
                                                creator = self.test_user)
    def tearDown(self):
        """
        Post-execution
        """
        self.branch_obj.delete()
        self.test_user.delete()
        
    def test_creation(self):
        
        #Enterprise structure objects
        self.thermal_area_obj = ThermalArea.objects.create(name = u"Тепловой район",
                                                            branch = self.branch_obj,
                                                            creator = self.test_user)
        self.assertEqual(self.thermal_area_obj.name, u"Тепловой район")
        self.thermal_area_obj.delete()
        
        
class BoilerHouseTest(TestCase):
    """
    Тесты для объекта котельной
    """
    def setUp(self):
        """
        Pre-execution
        """
        # test users
        self.test_user = User.objects.create_user('test', 'test@test.com', '123')
        self.test_user.is_staff = True
        self.test_user.save()
    
        self.branch_obj = Branch.objects.create(name = u"Филиал",
                                                creator = self.test_user)
        self.thermal_area_obj = ThermalArea.objects.create(name = u"Тепловой район",
                                           branch = self.branch_obj,
                                           creator = self.test_user)

    def tearDown(self):
        """
        Post-execution
        """
        self.thermal_area_obj.delete()
        self.branch_obj.delete()
        self.test_user.delete()
        
    def test_creation(self):
        self.boiler = BoilerHouse.objects.create(name = u"Котельная",
                                creator = self.test_user, 
                                thermalArea = self.thermal_area_obj,
                                branch = self.branch_obj)
        
        self.assertEqual(self.boiler.name, u"Котельная")
        self.boiler.delete()
        
class BoilerBookmarkTest(TestCase):
    def setUp(self):
        """
        Pre-execution
        """
        # test users
        self.test_user = User.objects.create_user('test', 'test@test.com', '123')
        self.test_user.is_staff = True
        self.test_user.save()
    
        self.branch_obj = Branch.objects.create(name = u"Филиал",
                                                creator = self.test_user)
        self.thermal_area_obj = ThermalArea.objects.create(name = u"Тепловой район",
                                           branch = self.branch_obj,
                                           creator = self.test_user)
        self.boiler_obj = BoilerHouse.objects.create(name = u"Котельная",
                                creator = self.test_user, 
                                thermalArea = self.thermal_area_obj,
                                branch = self.branch_obj)
    def tearDown(self):
        """
        Post-execution
        """
        self.boiler_obj.delete()
        self.thermal_area_obj.delete()
        self.branch_obj.delete()
        self.test_user.delete()
        
    def test_creation(self):
        bookmark = BoilerBookmark.objects.create(name=u"Закладка",
                            creator = self.test_user)
        bookmark.boiler.add(self.boiler_obj)
        
        self.assertIsNotNone(bookmark.id)
        
        obj = BoilerBookmark.objects.get(id=bookmark.id)
        self.assertEqual(obj.name, u"Закладка")
        bookmark.delete()
    
    def test_serialization(self):
        
        from django.core import serializers
        result = serializers.serialize('json', BoilerHouse.objects.all(), relations=('branch',))
        print result
        self.assertEqual('pk' in unicode(result), True)

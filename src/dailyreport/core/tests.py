# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
from dailyreport.core.models import HistoryModel 
from django.db.models import CharField
        
class HistoryModelTest(TestCase):

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
        Post-execution
        """
        self.test_user.delete()
        
    def test_object_creation(self):
        """
        Создание объекта
        """
        obj = HistoryModel()
        self.assertIsNotNone(obj)
        

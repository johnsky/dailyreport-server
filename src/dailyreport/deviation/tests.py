# -*- coding: utf-8 -*-

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from dailyreport.deviation.models import ParameterDeviationProblem ,\
    ParameterDeviationProblemState, ParameterDeviationProblemCause,\
    ParameterDeviationProblemComment, DeviationConcerned, DeviationResponcible
from dailyreport.utils.date_utils import current_day, get_today
from dailyreport.fuel.models import FuelConsumption, FuelInfo
from dailyreport.deviation.utils import create_problem, look_for_problems,\
    look_for_problems_query, close_problem
from dailyreport.company_object.models import Branch, ThermalArea, BoilerHouse,\
    Resource



 
class ParameterDeviationProblemTest(TestCase):
    
    def create_test_boiler(self,user): 
        #Enterprise structure objects
        self.branch_obj = Branch.objects.create(name = u"Филиал",
                                          creator = user)
        
        self.thermal_area_obj = ThermalArea.objects.create(name = u"Тепловой район",
                                            branch = self.branch_obj,
                                            creator = user)
    
    
        self.boiler_obj = BoilerHouse.objects.create(name=u"Котельная",
                                            thermalArea = self.thermal_area_obj,
                                            branch = self.branch_obj,
                                            address = u"Адрес котельной",
                                            creator = user)
    
    def setUp(self):
        self.state_open = ParameterDeviationProblemState.objects.create(name=settings.DEVIATION_PROBLEM_STATE_OPEN)
        self.state_closed = ParameterDeviationProblemState.objects.create(name=settings.DEVIATION_PROBLEM_STATE_CLOSED)
        
        self.human_cause = ParameterDeviationProblemCause.objects.create(name = 'Человеческий фактор', description='')
        self.wreck_cause = ParameterDeviationProblemCause.objects.create(name = 'Поломка', description='')
        
        # TEST USERS
        self.test_user = User.objects.create_user('test', 'test@test.com', '123')
        self.admin_user = User.objects.create_user('admin', settings.MANAGERS[0][1],'123')
        self.concerned1 = User.objects.create_user('concerned1', 'test@test.com', '123')
        self.concerned2 = User.objects.create_user('concerned2', 'test@test.com', '123')
        self.responsible1 = User.objects.create_user('responsible1', 'test@test.com', '123')
        self.responsible2 = User.objects.create_user('responsible2', 'test@test.com', '123')
        
        self.create_test_boiler(self.test_user)
        
        self.deviation_concerned1 = DeviationConcerned.objects.create(concerned = self.concerned1)
        self.deviation_concerned2 = DeviationConcerned.objects.create(concerned = self.concerned2)
        self.deviation_responcible1 = DeviationResponcible.objects.create(branch = self.branch_obj, responcible = self.responsible1)
        self.deviation_responcible2 = DeviationResponcible.objects.create(branch = self.branch_obj, responcible = self.responsible2)
        
        obj,created = Resource.objects.get_or_create(name=settings.RESOURCE_TYPE_WATER)
        obj,created = Resource.objects.get_or_create(name=settings.RESOURCE_TYPE_ELECTRICITY)
        obj,created = Resource.objects.get_or_create(name=settings.RESOURCE_TYPE_FUEL)
        
        
    def tearDown(self):
        ParameterDeviationProblemState.objects.all().delete()
        ParameterDeviationProblemCause.objects.all().delete()
        ParameterDeviationProblemComment.objects.all().delete()

        User.objects.all().delete()
        
    def test_creation(self):
        """
        Создание проблемы при возникновении отклонения.
        При заведении новой проблемы:
         - запись находится в статусе "Новая".
         - не указывается тип проблемы
         - указан список ответственных
         - указан список заинтересованных
         - указана дата возникновения проблемы
         - указан ресурс, параметр по которому отклоение превысило ожидаемый порог  
        """
        
        # TEST UTILITY METHOD
        info = FuelInfo.objects.create(boiler=self.boiler_obj,
                        creator = self.test_user,
                        type = settings.FUEL_TYPE_NAMES[0])
        consumption = FuelConsumption.objects.create(boiler=self.boiler_obj,
                                     date=get_today(),
                                     creator=self.test_user,
                                     fuel_info = info)
        
        problem1 = create_problem(consumption)
        
        self.assertNotEqual(problem1, None)
        
        
        
    def test_closing_problem(self):
        """
        Закрытие проблемы.
        """
        # TEST UTILITY METHOD
        info = FuelInfo.objects.create(boiler=self.boiler_obj,
                        creator = self.test_user,
                        type = settings.FUEL_TYPE_NAMES[0])
        consumption = FuelConsumption.objects.create(boiler=self.boiler_obj,
                                     date=get_today(),
                                     creator=self.test_user,
                                     fuel_info = info)
        
        problem = create_problem(consumption)
        close_problem(self.test_user, problem)
        problem = ParameterDeviationProblem.objects.get(id = problem.id) 
        self.assertEqual(problem.state, self.state_closed)
        
    
    def test_commenting_problem(self):
        """
        Комментирование проблемы.
        """
        # TEST UTILITY METHOD
        info = FuelInfo.objects.create(boiler=self.boiler_obj,
                        creator = self.test_user,
                        type = settings.FUEL_TYPE_NAMES[0])
        consumption = FuelConsumption.objects.create(boiler=self.boiler_obj,
                                     date=get_today(),
                                     creator=self.test_user,
                                     fuel_info = info)
        
        problem = create_problem(consumption)
        
        # Add comment
        comment1 = ParameterDeviationProblemComment.objects.create(author = self.responsible1,
                                                                   date = get_today(),
                                                                   text = u"Test comment!",
                                                                   deviation = problem)
        problem = ParameterDeviationProblem.objects.get(id = problem.id)
        
        # Два комментария с учетом комментария созданного при создании записи
        self.assertEqual(problem.comments.all().count(), 2)
        
        # Add another one comment
        comment2 = ParameterDeviationProblemComment.objects.create(author = self.concerned1,
                                                                   date = get_today(),
                                                                   text = u"Accept test comment!",
                                                                   deviation = problem)
        
        #problem = ParameterDeviationProblem.objects.get(id = problem.id)
        self.assertEqual(problem.comments.all().count(), 3)
        
        from django.core import serializers
        query_set = ParameterDeviationProblem.objects.all()
        result = serializers.serialize('json', query_set, indent=2, relations=('boiler','resource','state','cause','responsible'))
        print result
        #self.assertEqual('pk' in unicode(result), True)
    
        
        
    def test_look_for_problem(self):
        """"""
        problems = look_for_problems_query(self.test_user, [], [], None, None, None, None)
        
        self.assertEqual(list(problems), [])
        
        # create a problem
        info = FuelInfo.objects.create(boiler=self.boiler_obj,
                        creator = self.test_user,
                        type = settings.FUEL_TYPE_NAMES[0])
        consumption = FuelConsumption.objects.create(boiler=self.boiler_obj,
                                     date=get_today(),
                                     creator=self.test_user,
                                     fuel_info = info)
        
        problem = create_problem(consumption)
        
        self.assertNotEqual(problem, None)
        
        problems = look_for_problems_query(self.test_user, [], [], None, None, None, None)
        
        self.assertEqual(problems[0], problem)
        
        

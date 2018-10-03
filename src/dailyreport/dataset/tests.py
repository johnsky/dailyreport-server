# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.conf import settings

from dailyreport.company_object.models import Branch,BoilerHouse, ThermalArea
import calendar
from dailyreport.dataset.models import DatasetField, Dataset, get_entity
from dailyreport.dataset.utils import get_model_fields, get_models_content_types ,\
    get_datasets, get_dataset_rows_number, get_fields, get_data
from dailyreport.user_profile.models import UserProfile
from dailyreport.utils.date_utils import get_month_range, get_today, current_year,current_month

from permissions.utils import register_permission, unregister_permission,\
    grant_permission, has_permission, add_role
from permissions.utils import register_role, get_roles, unregister_role
from permissions.models import Role
from dailyreport.fuel.models import FuelInfo
from dailyreport.water.models import WaterConsumptionCategory


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
        
        # Удаляем все поля + все разрешения для полей 
        DatasetField.objects.all().delete()
        BoilerHouse.objects.all().delete()
    
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
        """
        Тест создания объекта
        """
        self.create_boiler()
        model_class = ContentType.objects.get(model='electricityconsumption').model_class()
        obj = get_entity(self.test_user, get_today(), model_class, self.boiler_obj, None, None)
        self.assertNotEquals(obj, None)

class DatasetFieldTest(TestCase):
    def setUp(self):
        """
        Pre-execution
        """
        # test users
        self.test_admin = User.objects.create_user('admin', 'admin@test.com', '123')
        self.test_manager = User.objects.create_user('manager', 'manager@test.com', '123')
        self.test_viewer = User.objects.create_user('viewer', 'viewer@test.com', '123')
        self.test_editor = User.objects.create_user('editor', 'editor@test.com', '123')
        self.test_developer = User.objects.create_user('developer', 'developer@test.com', '123')

        #PERMISSIONS
        register_permission(settings.PERMISSION_VIEW_NAME, settings.PERMISSION_VIEW_NAME)
        register_permission(settings.PERMISSION_EDIT_NAME, settings.PERMISSION_EDIT_NAME)
        register_permission(settings.PERMISSION_CREATE_NAME, settings.PERMISSION_CREATE_NAME)
        register_permission(settings.PERMISSION_DELETE_NAME, settings.PERMISSION_DELETE_NAME)
        
        # ROLES
        register_role(settings.ROLE_DEVELOPER_NAME)
        register_role(settings.ROLE_ADMIN_NAME)
        register_role(settings.ROLE_MANAGER_NAME)
        register_role(settings.ROLE_EDITOR_NAME)
        register_role(settings.ROLE_VIEWER_NAME)

        # ASSIGN ROlES        
        add_role(self.test_editor, Role.objects.get(name = settings.ROLE_EDITOR_NAME))
        add_role(self.test_viewer, Role.objects.get(name = settings.ROLE_VIEWER_NAME))
        add_role(self.test_admin, Role.objects.get(name = settings.ROLE_ADMIN_NAME))
        add_role(self.test_manager, Role.objects.get(name = settings.ROLE_MANAGER_NAME))
        add_role(self.test_developer, Role.objects.get(name = settings.ROLE_DEVELOPER_NAME))

    def tearDown(self):
        """
        A test Post-execution
        """

        #Удаляем всех пользователей
        User.objects.all().delete()
        
        # Удаляем все поля + все разрешения для полей 
        DatasetField.objects.all().delete()
        
        # Unregister all roles
        unregister_role(settings.ROLE_DEVELOPER_NAME)
        unregister_role(settings.ROLE_ADMIN_NAME)
        unregister_role(settings.ROLE_MANAGER_NAME)
        unregister_role(settings.ROLE_EDITOR_NAME)
        unregister_role(settings.ROLE_VIEWER_NAME)
        
        # Unregister all permissions
        unregister_permission( settings.PERMISSION_VIEW_NAME)
        unregister_permission( settings.PERMISSION_EDIT_NAME)
        unregister_permission( settings.PERMISSION_CREATE_NAME)
        unregister_permission( settings.PERMISSION_DELETE_NAME)
       
    def test_available_content_types(self):
        # доступные типы контента
        cts = get_models_content_types()
        
        ct = ContentType.objects.get(model='fuelconsumption',
                                        app_label='fuel')
        self.assertIn(ct, cts)
 
    def test_creation(self):
        """
        Проверка создания объекта поля.
        Создавать объекты могут только пользователи роль которых РАЗРАБОТЧИК, АДМИН, МЕНЕДЖЕР
        При создании у пользователя есть все права: редактировать, просматривать.
        
        
        """
        sources =get_models_content_types()
        field = get_model_fields(sources[0])[0]

        obj = DatasetField(creator = self.test_admin,
                         model_field_name = field.name,
                         model_content_type = sources[0])
        
        obj.save(save_revision=True)
        
        self.assertEquals(obj.name, "")
        self.assertEquals(obj.description, "")
        self.assertEquals(obj.internal_name, "")
        
        # Администратор, разработчик и менеджер имеют все права (Правка, просмотр, удаление)
        self.assertEqual(has_permission(obj, self.test_admin, settings.PERMISSION_VIEW_NAME), True)
        self.assertEqual(has_permission(obj, self.test_developer, settings.PERMISSION_VIEW_NAME), True)
        self.assertEqual(has_permission(obj, self.test_manager, settings.PERMISSION_VIEW_NAME), True)
        self.assertEqual(has_permission(obj, self.test_viewer, settings.PERMISSION_VIEW_NAME), False)
        self.assertEqual(has_permission(obj, self.test_editor, settings.PERMISSION_VIEW_NAME), False)
        
        self.assertEqual(has_permission(obj, self.test_admin, settings.PERMISSION_DELETE_NAME), True)
        self.assertEqual(has_permission(obj, self.test_developer, settings.PERMISSION_DELETE_NAME), True)
        self.assertEqual(has_permission(obj, self.test_manager, settings.PERMISSION_DELETE_NAME), True)
        self.assertEqual(has_permission(obj, self.test_viewer, settings.PERMISSION_DELETE_NAME), False)
        self.assertEqual(has_permission(obj, self.test_editor, settings.PERMISSION_DELETE_NAME), False)
        
        self.assertEqual(has_permission(obj, self.test_admin, settings.PERMISSION_EDIT_NAME), True)
        self.assertEqual(has_permission(obj, self.test_developer, settings.PERMISSION_EDIT_NAME), True)
        self.assertEqual(has_permission(obj, self.test_manager, settings.PERMISSION_EDIT_NAME), True)
        self.assertEqual(has_permission(obj, self.test_viewer, settings.PERMISSION_EDIT_NAME), False)
        self.assertEqual(has_permission(obj, self.test_editor, settings.PERMISSION_EDIT_NAME), False)
        
    def test_getting_source_fields_meta(self):
        """
        Проверка доступных для создания отчета полей 
        """
        content_types = get_models_content_types()
        field_names = get_model_fields(content_types[1])
        
        #
        field1 = DatasetField.objects.create(creator = self.test_admin,
                                         model_field_name = field_names[0],
                                         model_content_type = content_types[0])
        #
        field2 = DatasetField.objects.create(creator = self.test_admin,
                                         model_field_name = field_names[1],
                                         model_content_type = content_types[0])
        
        self.assertNotEquals(field1.id, 0)
        self.assertNotEquals(field2.id, 0)
        
    def test_permission_checking(self):
        # тип данных
        source_ct = ContentType.objects.get(model='fuelconsumption',
                                     app_label='fuel')
        
        # поле доступное для отчета из типа данных
        source_field = source_ct.model_class().DescriptorMeta.fields[0]
        
        field = DatasetField.objects.create(creator = self.test_admin,
                                         model_field_name = source_field,
                                         model_content_type = source_ct)
        
        grant_permission(field, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_EDIT_NAME)
        grant_permission(field, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        grant_permission(field, Role.objects.get(name=settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        self.assertEqual(has_permission(field, self.test_viewer,
                        settings.PERMISSION_VIEW_NAME), True)
        self.assertEqual(has_permission(field, self.test_viewer,
                        settings.PERMISSION_EDIT_NAME), False)
        
        self.assertEqual(has_permission(field, self.test_editor,
                        settings.PERMISSION_VIEW_NAME), True)
        self.assertEqual(has_permission(field, self.test_editor,
                        settings.PERMISSION_EDIT_NAME), True)
        
class DataSetTest(TestCase):
    
    def setUp(self):
        """
        Pre-execution
        """
        # test users
        self.test_admin = User.objects.create_user('admin', 'admin@test.com', '123')
        self.test_manager = User.objects.create_user('manager', 'manager@test.com', '123')
        self.test_viewer = User.objects.create_user('viewer', 'viewer@test.com', '123')
        self.test_editor = User.objects.create_user('editor', 'editor@test.com', '123')
        self.test_developer = User.objects.create_user('developer', 'developer@test.com', '123')

        #PERMISSIONS
        register_permission(settings.PERMISSION_VIEW_NAME, settings.PERMISSION_VIEW_NAME)
        register_permission(settings.PERMISSION_EDIT_NAME, settings.PERMISSION_EDIT_NAME)
        register_permission(settings.PERMISSION_CREATE_NAME, settings.PERMISSION_CREATE_NAME)
        register_permission(settings.PERMISSION_DELETE_NAME, settings.PERMISSION_DELETE_NAME)
        
        # ROLES
        register_role(settings.ROLE_DEVELOPER_NAME)
        register_role(settings.ROLE_ADMIN_NAME)
        register_role(settings.ROLE_MANAGER_NAME)
        register_role(settings.ROLE_EDITOR_NAME)
        register_role(settings.ROLE_VIEWER_NAME)

        # ASSIGN ROlES        
        add_role(self.test_editor, Role.objects.get(name = settings.ROLE_EDITOR_NAME))
        add_role(self.test_viewer, Role.objects.get(name = settings.ROLE_VIEWER_NAME))
        add_role(self.test_admin, Role.objects.get(name = settings.ROLE_ADMIN_NAME))
        add_role(self.test_manager, Role.objects.get(name = settings.ROLE_MANAGER_NAME))
        add_role(self.test_developer, Role.objects.get(name = settings.ROLE_DEVELOPER_NAME))

    def tearDown(self):
        """
        Post-execution
        """
        #Удаляем всех пользователей
        User.objects.all().delete()
        
        FuelInfo.objects.all().delete()
        WaterConsumptionCategory.objects.all().delete()
        BoilerHouse.objects.all().delete()
        
        # Удаляем все поля + разрешения (по умолчанию 
        # django каскадно удаляет все зависимые объекты)
        DatasetField.objects.all().delete()
        
        # Удаляем все отчеты + разрешения(по умолчанию 
        # django каскадно удаляет все зависимые объекты)
        Dataset.objects.all().delete()
        
        # Unregister all roles
        unregister_role(settings.ROLE_DEVELOPER_NAME)
        unregister_role(settings.ROLE_ADMIN_NAME)
        unregister_role(settings.ROLE_MANAGER_NAME)
        unregister_role(settings.ROLE_EDITOR_NAME)
        unregister_role(settings.ROLE_VIEWER_NAME)
        
        # Unregister all permissions
        unregister_permission( settings.PERMISSION_VIEW_NAME)
        unregister_permission( settings.PERMISSION_EDIT_NAME)
        unregister_permission( settings.PERMISSION_CREATE_NAME)
        unregister_permission( settings.PERMISSION_DELETE_NAME)
        
    def create_boiler(self):
        
        self.branch_obj = Branch.objects.create(name = u"Филиал",
                                                creator = self.test_admin)
        self.thermal_area_obj = ThermalArea.objects.create(name = u"Тепловой район",
                                           branch = self.branch_obj,
                                           creator = self.test_admin)
        self.boiler_obj = BoilerHouse.objects.create(name = u"Котельная",
                                creator = self.test_admin, 
                                thermalArea = self.thermal_area_obj,
                                branch = self.branch_obj)
        
        self.fuel_info =FuelInfo.objects.create(boiler=self.boiler_obj,
                        creator = self.test_admin,
                        type = u"Coal")

        self.water_category = WaterConsumptionCategory.objects.create(creator=self.test_admin,
                                              name = u"ГВС",
                                              boiler = self.boiler_obj)
        
    def test_creation(self):
        """
        Проверка создания объекта
        """
        obj = Dataset.objects.create(creator = self.test_admin,
                                         name=u"Название отчета",
                                         description=u"Описание отчета")

        # Администратор, разработчик и менеджер имеют все права (Правка, просмотр, удаление)
        self.assertEqual(has_permission(obj, self.test_admin, settings.PERMISSION_VIEW_NAME), True)
        self.assertEqual(has_permission(obj, self.test_developer, settings.PERMISSION_VIEW_NAME), True)
        self.assertEqual(has_permission(obj, self.test_manager, settings.PERMISSION_VIEW_NAME), True)
        self.assertEqual(has_permission(obj, self.test_viewer, settings.PERMISSION_VIEW_NAME), False)
        self.assertEqual(has_permission(obj, self.test_editor, settings.PERMISSION_VIEW_NAME), False)
        
        self.assertEqual(has_permission(obj, self.test_admin, settings.PERMISSION_DELETE_NAME), True)
        self.assertEqual(has_permission(obj, self.test_developer, settings.PERMISSION_DELETE_NAME), True)
        self.assertEqual(has_permission(obj, self.test_manager, settings.PERMISSION_DELETE_NAME), True)
        self.assertEqual(has_permission(obj, self.test_viewer, settings.PERMISSION_DELETE_NAME), False)
        self.assertEqual(has_permission(obj, self.test_editor, settings.PERMISSION_DELETE_NAME), False)
        
        self.assertEqual(has_permission(obj, self.test_admin, settings.PERMISSION_EDIT_NAME), True)
        self.assertEqual(has_permission(obj, self.test_developer, settings.PERMISSION_EDIT_NAME), True)
        self.assertEqual(has_permission(obj, self.test_manager, settings.PERMISSION_EDIT_NAME), True)
        self.assertEqual(has_permission(obj, self.test_viewer, settings.PERMISSION_EDIT_NAME), False)
        self.assertEqual(has_permission(obj, self.test_editor, settings.PERMISSION_EDIT_NAME), False)
    
    def test_permission_checking(self):
        """
        Проверка установки разрешений для датасета
        """
        dataset = Dataset.objects.create(creator = self.test_admin,
                                        name=u"Название отчета",
                                        description=u"Описание отчета")
        
        grant_permission(dataset, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_EDIT_NAME)
        grant_permission(dataset, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_VIEW_NAME)
        grant_permission(dataset, Role.objects.get(name=settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        self.assertEqual(has_permission(dataset, self.test_viewer,
                                        settings.PERMISSION_VIEW_NAME), True)
        self.assertEqual(has_permission(dataset, self.test_viewer,
                                        settings.PERMISSION_EDIT_NAME), False)
        
        self.assertEqual(has_permission(dataset, self.test_editor,
                                        settings.PERMISSION_VIEW_NAME), True)
        self.assertEqual(has_permission(dataset, self.test_editor,
                                        settings.PERMISSION_EDIT_NAME), True)
        
    def test_new_field_addition(self):
        """
        Проверка добавления поля в отчет
        """
        dataset = Dataset.objects.create(creator = self.test_admin,
                                         name=u"Название отчета",
                                         description=u"Описание отчета")
        
        # Добавить поле зависящее от категории расхода воды
        field_water = DatasetField()
        field_water.creator = self.test_admin
        field_water.model_content_type = ContentType.objects.get(model='waterconsumption')
        field_water.model_field_name = 'actual_day'
        field_water.name ='Фактический расход'
        field_water.description = "Фактический расход воды"
        field_water.save()
        
        field_water.dataset_set.add(dataset)
        
        self.assertEqual(field_water.dataset_set.filter(id=dataset.id).count(), 1)
        
    def test_available_datasets_for_user(self):
        """
        """
        # отчет новый
        dataset = Dataset.objects.create(creator = self.test_admin, name=u"Название отчета",
                               description=u"Описание отчета")
        
        grant_permission(dataset, Role.objects.get(name = settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        datasets = get_datasets(self.test_viewer)
        
        self.assertEqual(datasets[0].name, u"Название отчета")
        self.assertEqual(len(datasets), 1)
        self.assertEqual(len(datasets[0].fields.all()), 0 )

    def test_rows_number(self):
        """
        Проверка рассчета количества строк в наборе данных.
        """
        self.create_boiler()
        date_range = get_month_range(2011, 1)
        
        dataset = Dataset.objects.create(creator = self.test_admin,
                                         name = u"Название отчета",
                                         description = u"Описание отчета")
        
        grant_permission(dataset, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_EDIT_NAME)
        
        # Добавить поле, которое не зависит от категорий расхода топлива и воды
        field = DatasetField()
        field.creator = self.test_admin
        field.model_content_type = ContentType.objects.get(model='electricityconsumption')
        field.model_field_name = 'actual_day'
        field.name ='Фактический расход электричества'
        field.description = "Фактический расход"
        field.save()
        
        field.dataset_set.add(dataset)
        
        grant_permission(field, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_EDIT_NAME)
        grant_permission(field, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        # Проверяем, что количество строк в наборе данных будет равно 31, т.к. поле не 
        # зависит от категории расхода воды и электричества.
        # Только пользователь выполняющий роль редактора может увидеть поля.
        rows_num = get_dataset_rows_number(dataset, self.test_viewer, date_range, [self.boiler_obj]) 
        self.assertEqual(rows_num, 0)
        
        rows_num = get_dataset_rows_number(dataset, self.test_editor, date_range, [self.boiler_obj])
        self.assertEqual(rows_num, 31)
        
        # Добавить поле зависящее от категории расхода воды
        field_water = DatasetField()
        field_water.creator = self.test_admin
        field_water.model_content_type = ContentType.objects.get(model='waterconsumption')
        field_water.model_field_name = 'actual_day'
        field_water.name ='Фактический расход'
        field_water.description = "Фактический расход воды"
        field_water.save()
        
        field_water.dataset_set.add(dataset)
        
        grant_permission(field_water, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_EDIT_NAME)
        grant_permission(field_water, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        # Проверяем, что количество строк в наборе данных будет равно 31, т.к. поле не 
        # зависит от категории расхода воды и электричества.
        # Только пользователь выполняющий роль редактора может увидеть поля.
        rows_num = get_dataset_rows_number(dataset, self.test_viewer, date_range, [self.boiler_obj]) 
        self.assertEqual(rows_num, 0)
        
        rows_num = get_dataset_rows_number(dataset, self.test_editor, date_range, [self.boiler_obj])
        self.assertEqual(rows_num, 31)
        
        field_fuel = DatasetField()
        field_fuel.creator = self.test_admin
        field_fuel.model_content_type = ContentType.objects.get(model='fuelconsumption')
        field_fuel.model_field_name = 'actual_day'
        field_fuel.name ='Фактический расход топлива'
        field_fuel.description = "Фактический расход топлива в сутки"
        field_fuel.save()
        
        field_fuel.dataset_set.add(dataset)
        
        grant_permission(field_fuel, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_EDIT_NAME)
        grant_permission(field_fuel, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        # Проверяем, что количество строк в наборе данных будет равно 31, т.к. поле не 
        # зависит от категории расхода воды и электричества.
        # Только пользователь выполняющий роль редактора может увидеть поля.
        rows_num = get_dataset_rows_number(dataset, self.test_viewer, date_range, [self.boiler_obj]) 
        self.assertEqual(rows_num, 0)
        
        rows_num = get_dataset_rows_number(dataset, self.test_editor, date_range, [self.boiler_obj])
        self.assertEqual(rows_num, 62)
        
    def test_get_report_header(self):
        """
        Проверка получения метаданных полей набора данных.
        """
        dataset = Dataset.objects.create(creator = self.test_admin,
                                         name = u"Название отчета",
                                         description = u"Описание отчета")
        
        grant_permission(dataset, Role.objects.get(name=settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        # Добавить поле, которое не зависит от категорий расхода топлива и воды
        field = DatasetField()
        field.creator = self.test_admin
        field.model_content_type = ContentType.objects.get(model='electricityconsumption')
        field.model_field_name = 'actual_day'
        field.name =u'Фактический расход электричества'
        field.description = u"Фактический расход"
        field.save()
        
        field.dataset_set.add(dataset)
        
        grant_permission(field, Role.objects.get(name=settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_VIEW_NAME)

        meta = get_fields(dataset,self.test_viewer)
        # ID, Котельная, Дата, Расход электричества
        self.assertEqual(len(meta), 4)
        
        # Добавить поле зависящее от категории расхода воды
        # Проверить, что соответствующие мета данные генерируются для нового набора полей
        field_water = DatasetField()
        field_water.creator = self.test_admin
        field_water.model_content_type = ContentType.objects.get(model='waterconsumption')
        field_water.model_field_name = 'actual_day'
        field_water.name =u'Фактический расход'
        field_water.description = u"Фактический расход воды"
        field_water.save()
        
        field_water.dataset_set.add(dataset)
        
        grant_permission(field_water, Role.objects.get(name=settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        meta = get_fields(dataset, self.test_viewer)
        # ID, Котельная, Дата, WID, Категория, Расход воды, Расход электричества
        self.assertEqual(len(meta), 7)
        
        # Добавить поле зависящее от информации о топливе
        # Проверить что добавилось поле и информация о топливе
        field_fuel = DatasetField()
        field_fuel.creator = self.test_admin
        field_fuel.model_content_type = ContentType.objects.get(model='fuelconsumption')
        field_fuel.model_field_name = 'actual_day'
        field_fuel.name = u'Фактический расход топлива'
        field_fuel.description = u"Фактический расход топлива в сутки"
        field_fuel.save()
        
        field_fuel.dataset_set.add(dataset)
        
        grant_permission(field_fuel, Role.objects.get(name=settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_EDIT_NAME)
        grant_permission(field_fuel, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        meta = get_fields(dataset, self.test_viewer)
        # ID, Котельная, Дата, WID, Категория, FID, Вид топлива, Расход воды, Расход электричества, Расход топлива
        self.assertEqual(len(meta), 10)
        
        self.assertEqual(meta[0]['name'], u'ID')
        self.assertEqual(meta[1]['name'], u'Дата')
        self.assertEqual(meta[2]['name'], u'Котельная')
        self.assertEqual(meta[3]['name'], u'WID')
        self.assertEqual(meta[4]['name'], u'Категория расхода воды')
        self.assertEqual(meta[5]['name'], u'FID')
        self.assertEqual(meta[6]['name'], u'Вид топлива')
        self.assertEqual(meta[7]['name'], u'Фактический расход электричества')
        self.assertEqual(meta[8]['name'], u'Фактический расход')
        self.assertEqual(meta[9]['name'], u'Фактический расход топлива')
        
        # Изменяем порядок колонок
        field_fuel.index = 1
        field_fuel.save()
        field_water.index = 2
        field_water.save()
        
        meta = get_fields(dataset, self.test_viewer)
        
        self.assertEqual(meta[0]['name'], u'ID')
        self.assertEqual(meta[1]['name'], u'Дата')
        self.assertEqual(meta[2]['name'], u'Котельная')
        self.assertEqual(meta[3]['name'], u'WID')
        self.assertEqual(meta[4]['name'], u'Категория расхода воды')
        self.assertEqual(meta[5]['name'], u'FID')
        self.assertEqual(meta[6]['name'], u'Вид топлива')
        self.assertEqual(meta[7]['name'], u'Фактический расход электричества')
        self.assertEqual(meta[8]['name'], u'Фактический расход топлива')
        self.assertEqual(meta[9]['name'], u'Фактический расход')

    def test_load_report_data(self):
        self.create_boiler()

        # диапазон дат для которых нужно загрузить данные по отчету
        date_range = [get_today(), get_today()]
        
        # отчет новый
        dataset = Dataset.objects.create(creator = self.test_admin,
                                         name=u"Название отчета",
                                         description=u"Описание отчета")
        
        grant_permission(dataset, Role.objects.get(name=settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        # Добавить поле, которое не зависит от категорий расхода топлива и воды
        field = DatasetField()
        field.creator = self.test_admin
        field.model_content_type = ContentType.objects.get(model='electricityconsumption')
        field.model_field_name = 'actual_day'
        field.name ='Фактический расход электричества'
        field.description = "Фактический расход"
        field.save()
        
        grant_permission(field, Role.objects.get(name=settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        field.dataset_set.add(dataset)

        # Должны быть данные для полей: ID, Дата, Наименование котельной, Раход электричества.
        dataset_data = get_data(dataset, self.test_admin, date_range, [self.boiler_obj])
        self.assertEqual(dataset_data[0][0], self.boiler_obj.id)
        self.assertEqual(dataset_data[0][1].day, get_today().day)
        self.assertEqual(dataset_data[0][2], self.boiler_obj.name)
        self.assertEqual(dataset_data[0][3], 0.0)
        
        # Добавить поле зависящее от категории расхода воды
        field_water = DatasetField()
        field_water.creator = self.test_admin
        field_water.model_content_type = ContentType.objects.get(model='waterconsumption')
        field_water.model_field_name = 'actual_day'
        field_water.name ='Фактический расход'
        field_water.description = "Фактический расход воды"
        field_water.save()
        
        field_water.dataset_set.add(dataset)
        
        grant_permission(field_water, Role.objects.get(name=settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        # Должны быть данные для полей: Идентификатор котельной,
        # Дата, Наименование котельной, WID, Наименование категории,
        # Раход электричества, Расход воды
        dataset_data = get_data(dataset, self.test_admin, date_range, [self.boiler_obj])
        self.assertEqual(dataset_data[0][0], self.boiler_obj.id)
        self.assertEqual(dataset_data[0][1].day, get_today().day)
        self.assertEqual(dataset_data[0][2], self.boiler_obj.name)
        self.assertEqual(dataset_data[0][3], self.water_category.id)
        self.assertEqual(dataset_data[0][4], self.water_category.name)
        self.assertEqual(dataset_data[0][5], 0.0)
        self.assertEqual(dataset_data[0][6], 0.0)
        
        field_fuel = DatasetField()
        field_fuel.creator = self.test_admin
        field_fuel.model_content_type = ContentType.objects.get(model='fuelconsumption')
        field_fuel.model_field_name = 'actual_day'
        field_fuel.name ='Фактический расход топлива'
        field_fuel.description = "Фактический расход топлива в сутки"
        field_fuel.save()
        
        field_fuel.dataset_set.add(dataset)
        
        grant_permission(field_fuel, Role.objects.get(name=settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        # Должны быть данные для полей: Идентификатор котельной,
        # Дата, Наименование котельной, Раход электричества, Расход воды,
        # Идентификатор вида топлива, наименование топлива, марка топлива,
        # Расход топлива
        dataset_data = get_data(dataset, self.test_admin, date_range, [self.boiler_obj])
        self.assertEqual(dataset_data[0][0], self.boiler_obj.id)
        self.assertEqual(dataset_data[0][1].day, get_today().day)
        self.assertEqual(dataset_data[0][2], self.boiler_obj.name)
        self.assertEqual(dataset_data[0][3], self.water_category.id)
        self.assertEqual(dataset_data[0][4], self.water_category.name)
        self.assertEqual(dataset_data[0][5], self.fuel_info.id)
        self.assertEqual(dataset_data[0][6], self.fuel_info.type)
        self.assertEqual(dataset_data[0][7], 0.0)
        self.assertEqual(dataset_data[0][8], 0.0)
        self.assertEqual(dataset_data[0][9], 0.0)

        # Добавляем 
        info = FuelInfo.objects.create(boiler=self.boiler_obj,
                        creator = self.test_admin,
                        type = u"Coal")
        
        # Должны быть данные для полей: Идентификатор котельной,
        # Дата, Наименование котельной, Раход электричества, Расход воды,
        # Идентификатор вида топлива, наименование топлива, марка топлива,
        # Расход топлива
        # Данных должно быть 2 ряда
        dataset_data = get_data(dataset, self.test_admin, date_range, [self.boiler_obj])
        
        self.assertEqual(dataset_data[0][0], self.boiler_obj.id)
        self.assertEqual(dataset_data[0][1].day, get_today().day)
        self.assertEqual(dataset_data[0][2], self.boiler_obj.name)
        self.assertEqual(dataset_data[0][3], self.water_category.id)
        self.assertEqual(dataset_data[0][4], self.water_category.name)
        self.assertEqual(dataset_data[0][5], self.fuel_info.id)
        self.assertEqual(dataset_data[0][6], self.fuel_info.type)
        self.assertEqual(dataset_data[0][7], 0.0)
        self.assertEqual(dataset_data[0][8], 0.0)
        self.assertEqual(dataset_data[0][9], 0.0)
        
        self.assertEqual(dataset_data[1][0], self.boiler_obj.id)
        self.assertEqual(dataset_data[1][1].day, get_today().day)
        self.assertEqual(dataset_data[1][2], self.boiler_obj.name)
        self.assertEqual(dataset_data[1][3], self.water_category.id)
        self.assertEqual(dataset_data[1][4], self.water_category.name)
        self.assertEqual(dataset_data[1][5], info.id)
        self.assertEqual(dataset_data[1][6], info.type)
        self.assertEqual(dataset_data[1][7], 0.0)
        self.assertEqual(dataset_data[1][8], 0.0)
        self.assertEqual(dataset_data[1][9], 0.0)

    def test_data_setting(self):
        """
        Проверка установки значения через DataSet
        """
        self.create_boiler()
        # отчет новый
        dataset = Dataset.objects.create(creator = self.test_admin,
                                         name=u"Название отчета",
                                         description=u"Описание отчета")

        grant_permission(dataset, Role.objects.get(name=settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        # Добавить поле, которое не зависит от категорий расхода топлива и воды
        field = DatasetField()
        field.creator = self.test_admin
        field.model_content_type = ContentType.objects.get(model='electricityconsumption')
        field.model_field_name = u'actual_day'
        field.name =u'Фактический расход электричества'
        field.description = u"Фактический расход"
        field.save()
        
        grant_permission(field, Role.objects.get(name=settings.ROLE_VIEWER_NAME),
                         settings.PERMISSION_VIEW_NAME)
        
        field.dataset_set.add(dataset)

        # self.field1.set_value()
        self.assertRaises(PermissionDenied,
                          field.set_value,
                          self.test_viewer,
                          get_today(),
                          0.1,
                          self.boiler_obj,
                          None,
                          None)
        
        grant_permission(field, Role.objects.get(name=settings.ROLE_EDITOR_NAME),
                         settings.PERMISSION_EDIT_NAME)
        
        val = 5.2
        field.set_value(self.test_editor, get_today(), val, self.boiler_obj, None, None)
        current_val, entity = field.get_value(self.test_editor, get_today(), self.boiler_obj, None, None)
        self.assertEqual(current_val, val)
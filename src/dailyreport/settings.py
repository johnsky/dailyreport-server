# -*- coding: utf-8 -*-

import os
import logging

PRODUCTION_VERSION = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

SETTINGS_FILE_LOCATION = os.path.dirname(__file__)
DATE_FORMAT = "%Y-%m-%d"

ADMINS = (
    ('Ivan Pogorelov', 'ivan.pogorelov@gmail.com'),
)

MANAGERS = ADMINS


# Database settings
DATABASES = {
    'default':
    {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dev',                                      # Or path to database file if using sqlite3.
        'USER': 'dailyreport',                              # Not used with sqlite3.
        'PASSWORD': '123456',                           # Not used with sqlite3.
        'HOST': '127.0.0.1',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                                    # Set to empty string for default. Not used with sqlite3.
    },
    
    'import_target':
    {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dailyreport_import',                          # Or path to database file if using sqlite3.
        'USER': 'dailyreport',                              # Not used with sqlite3.
        'PASSWORD': '123456',                           # Not used with sqlite3.
        'HOST': '127.0.0.1',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                                     # Set to empty string for default. Not used with sqlite3.
    },
    
    'import_source':
    {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dailyreport',                          # Or path to database file if using sqlite3.
        'USER': 'dailyreport',                              # Not used with sqlite3.
        'PASSWORD': '123456',                           # Not used with sqlite3.
        'HOST': '127.0.0.1',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                                     # Set to empty string for default. Not used with sqlite3.
    },         
             
}

if PRODUCTION_VERSION:
    DATABASES['default'] = \
    {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dailyreport_dev',                          # Or path to database file if using sqlite3.
        'USER': 'dailyreport',                              # Not used with sqlite3.
        'PASSWORD': '123456',                           # Not used with sqlite3.
        'HOST': '127.0.0.1',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                                     # Set to empty string for default. Not used with sqlite3.
    }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "Asia/Vladivostok"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-RU'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

#STATIC_ROOT = "/home/jacob/projects/mysite.com/sitestatic"
#STATIC_URL = ""

LOCAL_ROOT = None
if not LOCAL_ROOT:
    local_dir = os.path.dirname(__file__)
    #print local_dir
    LOCAL_ROOT = os.path.join(local_dir)

#HTDOCS_ROOT = os.path.join(LOCAL_ROOT, 'htdocs')
#MEDIA_ROOT = os.path.join(HTDOCS_ROOT, 'media')

# URL prefix for media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
#
# Examples: "http://foo.com/media/", "/media/".
#MEDIA_URL = 


#------------------------------------------------------------------------------

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = 'media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# If the application version is production then..  
if PRODUCTION_VERSION:
    MEDIA_ROOT = '/var/www/html/dailyreport/media/'
    MEDIA_URL = 'http://127.0.0.1/dailyreport/media/'
    ADMIN_MEDIA_PREFIX = '/dailyreport/media/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'jj0sd5qbxpuv6!f#^h-^cdnwe((jrr+wd9+kv*g*lu0+$rz&_%'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'dailyreport.middleware.Checker'
)

ROOT_URLCONF = 'dailyreport.urls'

TEMPLATE_DIRS = (
    os.path.join(SETTINGS_FILE_LOCATION, "reporting", "templates"),
)

#AUTHENTICATION_BACKENDS = (
#   'dailyreport.auth.auth_backends.ReportUserModelBackend',)

#CUSTOM_USER_MODEL = 'accounts.ReportUser'


# Разрешения
PERMISSION_CREATE_NAME = u"Создавать"
PERMISSION_VIEW_NAME = u"Просматривать"
PERMISSION_EDIT_NAME = u"Редактировать"
PERMISSION_DELETE_NAME = u"Удалять"

# Разработчик может все испортить
ROLE_DEVELOPER_NAME = u"Разработчик"
# Роль администратора
ROLE_ADMIN_NAME = u"Администратор"
# Имеет право создавать, редактировать, удалять записи
# Без ограничения по времени. 
ROLE_MANAGER_NAME = u"Менеджер"
# Имеет право редактировать
# Редактирование разрешено в течение 3 дней 
ROLE_EDITOR_NAME = u"Редактор"
# Имеет право только просматривать
ROLE_VIEWER_NAME = u"Обозреватель"

DEVELOPERS_GROUP_NAME = u"Разработчики"
MANAGERS_GROUP_NAME = u"Менеджеры"
ADMINS_GROUP_NAME = u"Администраторы"
VIEWERS_GROUP_NAME = u"Обозреватели"
EDITORS_GROUP_NAME = u"Редакторы"

# Виды топлива
FUEL_TYPE_NAMES=(u"Уголь",u"Газ",u"ДТ",u"Мазут")

# Виды ресурсов
RESOURCE_TYPE_WATER = u"Вода"
RESOURCE_TYPE_ELECTRICITY = u"Электричество"
RESOURCE_TYPE_FUEL = u"Топливо"

DEVIATION_PROBLEM_STATE_OPEN = u'Открыта'
DEVIATION_PROBLEM_STATE_CLOSED = u'Закрыта'


REPORTING_FONTS_LOCATION = os.path.join(SETTINGS_FILE_LOCATION, "reporting", "fonts")
 
SERIALIZATION_MODULES = {
    'json': 'wadofstuff.django.serializers.json'
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    #'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'permissions',
    
    # Dailyreport applications
    'dailyreport.authentication',
    'dailyreport.core',
    'dailyreport.dataset',
    'dailyreport.company_object',
    'dailyreport.user_profile',
    'dailyreport.reporting',
    'dailyreport.consumption',
    'dailyreport.water',
    'dailyreport.fuel',
    'dailyreport.electricity',
    'dailyreport.deviation',
    
    # Schema migration toolkit
    'south',
    
    # Data versioning
    'reversion',
)


LOGGING = {
   'version': 1,
   'disable_existing_loggers': True,
   'formatters' : {
       'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
   },
   'handlers': {
        'file':{
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter' : 'verbose',
            'encoding' : 'utf-8',
            'when' : 'midnight',
            'filename': 'dailyreport.log',
        },
        'null': {
            'level':'ERROR',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'ERROR',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'dailyreport': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

if PRODUCTION_VERSION:
    LOGGING = {
       'version': 1,
       'disable_existing_loggers': True,
       'formatters' : {
           'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(levelname)s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
       },
       'handlers': {
            'file':{
                'level': 'DEBUG',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter' : 'verbose',
                'encoding' : 'utf-8',
                'when' : 'midnight',
                'filename': '/var/log/dailyreport/dailyreport.log',
            },
            'null': {
                'level':'ERROR',
                'class':'django.utils.log.NullHandler',
            },
            'console':{
                'level':'ERROR',
                'class':'logging.StreamHandler',
                'formatter': 'simple'
            },
        },
        'loggers': {
            'dailyreport': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }

SOUTH_TESTS_MIGRATE = False
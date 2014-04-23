'''
Copyright (C) 2012,2013 Scuola Superiore Sant'Anna (http://www.sssup.it) 
and Consorzio Nazionale Interuniversitario per le Telecomunicazioni 
(http://www.cnit.it).

This file is part of PyoT, an IoT Django-based Macroprogramming Environment.

PyoT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
  
PyoT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with PyoT.  If not, see <http://www.gnu.org/licenses/>.

@author: Andrea Azzara' <a.azzara@sssup.it>
'''
import os, socket
from ConfigParser import RawConfigParser

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

config = RawConfigParser()
config.read(PROJECT_PATH + '/settings.ini')

LOCAL_DB = config.getboolean('database', 'DATABASE_LOCAL')

WEB_APPLICATION_SERVER = False

if socket.gethostname() == 'andrea-lab':
    WEB_APPLICATION_SERVER = False
    LOCAL_DB = True

DEBUG = True

if socket.gethostname() == 'pyot-vcr':
    WEB_APPLICATION_SERVER = True
    DEBUG = True
    LOCAL_DB = False
TEMPLATE_DEBUG = DEBUG

RABBIT_PORT = 5672
DB_SCHEMA =  config.get('database', 'DATABASE_NAME')
SQL_USER = config.get('database', 'DATABASE_USERNAME')
SQL_PWD = config.get('database', 'DATABASE_PASSWORD_USER')
SQL_PORT = ''

if WEB_APPLICATION_SERVER:
    SERVER_ADDRESS = '127.0.0.1'
else:
    SERVER_ADDRESS = config.get('database', 'DATABASE_HOST')    

'''
ADMINS = (
    ('Andrea', 'a.azzara@sssup.it'),
)
'''

TRES_BASE = config.get('tres', 'TRES_BASE')

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []



CLEANUP_TASK_PERIOD = 30
CLEANUP_TIME = 90
RECOVERY_PERIOD = 30

WORKER_RECOVERY = True
SUBSCRIPTION_RECOVERY = True

TFMT = "%Y-%m-%d %H:%M:%S" #global format for time strings

AUTH_PROFILE_MODULE = 'pyot.UserProfile'

#MANAGERS = ADMINS

SQLITE_3 = os.path.join(PROJECT_PATH, 'db')

if LOCAL_DB:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': SQLITE_3,                      # Or path to database file if using sqlite3.
            'USER': '',                      # Not used with sqlite3.
            'PASSWORD': '',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': DB_SCHEMA,                      # Or path to database file if using sqlite3.
            'USER': SQL_USER,                      # Not used with sqlite3.
            'PASSWORD': SQL_PWD,                  # Not used with sqlite3.
            'HOST': SERVER_ADDRESS,                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': SQL_PORT,                      # Set to empty string for default. Not used with sqlite3.
        }
    }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.abspath(os.path.dirname(__file__)) + '/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

TEMPLATE_ROOT = os.path.abspath(os.path.dirname(__file__)) + '/templates/'
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.abspath(os.path.dirname(__file__)) + '/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
#ADMIN_MEDIA_PREFIX = '/static/admin/'

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
SECRET_KEY = '9%$in^gpdaig@v3or_to&_z(=n)3)$f1mr3hf9e#kespy2ajlo'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

INTERNAL_IPS = ('127.0.0.1',)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    TEMPLATE_ROOT,
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

import djcelery
djcelery.setup_loader()

#rabbitMQ config
BROKER_URL = SERVER_ADDRESS

CELERY_ROUTES = {'pyot.tasks.checkConnectedHosts': {'queue': 'periodic'},
                 'pyot.tasks.recoveryWorkers': {'queue': 'periodic'}} # dedicated queue for periodic tasks 

CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERYD_MAX_TASKS_PER_CHILD=1
CELERYD_TIMER_PRECISION=0.1
CELERYD_PREFETCH_MULTIPLIER=1

BROKER_HEARTBEAT=0

CELERY_ENABLE_UTC=True

CELERY_DISABLE_RATE_LIMITS = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pyot',
    'djcelery',
    'django_evolution',
    'registration',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django_extensions',
)

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

'''
import logging
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
)
'''

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


LOGF = os.path.abspath(os.path.dirname(__file__)) + '/log/django.log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file_logging': {
            'level' : 'DEBUG',
            'class' : 'logging.handlers.RotatingFileHandler',
            'backupCount' : 5,
            'maxBytes': 5000000,
            'filename': LOGF
            },
        'null': {
            'level': 'DEBUG',
            'class':'django.utils.log.NullHandler',
            }, 
        },
        'loggers': {
            'django.db' : {
                'handlers' : ['null'],
                'level' : 'DEBUG',
                'propagate': False,
            },
        'django': {
            'handlers': ['file_logging'],
            'level': 'DEBUG',
            'propagate': True,
        }, 
        }
}

IPYTHON_ARGUMENTS = [
    '--ext', 'django_extensions.management.notebook_extension',
    '--ext', 'pyot.notebook_extension',
    '--debug',    "--ip='*'",
]

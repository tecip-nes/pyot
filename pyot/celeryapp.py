from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings


CELERY_ROUTES = {'pyot.tasks.checkConnectedHosts': {'queue': 'periodic'},
                 'pyot.tasks.recoveryWorkers': {'queue': 'periodic'}}

CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERYD_MAX_TASKS_PER_CHILD = 1
CELERYD_TIMER_PRECISION = 0.1
CELERYD_PREFETCH_MULTIPLIER = 1

BROKER_HEARTBEAT = 0

CELERY_ENABLE_UTC = True

CELERY_DISABLE_RATE_LIMITS = True


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyot.settings')

app = Celery('pyot', backend='amqp', broker='amqp://'+settings.BROKER_URL)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print 'Request: {0!r}'.format(self.request)

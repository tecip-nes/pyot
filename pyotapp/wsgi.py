import os
import sys


apache_configuration= os.path.dirname(__file__)
project = os.path.dirname(apache_configuration)
workspace = os.path.dirname(project)
sys.path.append(workspace)

sys.path.append('/usr/local/lib/python2.6/dist-packages/django')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ["CELERY_LOADER"] = "django"
# This application object is used by the development server
# as well as any WSGI server configured to use this file.

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


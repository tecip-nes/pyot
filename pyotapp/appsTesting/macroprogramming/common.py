import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from django.core.management import setup_environ
import settings
setup_environ(settings)
import time

#! /bin/bash

venv/bin/python manage.py syncdb --noinput 
venv/bin/python manage.py loaddata auth.json

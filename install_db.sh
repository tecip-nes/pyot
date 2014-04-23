#! /bin/bash
venv/bin/python pyotapp/manage.py syncdb --noinput 
venv/bin/python pyotapp/manage.py loaddata pyotapp/auth.json

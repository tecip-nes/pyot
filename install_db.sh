#! /bin/bash
cd pyot
../venv/bin/python manage.py syncdb --noinput 
../venv/bin/python manage.py loaddata auth.json

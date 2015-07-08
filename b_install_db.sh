#! /bin/bash

venv/bin/python manage.py migrate --noinput 
venv/bin/python manage.py loaddata initial_data_pyot.json

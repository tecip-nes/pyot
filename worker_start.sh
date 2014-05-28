#! /bin/bash
venv/bin/python pyotapp/manage.py celeryd -s celery -E -B -l INFO -c 30 -n cooja@pyot -Q cooja@pyot,celery,periodic --without-heartbeat --without-gossip --Ofair

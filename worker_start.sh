#! /bin/bash
venv/bin/python pyotapp/manage.py celeryd -s celery -E -B -l INFO -c 30 -n celery@cooja -Q celery@cooja,celery,periodic --without-heartbeat --without-gossip

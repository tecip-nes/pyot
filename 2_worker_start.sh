#! /bin/bash
venv/bin/celery -A pyot worker -l info -s celery -E -B -l INFO -c 30 \
  -n cooja@pyot -Q cooja@pyot,celery --without-heartbeat \
  --without-gossip -Ofair --purge

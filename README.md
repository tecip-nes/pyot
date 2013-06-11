py-ot
=====
export CONTIKI_SNM_BASE="/.../pyotapp"
export CONTIKI ........


sudo apt-get install python-mysqldb libmysqlclient-dev rabbitmq-server python-pip python-dev

sudo pip install -r requirements.txt

compilazione libcoap/examples
********************************************************************************
in coapyGw/appsTesting/libcoap-4.0.1
$ ./configure
$ make


Creazione db
********************************************************************************
in coapyGw/
$ ./manage syncdb


Avvio dell'applicazione web e di celery
********************************************************************************
in coapyGw/
$ ./manage runserver

in another terminal:
$ ./manage.py celeryd -B -s celery -E -l INFO -c 10


compilazione ed avvio di cooja
********************************************************************************
in coapyGw/appsTesting/contiki_cooja

$ make TARGET=cooja server-rd.csc
in another terminal:
$ make connect-router-cooja



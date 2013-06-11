PyoT
=========

PyoT is a IoT Django-based web application and macroprogramming interface.

PyoT puts together Django, Celery, libcoap: 

  - Allows remote management of a IoT based network. (6LoWPAN, CoAP)
  - CoAP resources, 6LoWPAN nodes are abstracted as high-level Django models  objects
  - Provides a nice interface to interact with CoAP resources
  - Enables macroprogramming, using django shell

PyoT comes with a Contiki Cooja simulation for local testing.

Requirements and installation
--------------
To test PyoT locally you need CONTIKI OS tree.

Make sure to have an environment variable pointing to CONTIKI root:
```sh
export CONTIKI PATH_TO_CONTIKI_ROOT
```

Installing general requirements:
```sh
sudo apt-get install python-mysqldb libmysqlclient-dev rabbitmq-server python-pip python-dev
```

Install python requirements, using virtualenv is reccomended
```sh
sudo pip install -r requirements.txt
```

Configure and build libcoap:
```sh
cd pyotapp/appsTesting/libcoap-4.0.1/
./configure
make
```

Database creation:
```sh
cd pyotapp
./manage syncdb
```

Running the application
--------------
Starting Django web application:
```sh
cd pyotapp
./manage runserver
```

Start celery workers in another terminal:
```sh
./manage.py celeryd -B -s celery -E -l INFO -c 10
```

Compile and start Cooja simulation:
```sh
cd pyotapp/appsTesting/contiki_cooja
make TARGET=cooja server-rd.csc
```

Start tunslip, open another terminal and type:
```sh
make connect-router-cooja
```

Open 127.0.0.1:8000 in a web browser, enter "settings" page and start RD server. Open Cooja simulator and start the simulation. In a few seconds you should see the Host and Resource page populating with the nodes .


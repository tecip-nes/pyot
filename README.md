PyoT
=========

PyoT is an IoT Django-based web application and macroprogramming interface.

PyoT puts together Django, Celery, libcoap: 

  - Allows remote management of a IoT based network. (6LoWPAN, CoAP)
  - CoAP resources, 6LoWPAN nodes are abstracted as high-level Django models objects
  - Provides a nice interface to interact with CoAP resources
  - Enables macroprogramming, using Django shell
  - Supports multiple network handled by different celery worker nodes

PyoT comes with a Contiki Cooja simulation for local testing.

Requirements and installation (tested on Ubuntu 12.04)
--------------
To test PyoT locally you need CONTIKI OS tree.

Make sure to have an environment variable pointing to CONTIKI root:
```sh
export CONTIKI PATH_TO_CONTIKI_ROOT
```

Installing general requirements:
```sh
sudo apt-get install python-mysqldb libmysqlclient-dev rabbitmq-server python-pip python-dev libcurl4-gnutls-dev graphviz libgraphviz-dev  libfreetype6-dev libpng12-dev
```

Install python requirements, using virtualenv, and build libcoap and its examples:
```sh
sudo pip install virtualenv
./install_reqs.sh
```

Database creation:
```sh
./install_db.sh
```

Running the application
--------------
Starting Django web application:
```sh
cd pyotapp
./server_start.sh
```

Start the worker node in another terminal:
```sh
./worker_start.sh
```

Optionally open a new terminal to start IPython Notebook interface:
```sh
./notebook_start.sh
```

Compile and start Cooja simulation. For this step I assume you have ant, jdk, msp430gcc already installed:
```sh
./cooja_start.sh
```

Start tunslip, open another terminal and type:
```sh
./tunslip_start.sh
```

Open 127.0.0.1:8000 in a web browser (tested with Chrome), enter "settings" page and start *RD server*. Open Cooja simulator and start the simulation. In a few seconds you should see the Host and Resource page populating with the nodes. The system will automatically perform resource discovery on the hosts.


Real deployment
--------------
PyoT Celery workers are designed to be executed on embedded devices connected to 6LoWPAN border routers. CoAP-related tasks will be dispatched to the workers by Celery. In order to test PyoT on a real IoT deployment, clone the project on the selected platform and edit *settings.py*

Also change LOCAL_DB to *False* (you will need a mySQL db). Repeat DB installation phase (syncdb command) to create the mySQL DB. I assume that you will install a mySQL server on the same machine where  Web application server is executed.

You will have two copies of PyoT running, one on the web application server, the other one on the (embedded) platform connected to the border router. On the web application server set 
```py
WEB_APPLICATION_SERVER = True
```

On the (embedded)platform set 
```py
WEB_APPLICATION_SERVER = False
```
and configure SERVER_ADDRESS to the IP address of the Web application server.

Screenshots
--------------
**Hosts**


![Hosts](https://raw.github.com/tecip-nes/pyot/master/screenshots/hosts.png)

**Observe**


![Observe](https://raw.github.com/tecip-nes/pyot/master/screenshots/observe.png)

**Macroprogramming**


![Macroprogramming](https://raw.github.com/tecip-nes/pyot/master/screenshots/macroprogramming.png)

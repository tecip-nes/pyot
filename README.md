PyoT
=========

PyoT is a Web-Based Macroprogramming Interface for the IoT

  - Allows remote management of IoT-based networks
  - CoAP resources and 6LoWPAN nodes are abstracted as high-level Python objects
  - Provides a web interface to interact with CoAP resources
  - Provides interactive Macroprogramming, using the Shell
  - Resource discovery and indexing based on CoRE Resource Directory
  - Flexible event handling (automatic reaction when IoT resources send alarm notifications)
  - Asynchronous tasks performing communication with IoT nodes on PyoT Workers

<img src="https://raw.github.com/tecip-nes/pyot/master/screenshots/arch.png" alt="PyoT Architecture" width="500px" />

PyoT comes with a Contiki Cooja simulation for local testing.

Requirements and installation (tested on Ubuntu 12.04)
--------------
To test PyoT locally you need Contiki OS tree. PyoT has been tested on tag 2.7 of Contiki Git repository.

Make sure to have an environment variable pointing to Contiki root:
```sh
export CONTIKI [/../contiki]
```

Install general requirements:
```sh
sudo apt-get install python-mysqldb libmysqlclient-dev rabbitmq-server python-pip python-dev libcurl4-gnutls-dev graphviz libgraphviz-dev  libfreetype6-dev libpng12-dev
```

The next step will install python requirements, in a local virtual env folder, and build libcoap:
```sh
./a_install_reqs.sh
```

The we create a local sqlite database:
```sh
./b_install_db.sh
```

How to run the application
--------------
Start the web application:
```sh
./1_server_start.sh
```

Start the worker node in another terminal:
```sh
./2_worker_start.sh
```

Optionally open a new terminal to start IPython Notebook interface:
```sh
./3_notebook_start.sh
```

Compile and start Cooja simulation. For this step I assume you have ant, jdk, msp430gcc and everything required to run a Cooja simulation already installed:
```sh
./4_cooja_start.sh
```

Start tunslip, open another terminal and type:
```sh
./5_tunslip_start.sh
```

Open a web browser (tested with Chrome) and visit http://127.0.0.1:8000. Enter *"settings"* page and start *RD server* on the Cooja worker node. Open Cooja simulator and start the simulation. In a few seconds you should see the Host and Resource page populating with the nodes. The system will automatically perform resource discovery on the hosts.

Macroprogramming
--------------
  - Program group of nodes or entire networks as a whole
  - Easily control sensors and actuators
  - Support Synchronous and Asynchronous Semantic
  
The easiest way to test macroprogramming is through the IPython Notebook interface. You can find some example scripts preloaded on PyoT's Notebook.

Real deployment
--------------
PyoT Worker Nodes are designed to be executed on embedded devices connected to 6LoWPAN border routers. CoAP-related tasks will be dispatched to the workers through the broker. In order to test PyoT on a real IoT deployment, clone the project on the selected platform and edit *settings.py*

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
[Hosts](https://raw.github.com/tecip-nes/pyot/master/screenshots/hosts.png)

[Observe](https://raw.github.com/tecip-nes/pyot/master/screenshots/observe.png)

[Macroprogramming](https://raw.github.com/tecip-nes/pyot/master/screenshots/macroprogramming.png)

Build status
------------

|              builder                                            |      build            | outcome
| --------------------------------------------------------------- | --------------------- | -------
| [Travis](https://travis-ci.org/tecip-nes/pyot)           | unit tests            | [![Build Status](https://travis-ci.org/tecip-nes/pyot.png?branch=master)](https://travis-ci.org/tecip-nes/pyot)
[![Code Health](https://landscape.io/github/andreaazzara/pyot/master/landscape.png)](https://landscape.io/github/andreaazzara/pyot/master)


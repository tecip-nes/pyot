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

Install general requirements:
```sh
sudo apt-get install python-mysqldb libmysqlclient-dev rabbitmq-server python-pip python-dev libcurl4-gnutls-dev graphviz libgraphviz-dev  libfreetype6-dev libpng12-dev
```

The next step will install python requirements, in a local virtual env folder, and build libcoap:
```sh
./a_install_reqs.sh
```

Then create a local sqlite database:
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

Open Cooja simulator and start the simulation. In a few seconds you should see the Host and Resource page populating with the nodes. The system will automatically perform resource discovery on the hosts.

Macroprogramming
--------------
  - Program group of nodes or entire networks as a whole
  - Easily control sensors and actuators
  - Support Synchronous and Asynchronous Semantic
  
The easiest way to test macroprogramming is through the IPython Notebook interface. You can find some example scripts preloaded on PyoT's Notebook.

Build status
------------

|              builder                                            |      build            | outcome
| --------------------------------------------------------------- | --------------------- | -------
| [Travis](https://travis-ci.org/tecip-nes/pyot)           | unit tests            | [![Build Status](https://travis-ci.org/tecip-nes/pyot.png?branch=master)](https://travis-ci.org/tecip-nes/pyot)
[![Code Health](https://landscape.io/github/andreaazzara/pyot/master/landscape.png)](https://landscape.io/github/andreaazzara/pyot/master)


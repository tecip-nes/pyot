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

PyoT comes with some Contiki Cooja simulations for local testing. The examples included in the package require the gcc-msp430 version 4.7.2 compiler. [Here] you can find instructions on how to build the compiler. For simplicity a packer-based virtual machine is provided in the *packer_pyot_vm* folder. To build the VM just execute *run.sh*. The resulting VM can be loaded on VirtualBox and contains a ready-to-run version of PyoT, with all the required dependencies.

[Here]:https://github.com/tecip-nes/contiki-tres/wiki/Building-the-latest-version-of-mspgcc

Requirements and manual installation (tested on Ubuntu 12.04)
--------------

Install general requirements:
```sh
sudo apt-get install python-mysqldb libmysqlclient-dev rabbitmq-server python-pip python-dev libcurl4-gnutls-dev graphviz libgraphviz-dev  libfreetype6-dev libpng12-dev
```

The next step will install python requirements, in a local virtual env folder, and build libcoap:
```sh
./a_install_reqs.sh
```

This command creates a local sqlite database and loads some preliminary data on it:
```sh
./b_install_db.sh
```
An admin user account is automatically created. Username: *noes*. Password: *noes*.

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

Open a new terminal to start IPython Notebook interface:
```sh
./3_notebook_start.sh
```

Compile and start on the provided Cooja simulations. For the following steps I assume you have ant, jdk, msp430gcc and everything required to run a Cooja simulation already installed:

```sh
./4a_cooja_erbium_start.sh
```
The first simulation includes a set of simple CoAP servers with simulated sensors and actuators. It can be tested opening and executing the 'demo' notebook.

```sh
./4b_cooja_tres_start.sh
```

The second simulation includes a [T-Res] example. To test it just open and execute the 'T-Res' notebook.

[T-Res]:https://github.com/tecip-nes/contiki-tres

Start tunslip, open another terminal and type:
```sh
./5_tunslip_start.sh
```

Open the Cooja simulator window and start the simulation. In a few seconds you should see the Host and Resource page populating with the nodes. The system will automatically perform resource discovery on the hosts.

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


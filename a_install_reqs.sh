#! /bin/bash

git submodule update --init
cd contiki-tres/tools/cooja
ant jar
cd ../
make tunslip6
cd ../../


sudo pip install virtualenv
virtualenv venv
venv/bin/pip install -r requirements.txt

cd libcoap-coap18/
autoconf
./configure
make
cd examples
make

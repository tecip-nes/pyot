#! /bin/bash

sudo pip install virtualenv
virtualenv venv
venv/bin/pip install -r requirements.txt
venv/bin/pip install matplotlib==1.1

cd libcoap-coap18/
autoconf
./configure
make
cd examples
make

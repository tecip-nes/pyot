#! /bin/bash

sudo pip install virtualenv
virtualenv venv
venv/bin/pip install -r requirements.txt

cd libcoap-coap18/
autoconf
./configure
make
cd examples
make

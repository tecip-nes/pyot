#! /bin/bash

sudo pip install virtualenv
virtualenv venv
venv/bin/pip install -r requirements.txt
venv/bin/pip install matplotlib==1.1

cd pyotapp/appsTesting/libcoap-4.0.1/
./configure
make
cd examples
make

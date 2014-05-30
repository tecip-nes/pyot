#! /bin/bash
cd examples/contiki_cooja

while : 
do
  sudo $CONTIKI/tools/tunslip6 -a localhost bbbb::1/64
  sleep 1
done

#! /bin/bash
CONTIKI=./contiki-tres

while : 
do
  sudo $CONTIKI/tools/tunslip6 -a localhost aaaa::1/64
  sleep 1
done

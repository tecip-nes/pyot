#!/bin/bash
../../../../apps/tres/tools/tres-client-od-18 \
   coap://[aaaa::200:0:0:2]/tasks/halve \
   va.py \
   "<coap://[aaaa::200:0:0:4]/actuator>","<coap://[aaaa::200:0:0:5]/actuator>","<coap://[aaaa::200:0:0:3]/actuator>"

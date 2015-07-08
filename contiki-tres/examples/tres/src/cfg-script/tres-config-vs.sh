#!/bin/bash
../../../../apps/tres/tools/tres-client-18 \
   coap://[aaaa::200:0:0:2]/tasks/halve \
   vs.py \
   "<coap://[aaaa::200:0:0:3]/sensor>","<coap://[aaaa::200:0:0:4]/sensor>" \
   "<coap://[aaaa::200:0:0:4]/actuator>","<coap://[aaaa::200:0:0:5]/actuator>"

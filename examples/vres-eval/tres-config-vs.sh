#!/bin/bash
$CONTIKI/apps/tres/tools/tres-client-18 \
   coap://[bbbb::200:0:0:6]/tasks/halve \
   vs.py \
   "<coap://[bbbb::200:0:0:3]/sensors/light>","<coap://[bbbb::200:0:0:4]/sensors/light>","<coap://[bbbb::200:0:0:5]/sensors/light>" 

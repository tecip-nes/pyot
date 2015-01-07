#!/bin/bash
$CONTIKI/apps/tres/tools/tres-client-od-18 \
   coap://[bbbb::200:0:0:d]/tasks/halve \
   va.py \
   "<coap://[bbbb::200:0:0:a]/actuators/leds>","<coap://[bbbb::200:0:0:b]/actuators/leds>","<coap://[bbbb::200:0:0:c]/actuators/leds>"

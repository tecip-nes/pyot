/*
 * Copyright (c) 2012, Matthias Kovatsch and other contributors.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the Institute nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * This file is part of the Contiki operating system.
 */

/**
 * \file
 *      based on Erbium (Er) REST Engine example (with CoAP-specific code)
 * \author
 *      Matthias Kovatsch <kovatsch@inf.ethz.ch>
 *      modified by Andrea Azzara' <a.azzara@sssup.it>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "contiki.h"
#include "contiki-net.h"
#include "../rplinfo/rplinfo.h"
#include "../common/pyot.h"
#include "node-id.h"

#include "er-coap.h"
#include "er-coap-engine.h"
#include "er-coap-transactions.h"


uip_ipaddr_t server_ipaddr;
static struct etimer et;

/* Example URIs that can be queried. */
#define NUMBER_OF_URLS 2

extern resource_t res_light;
extern resource_t res_toggle;
extern resource_t res_leds;


int getRandUint(unsigned int mod){
  return (unsigned int)(rand() % mod);
}

PROCESS(rest_server_example, "Er");
AUTOSTART_PROCESSES(&rest_server_example);

PROCESS_THREAD(rest_server_example, ev, data)
{
  PROCESS_BEGIN();
  srand(node_id);

  /* Initialize the REST engine. */
  rest_init_engine();
  SERVER_NODE(&server_ipaddr);
  /* Activate the application-specific resources. */
  rest_activate_resource(&res_light, "light"); 
  //rest_activate_resource(&res_toggle, "actuators/toggle");  
  rest_activate_resource(&res_leds, "actuators/leds");  
  rplinfo_activate_resources();

#if PYOT_KEEPALIVE 
  static coap_packet_t request[1]; /* This way the packet can be treated as pointer as usual. */
  
  static int time=0;
  static char content[12];

  int wait_time = getRandUint(MAX_WAITING);
  int base_wait = BASE_WAITING;

  etimer_set(&et, (wait_time + base_wait) * CLOCK_SECOND);

  while(1) {
    PROCESS_YIELD();
    if (etimer_expired(&et)) break;
    }
  etimer_reset(&et);
  etimer_set(&et, TOGGLE_INTERVAL * CLOCK_SECOND);
  size_t len;
  while(1) {
    PROCESS_YIELD();
    if (etimer_expired(&et)) {
      PRINTF("Sending msg to rd...");

      coap_init_message(request, COAP_TYPE_NON, COAP_POST, 0 );
      coap_set_header_uri_path(request, "/rd");
      coap_set_payload(request, content, snprintf(content, sizeof(content), "%d", time++));
      request->mid = coap_get_mid();
      len = coap_serialize_message(request, uip_appdata);
      coap_send_message(&server_ipaddr, REMOTE_PORT, uip_appdata, len);      
      PRINTF("Done\n");
      etimer_reset(&et);
     }
  } /* while (1) */

#endif //PYOT_KEEPALIVE 
  PROCESS_END();
}

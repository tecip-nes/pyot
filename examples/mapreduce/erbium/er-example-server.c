/*
 * Copyright (c) 2013, Real-Time Systems laboratory, Sucola Superiore Sant'Anna
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
 */

/**
 * \author
 *      Daniele Alessandrelli - <d.alessandrelli@sssup.it>
 */

#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

#include "contiki.h"
#include "node-id.h"
#include "erbium.h"
#include "../rplinfo/rplinfo.h"
#include "../common/pyot.h"

/* For CoAP-specific example: not required for normal RESTful Web service. */
#if WITH_COAP == 3
#include "er-coap-03.h"
#elif WITH_COAP == 7
#include "er-coap-07.h"
#elif WITH_COAP == 12
#include "er-coap-12.h"
#elif WITH_COAP == 13
#include "er-coap-13.h"
#else
#warning "Erbium example without CoAP-specifc functionality"
#endif /* CoAP-specific example */

#if WITH_COAP == 3
#include "er-coap-03-engine.h"
#elif WITH_COAP == 6
#include "er-coap-06-engine.h"
#elif WITH_COAP == 7
#include "er-coap-07-engine.h"
#elif WITH_COAP == 12
#include "er-coap-12-engine.h"
#elif WITH_COAP == 13
#include "er-coap-13-engine.h"
#else
#error "CoAP version defined by WITH_COAP not implemented"
#endif
/*----------------------------------------------------------------------------*/
#if !UIP_CONF_IPV6_RPL                       \
    && !defined (CONTIKI_TARGET_MINIMAL_NET) \
    && !defined (CONTIKI_TARGET_NATIVE)
#warning "Compiling with static routing!"
#include "static-routing.h"
#endif

/*----------------------------------------------------------------------------*/
/*                               Extern variables                             */
/*----------------------------------------------------------------------------*/
/*----------------------------------------------------------------------------*/
uip_ipaddr_t server_ipaddr;
static struct etimer et;

/* Example URIs that can be queried. */
#define NUMBER_OF_URLS 2
/* leading and ending slashes only for demo purposes, get cropped automatically when setting the Uri-Path */
char* service_urls[NUMBER_OF_URLS] = {".well-known/core", "/rd"};
/*----------------------------------------------------------------------------*/
int getRandUint(unsigned int mod){
  return (unsigned int)(rand() % mod);
}

/*----------------------------------------------------------------------------*/
PROCESS(tres_process, "actuator node");

AUTOSTART_PROCESSES(&tres_process);


/*----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------*/
/*                          Fake Actuator Resoruce                            */
/*----------------------------------------------------------------------------*/
RESOURCE(actuator, METHOD_GET | METHOD_POST | METHOD_PUT, "actuator",
        "title=\"actuator\";rt=\"Text\"");

/*----------------------------------------------------------------------------*/
void
actuator_handler(void *request, void *response, uint8_t *buffer,
                 uint16_t preferred_size, int32_t *offset)
{
  static char setpoint[10];
  static uint8_t last_token_len = 0;
  static uint8_t last_token[COAP_TOKEN_LEN];
  const uint8_t *token;
  uint16_t len;
  rest_resource_flags_t method;
  const uint8_t *ptr;
  int i;

  // Filter duplicated messages
  // FIXME: token option is not enough, we must check also the client ip address
  len = coap_get_header_token(request, &token);
  if(last_token_len == len) {
    for(i = 0; i < len && token[i] == last_token[i]; i++);
    if(i == len) {
      // duplicated message
      return;
    }
  }
  last_token_len = len;
  for(i = 0; i < len; i++) {
    last_token[i] = token[i];
  }

  method = REST.get_method_type(request);
  if(method == METHOD_GET) {
    len = strlen(setpoint);
    memcpy(buffer, setpoint, len);
    REST.set_header_content_type(response, REST.type.TEXT_PLAIN);
    REST.set_response_payload(response, buffer, len);
  } else {                      // it's a put/post request
    len = REST.get_request_payload(request, &ptr);
    printf("A: %s\n", (char *)ptr);
    if(len > 9) {
      len = 9;
    }
    memcpy(setpoint, ptr, len);
    setpoint[len] = '\0';
  }
}



/*----------------------------------------------------------------------------*/
PROCESS_THREAD(tres_process, ev, data)
{
  PROCESS_BEGIN();

  srand(node_id);
  rest_init_engine();
  rest_activate_resource(&resource_actuator);
  rplinfo_activate_resources();
  
  static coap_packet_t request[1]; /* This way the packet can be treated as pointer as usual. */
  SERVER_NODE(&server_ipaddr);

  /* receives all CoAP messages */
  coap_receiver_init();
  
  int wait_time = getRandUint(MAX_WAITING);
  int base_wait = BASE_WAITING;
  
  static int g_time=0;
  static char content[12];
  etimer_set(&et, (wait_time + base_wait) * CLOCK_SECOND);

  while(1) {
    PROCESS_YIELD();
    //PROCESS_WAIT_EVENT();
    if (etimer_expired(&et)) break;
    }
  etimer_reset(&et);
  etimer_set(&et, TOGGLE_INTERVAL * CLOCK_SECOND);

  while(1) {
    PROCESS_YIELD();
    if (etimer_expired(&et)) {

      coap_init_message(request, COAP_TYPE_NON, COAP_POST, 0 );
      coap_set_header_uri_path(request, service_urls[1]);


      coap_set_payload(request, content, snprintf(content, sizeof(content), "%d", g_time++));

      coap_transaction_t *transaction;

      request->mid = coap_get_mid();
      if ((transaction = coap_new_transaction(request->mid, &server_ipaddr, REMOTE_PORT)))
      {
        transaction->packet_len = coap_serialize_message(request, transaction->packet);
        coap_send_transaction(transaction);
      }

      etimer_reset(&et);
     }
  } /* while (1) */  
  PROCESS_END();
}

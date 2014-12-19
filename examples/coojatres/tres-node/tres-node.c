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
#include "er-coap.h"
#include "tres.h"
#include "pm.h"
#include "rplinfo.h"
#include "pyot.h"

/*----------------------------------------------------------------------------*/
#if !UIP_CONF_IPV6_RPL                       \
    && !defined (CONTIKI_TARGET_MINIMAL_NET) \
    && !defined (CONTIKI_TARGET_NATIVE)
#warning "Compiling with static routing!"
#include "static-routing.h"
#endif

#ifdef TRES_EXAMPLE_CONF_RANDOM_SENSOR_VALUE
#define TRES_EXAMPLE_RANDOM_SENSOR_VALUE TRES_EXAMPLE_CONF_RANDOM_SENSOR_VALUE
#else
#define TRES_EXAMPLE_RANDOM_SENSOR_VALUE 0
#endif

/*----------------------------------------------------------------------------*/
/*                               Extern variables                             */
/*----------------------------------------------------------------------------*/
uint8_t tres_start_monitoring(tres_res_t *tres);
uint8_t tres_stop_monitoring(tres_res_t *tres);
void task_is_add(tres_res_t *task, char *str);
void task_od_set(tres_res_t *task, char *str);
uip_ipaddr_t server_ipaddr;
static struct etimer et;
/*----------------------------------------------------------------------------*/

PROCESS(tres_process, "T-Res Evaluation");

AUTOSTART_PROCESSES(&tres_process);

/*----------------------------------------------------------------------------*/
/*                          Fake Actuator Resoruce                            */
/*----------------------------------------------------------------------------*/
void actuator_get_handler(void *request, void *response, uint8_t *buffer,
                 uint16_t preferred_size, int32_t *offset);
void
actuator_set_handler(void *request, void *response, uint8_t *buffer,
                 uint16_t preferred_size, int32_t *offset);

static char setpoint[10];                 

RESOURCE(actuator, "title=\"A fake generic actuator\";rt=\"Text\"",
        actuator_get_handler, 
        actuator_set_handler, 
        actuator_set_handler, 
        NULL);


/*----------------------------------------------------------------------------*/
void
actuator_set_handler(void *request, void *response, uint8_t *buffer,
                 uint16_t preferred_size, int32_t *offset)
{
  //static uint8_t last_token_len = 0;
  //static uint8_t last_token[COAP_TOKEN_LEN];
  //const uint8_t *token;
  uint16_t len;
  const uint8_t *ptr;
  //int i;

  // Filter duplicated messages
  // FIXME: token option is not enough, we must check also the client ip address
  /*len = coap_get_token(request, &token);
  if(last_token_len == len) {
    for(i = 0; i < len && token[i] == last_token[i]; i++);
    if(i == len) {
      printf("Duplicated");
      // duplicated message
      return;
    }
  }
  last_token_len = len;
  for(i = 0; i < len; i++) {
    last_token[i] = token[i];
  }*/ //FIXME andrea: this thing does not work anymore, returns always as duplicated
  

  len = REST.get_request_payload(request, &ptr);
  printf("A: %s\n", (char *)ptr);
  if(len > 9) {
    len = 9;
  }
  memcpy(setpoint, ptr, len);
  setpoint[len] = '\0';
}

/*----------------------------------------------------------------------------*/
void
actuator_get_handler(void *request, void *response, uint8_t *buffer,
                 uint16_t preferred_size, int32_t *offset)
{
  uint16_t len;

  len = strlen(setpoint);
  memcpy(buffer, setpoint, len);
  REST.set_header_content_type(response, REST.type.TEXT_PLAIN);
  REST.set_response_payload(response, buffer, len);
}

/*----------------------------------------------------------------------------*/
PROCESS_THREAD(tres_process, ev, data)
{
  PROCESS_BEGIN();

  srand(node_id);
  rest_init_engine();
  tres_init();
  rest_activate_resource(&actuator, "actuator");
  rplinfo_activate_resources();
  sprintf(setpoint, "0");
#if PYOT_KEEPALIVE
  static coap_packet_t request[1]; /* This way the packet can be treated as pointer as usual. */
  SERVER_NODE(&server_ipaddr);
  
  int wait_time = (unsigned int)(rand() % MAX_WAITING);
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
      coap_set_header_uri_path(request, "/rd");
      coap_set_payload(request, content, snprintf(content, sizeof(content), "%d", g_time++));
      //PRINT6ADDR(&server_ipaddr);
      //PRINTF(" : %u\n", UIP_HTONS(REMOTE_PORT));

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
#endif
  PROCESS_END();
}

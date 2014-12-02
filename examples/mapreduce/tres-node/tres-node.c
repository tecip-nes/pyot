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
#include "dev/light-sensor.h"
#include "contiki.h"
#include "node-id.h"
#include "erbium.h"
#include "tres.h"
#include "pm.h"
//#include "../rplinfo/rplinfo.h"
#include "../common/pyot.h"

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
uint8_t tres_start_monitoring(tres_res_t *tres);
uint8_t tres_stop_monitoring(tres_res_t *tres);
void task_is_add(tres_res_t *task, char *str);
void task_od_set(tres_res_t *task, char *str);
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
PROCESS(tres_process, "T-Res");

AUTOSTART_PROCESSES(&tres_process);

/* A simple getter example. Returns the reading from light sensor with a simple etag */
PERIODIC_RESOURCE(light, METHOD_GET, "sensors/light", "title=\"Light\";obs", 10*CLOCK_SECOND);
void
light_handler(void* request, void* response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
  uint16_t light_photosynthetic = light_sensor.value(LIGHT_SENSOR_PHOTOSYNTHETIC);
  uint16_t light_solar = light_sensor.value(LIGHT_SENSOR_TOTAL_SOLAR);

  const uint16_t *accept = NULL;
  int num = REST.get_header_accept(request, &accept);

  if ((num==0) || (num && accept[0]==REST.type.TEXT_PLAIN))
  {
    REST.set_header_content_type(response, REST.type.TEXT_PLAIN);
    snprintf((char *)buffer, REST_MAX_CHUNK_SIZE, "%u;%u", light_photosynthetic, light_solar);

    REST.set_response_payload(response, (uint8_t *)buffer, strlen((char *)buffer));
  }
  else
  {
    REST.set_response_status(response, REST.status.NOT_ACCEPTABLE);
    const char *msg = "no";
    REST.set_response_payload(response, msg, strlen(msg));
  }
}

void
light_periodic_handler(resource_t *r)
{
  uint16_t light_photosynthetic = light_sensor.value(LIGHT_SENSOR_PHOTOSYNTHETIC);
  static uint16_t obs_counter = 0;
  
  static char content[11];
  ++obs_counter;
  /* Build notification. */
  coap_packet_t notification[1]; /* This way the packet can be treated as pointer as usual. */
  coap_init_message(notification, COAP_TYPE_NON, REST.status.OK, 0 );
  coap_set_payload(notification, content, snprintf(content, sizeof(content), "%u", light_photosynthetic));

  /* Notify the registered observers with the given message type, observe option, and payload. */
  REST.notify_subscribers(r, obs_counter, notification);
}



/*----------------------------------------------------------------------------*/
PROCESS_THREAD(tres_process, ev, data)
{
  PROCESS_BEGIN();

  srand(node_id);
  rest_init_engine();
  tres_init();
  SENSORS_ACTIVATE(light_sensor);
  rest_activate_periodic_resource(&periodic_resource_light);  
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

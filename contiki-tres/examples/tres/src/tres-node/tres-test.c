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

#include "button.h"

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

/*----------------------------------------------------------------------------*/
PROCESS(tres_test_process, "T-Res Evaluation");

AUTOSTART_PROCESSES(&tres_test_process);

static uint16_t sensor_value = 0;

/*----------------------------------------------------------------------------*/
/*                            Fake sensor resource                            */
/*----------------------------------------------------------------------------*/
void sensor_periodic_handler(void);
void sensor_handler(void *request, void *response, uint8_t *buffer,
               uint16_t preferred_size, int32_t *offset);

PERIODIC_RESOURCE(sensor, "title=\"Fake generic sensor\";obs",
                 sensor_handler,
                 NULL,
                 NULL,
                 NULL,
                 TRES_EXAMPLE_SENSOR_PERIOD * CLOCK_SECOND, 
                 sensor_periodic_handler);

/*----------------------------------------------------------------------------*/
void
sensor_handler(void *request, void *response, uint8_t *buffer,
               uint16_t preferred_size, int32_t *offset)
{
  uint16_t len;
  char *str;

  str = (char *)buffer;
  sprintf(str, "%d", sensor_value);
  len = strlen(str);
  REST.set_header_content_type(response, REST.type.TEXT_PLAIN);
  REST.set_response_payload(response, buffer, len);
}

/*----------------------------------------------------------------------------*/
#if TRES_EXAMPLE_RANDOM_SENSOR_VALUE
static uint16_t
new_sensor_value()
{
  uint16_t tmp = rand();

  return tmp % 2000;
}
#else
static uint16_t
new_sensor_value()
{
  // never exceeds 4 digits
  if(sensor_value == 9999) {
    sensor_value = -1;
  }
  sensor_value++;
  return sensor_value;
}
#endif

/*----------------------------------------------------------------------------*/
void
sensor_periodic_handler(void)
{
  // we always want an obs_counter of 2 bytes, therefore we initialize it to 
  // 0xFF since it is immediately incremented by 1
  static uint16_t obs_counter = 0xFF;
  char str[10];
  uint16_t len;

  obs_counter++;
  sensor_value = new_sensor_value();
  len = snprintf(str, sizeof(str), "%04u", sensor_value);
  //printf("S: %s\n", str);
  /* Build notification. */
  coap_packet_t notification[1];

  coap_init_message(notification, COAP_TYPE_NON, CONTENT_2_05, 0);
  coap_set_payload(notification, str, len);
  /* Notify the registered observers with the given message type, 
   * observe option, and payload. */
  REST.notify_subscribers(&sensor);
  // we always want an obs_counter of 2 bytes
  if(obs_counter == 0xFFFF) {
    obs_counter = 0xFF;
  }
}



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
PROCESS_THREAD(tres_test_process, ev, data)
{
  PROCESS_BEGIN();

  srand(node_id);
  rest_init_engine();
  tres_init();
  rest_activate_resource(&sensor, "sensor");
  rest_activate_resource(&actuator, "actuator");
  tres_eval_init_button();

  PROCESS_END();
}

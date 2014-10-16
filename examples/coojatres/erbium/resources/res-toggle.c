/*
 * Copyright (c) 2013, Institute for Pervasive Computing, ETH Zurich
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
 *      Example resource
 * \author
 *      Matthias Kovatsch <kovatsch@inf.ethz.ch>
 */

#include "contiki.h"

#if PLATFORM_HAS_LEDS

#include <string.h>
#include "contiki.h"
#include "rest-engine.h"
#include "dev/leds.h"

static uint8_t toggle_status = 0;
#define STATUS_SIZE 4

static void res_set_handler(void *request, void *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void res_get_handler(void *request, void *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

/* A simple actuator example. Toggles the red led */
RESOURCE(res_toggle,
         "title=\"Red LED\";rt=\"Control\"",
         res_get_handler,
         res_set_handler,
         res_set_handler,
         NULL);

static void
res_set_handler(void *request, void *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
  size_t len = 0;
  const char *mode = NULL;   
  if ((len=REST.get_query_variable(request, "mode", &mode)))
  {
    printf("query ");
    if (strncmp(mode, "on", len)==0) 
    {
      printf("led on\n");
      toggle_status = 1;
      leds_on(LEDS_RED);            
    } else if (strncmp(mode, "off", len)==0) {
            printf("led off\n");
      toggle_status = 0;
            leds_off(LEDS_RED);
          }          
  }
  else{
    toggle_status ^= 1;
    leds_toggle(LEDS_ALL);
  }  
  snprintf((char *)buffer, REST_MAX_CHUNK_SIZE, "ok");
  REST.set_response_payload(response, buffer, strlen((char *)buffer));  
}


static void
res_get_handler(void *request, void *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
  char status[STATUS_SIZE];
  if (toggle_status){
    snprintf(status, STATUS_SIZE, "on");
  }
  else{
    snprintf(status, STATUS_SIZE, "off");
  }
    snprintf((char *)buffer, REST_MAX_CHUNK_SIZE, "%s", status);
  REST.set_response_payload(response, buffer, strlen((char *)buffer));
}


#endif /* PLATFORM_HAS_LEDS */

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
 *      Andrea Azzara' - <a.azzara@sssup.it>
 */

#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

#include "contiki.h"
#include "node-id.h"
#include "er-coap.h"
#include "tres.h"
#include "tres-interface.h"
#include "pm.h"
#include "powerlog.h"
#include "common-conf.h"

#define DEBUG 1
#if DEBUG
#define PRINTF(...) printf(__VA_ARGS__)
#define PRINT6ADDR(addr) PRINTF("[%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x]", ((uint8_t *)addr)[0], ((uint8_t *)addr)[1], ((uint8_t *)addr)[2], ((uint8_t *)addr)[3], ((uint8_t *)addr)[4], ((uint8_t *)addr)[5], ((uint8_t *)addr)[6], ((uint8_t *)addr)[7], ((uint8_t *)addr)[8], ((uint8_t *)addr)[9], ((uint8_t *)addr)[10], ((uint8_t *)addr)[11], ((uint8_t *)addr)[12], ((uint8_t *)addr)[13], ((uint8_t *)addr)[14], ((uint8_t *)addr)[15])
#define PRINTLLADDR(lladdr) PRINTF("[%02x:%02x:%02x:%02x:%02x:%02x]",(lladdr)->addr[0], (lladdr)->addr[1], (lladdr)->addr[2], (lladdr)->addr[3],(lladdr)->addr[4], (lladdr)->addr[5])
#else
#define PRINTF(...)
#define PRINT6ADDR(addr)
#define PRINTLLADDR(addr)
#endif

uint8_t tres_start_monitoring(tres_res_t *tres);
uint8_t tres_stop_monitoring(tres_res_t *tres);

uip_ipaddr_t server_ipaddr;
static struct etimer et;

PROCESS(tres_process, "T-Res Evaluation");
AUTOSTART_PROCESSES(&tres_process);

extern unsigned char usrlib_img[];

tres_res_t * t1 = NULL;

#define SENSOR_URI_1    "<coap://[aaaa::200:0:0:3]/sensors/light>"
#define SENSOR_URI_2    "<coap://[aaaa::200:0:0:4]/sensors/light>"
#define SENSOR_URI_3    "<coap://[aaaa::200:0:0:5]/sensors/light>"
#define SENSOR_URI_4    "<coap://[aaaa::200:0:0:f]/sensors/light>"

static void
init_tres_eval_resource()
{
  t1 = tres_add_task("vs", 1);
  t1->pf_img = usrlib_img;
  task_is_add(t1, SENSOR_URI_1);
  task_is_add(t1, SENSOR_URI_2);
#if defined THREEOUT
  task_is_add(t1, SENSOR_URI_3);
#elif defined FOUROUT
  PRINTF("Four outputs\n");
  task_is_add(t1, SENSOR_URI_3);
  task_is_add(t1, SENSOR_URI_4);
#endif
  t1->state_len = 0;
}

/*----------------------------------------------------------------------------*/
PROCESS_THREAD(tres_process, ev, data)
{
  PROCESS_BEGIN();

  srand(node_id);

#ifdef POWER_MEASURE
  power_log_start();
#endif //POWER_MEASURE

  rest_init_engine();
  tres_init();
  init_tres_eval_resource();
  etimer_set(&et, 20 * CLOCK_SECOND);
  while(1) {
    PROCESS_YIELD();
    if (etimer_expired(&et)) break;
  }
  tres_start_monitoring(t1);

  PROCESS_END();
}


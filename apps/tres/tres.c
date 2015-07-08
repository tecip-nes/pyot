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
 * \file
 *      Main functions for T-Res.
 *
 *      T-Res is described and evaluated in the paper "T-Res: enabling
 *      reprogrammable in-network processing in IoT-based WSNs",
 *      D. Alessandrelli, M. Petracca, and P. Pagano, in Proceedings of IEEE
 *      DCoSS 2013 Conference and Workshops.
 *
 * \author
 *      Daniele Alessandrelli - <d.alessandrelli@sssup.it>
 * \author
 *      Andrea Azzarà - <a.azzara@sssup.it>
 */


#include <string.h>
#include <stdlib.h>
#include "contiki.h"
#include "er-coap.h"
#include "pm.h"

#include "tres.h"
#include "tres-pymite.h"
#include "list_unrename.h"
#include "tres-interface.h"

#define DEBUG 1
#if DEBUG
#define PRINTF(...) printf(__VA_ARGS__)
#define PRINTFLN(format, ...) printf(format "\n", ##__VA_ARGS__)
#define PRINT6ADDR(addr) PRINTF("[%02x%02x:%02x%02x:%02x%02x:%02x%02x:"        \
                                 "%02x%02x:%02x%02x:%02x%02x:%02x%02x]",       \
                                ((uint8_t *)addr)[0], ((uint8_t *)addr)[1],    \
                                ((uint8_t *)addr)[2], ((uint8_t *)addr)[3],    \
                                ((uint8_t *)addr)[4], ((uint8_t *)addr)[5],    \
                                ((uint8_t *)addr)[6], ((uint8_t *)addr)[7],    \
                                ((uint8_t *)addr)[8], ((uint8_t *)addr)[9],    \
                                ((uint8_t *)addr)[10], ((uint8_t *)addr)[11],  \
                                ((uint8_t *)addr)[12], ((uint8_t *)addr)[13],  \
                                ((uint8_t *)addr)[14], ((uint8_t *)addr)[15])
#else
#define PRINTF(...)
#define PRINT6ADDR(addr)
#define PRINTFLN(...)
#endif


#define ERR_NONE 0
#define ERR_DATA_NONE_FREE -7
/*----------------------------------------------------------------------------*/
/*                              Global variables                              */
/*----------------------------------------------------------------------------*/

PROCESS(pf_process, "T-res processing function process");
PROCESS(periodic_output, "T-res periodic output manager");

static struct etimer et;
MEMB(idata_mem, tres_idata_t, TRES_DATA_MAX_NUMBER);

extern struct tres_pm_io_s tres_pm_io;

/// The heap for the Python VM. Make it far memory, dword-aligned.
static uint8_t heap[TRES_PM_HEAP_SIZE]
  __attribute__ ((aligned((2 * sizeof(int)))));

static process_event_t new_input_event;

/*----------------------------------------------------------------------------*/
/*                            Forward Declarations                            */
/*----------------------------------------------------------------------------*/
static tres_is_t *find_is(tres_res_t *task, coap_observee_t *obs);

/*----------------------------------------------------------------------------*/
/*                                Helper functions                            */
/*----------------------------------------------------------------------------*/
static tres_is_t *
find_is(tres_res_t *task, coap_observee_t *obs)
{
  tres_is_t *is;

  for(is = list_head(task->is_list); is != NULL; is = list_item_next(is)) {
    if(is->obs == obs) {
      return is;
    }
  }
  return NULL;
}

/*----------------------------------------------------------------------------*/
/*
static void 
print_byte_array(uint8_t *bytes, uint16_t len)
{
  uint32_t i;
  for (i = 0; i < len; i++) {
    PRINTF("%02X ", bytes[i]);
    if ((i % 8) == 7) {
      PRINTF("\n");
    } 
  }
  PRINTF("\n");
}
*/


/*----------------------------------------------------------------------------*/
static int
task_idata_add(tres_res_t *task, int16_t val)
{
  tres_idata_t *idata;

  idata = memb_alloc(&idata_mem);
  if(idata == NULL) {
	PRINTF("no more space in the list\n");
    return ERR_DATA_NONE_FREE;
  }
  idata->data=val;
  list_add(task->idata_list, idata);
  return ERR_NONE;
}

/*----------------------------------------------------------------------------*/
void new_input_data(tres_res_t *task, int16_t val){
  if (task->period == 0){
    process_post(&pf_process, new_input_event, task);
  }
  else{
    task_idata_add(task, val);
  }
}

/*----------------------------------------------------------------------------*/
static void
run_processing_func(tres_res_t *task)
{
  //PmReturn_t retval;

  //printf("F?\n");
  pm_init(heap, sizeof(heap), MEMSPACE_PROG, NULL);
  tres_pm_io.in = (char *)task->last_input;
  tres_pm_io.out = (char *)task->last_output;
  tres_pm_io.out[0] = '\0';
  tres_pm_io.tag = (char *)task->last_input_tag;
  tres_pm_io.output_set = 0;
  tres_pm_io.state = task->state;
  tres_pm_io.state_len = &task->state_len;
  tres_pm_io.od_count = list_length(task->od_list);
  LIST_STRUCT_INIT(&tres_pm_io, io_data_list);
  list_copy(tres_pm_io.io_data_list, task->idata_list);
  pm_run_from_img((uint8_t *)"pf", MEMSPACE_PROG, task->pf_img);
  //printf("F!\n");
  //PRINTF("Python finished, return of 0x%02x\n", retval);
}
#if TRES_RELIABLE
/* This function is will be passed to COAP_BLOCKING_REQUEST() to handle responses. */
static
void
client_chunk_handler(void *response)
{
  const uint8_t *chunk;

  int len = coap_get_payload(response, &chunk);

  printf("|%.*s", len, (char *)chunk);
}
#endif

/*----------------------------------------------------------------------------*/
PROCESS_THREAD(pf_process, ev, data)
{
  PROCESS_BEGIN();
  PRINTF("PF process\n");
  static tres_res_t *task;
  static tres_od_t *od;
  static coap_packet_t request[1];
  static uint8_t *token_ptr;
  static uint8_t token_len;
  new_input_event = process_alloc_event();
  while(1) {
    PROCESS_WAIT_EVENT_UNTIL(ev == new_input_event);
    task = (tres_res_t *)data;
    run_processing_func(task);
    if(tres_pm_io.output_set) {
      if(list_length(task->od_list) > 0) {
        PRINTF("od list len > 0, send output\n");
        for(od = list_head(task->od_list); od != NULL; od = list_item_next(od)) {
          PRINTFLN("--Requesting %s--", od->path);
          PRINT6ADDR(od->addr);

#if TRES_RELIABLE
          coap_init_message(request, COAP_TYPE_CON, COAP_PUT, coap_get_mid());
          coap_set_payload(request, task->last_output,
                           strlen((char *)task->last_output));
          token_len = coap_generate_token(&token_ptr);
          coap_set_token(request, token_ptr, token_len);
          coap_set_header_uri_path(request, od->path);
          PRINTF("RELIABLE SEND\n");
          COAP_BLOCKING_REQUEST(od->addr, TRES_REMOTE_PORT, request,
                                client_chunk_handler);
#else
          PRINTF("UNRELIABLE SEND\n");
          coap_init_message(request, COAP_TYPE_NON, COAP_PUT, coap_get_mid());
          coap_set_payload(request, task->last_output,
                           strlen((char *)task->last_output));
          token_len = coap_generate_token(&token_ptr);
          coap_set_token(request, token_ptr, token_len);
          coap_set_header_uri_path(request, od->path);
          static coap_transaction_t *t;
          if ((t = coap_new_transaction(request->mid, od->addr, TRES_REMOTE_PORT)))
          {
            t->packet_len = coap_serialize_message(request, t->packet);
            coap_send_transaction(t);
            PRINT6ADDR(od->addr);
            PRINTFLN();
            process_poll(&pf_process);
            PRINTF("EVENT %d\n", ev);
            PRINTF("YIELD\n");
            //PROCESS_YIELD_UNTIL(ev == PROCESS_EVENT_POLL);
            PROCESS_YIELD();
            PRINTF("AFTER YIELD\n");
            coap_clear_transaction(t);
          } else {
            PRINTF("Could not allocate transaction buffer");
          }
#endif
        }
        PRINTFLN("--Done--");
      }
      lo_event_handler(task);
    }
  }
  PROCESS_END();
}

/*----------------------------------------------------------------------------*/

PROCESS_THREAD(periodic_output, ev, data)
{
  PROCESS_BEGIN();
  
  etimer_set(&et, 1 * CLOCK_SECOND);
  int i;
  static tres_od_t *od;
  static coap_packet_t request[1];
  static uint8_t *token_ptr;
  static uint8_t token_len;  
  static tres_res_t *task;  
  while(1) {
    PROCESS_YIELD();
    if (etimer_expired(&et)) {
      struct memb* tasks = get_tasks_mem();
      for(i = 0; i < tasks->num; i++) {
        task = &tasks->mem[i];
        if (task->monitoring == 1 && task->period != 0){
          if (task->period <= task->ticks){
            int len = list_length(task->idata_list);
        	PRINTF("timer expired for %s, %d elem \n", task->name, len);
        	run_processing_func((tres_res_t *)task);

            if(tres_pm_io.output_set) {
              if(list_length(task->od_list) > 0) {
                PRINTF("od list len > 0, send output\n");
                for(od = list_head(task->od_list); od != NULL; od = list_item_next(od)) {
                  PRINTFLN("--Requesting %s--", od->path);
                  PRINT6ADDR(od->addr);
#if TRES_RELIABLE
                  coap_init_message(request, COAP_TYPE_CON, COAP_PUT, coap_get_mid());
                  coap_set_payload(request, task->last_output,
                                   strlen((char *)task->last_output));
                  token_len = coap_generate_token(&token_ptr);
                  coap_set_token(request, token_ptr, token_len);
                  coap_set_header_uri_path(request, od->path);
                  PRINTF("RELIABLE SEND\n");
                  COAP_BLOCKING_REQUEST(od->addr, TRES_REMOTE_PORT, request,
                                        client_chunk_handler);
#else
                  /*PRINTF("UNRELIABLE SEND\n");
                  coap_init_message(request, COAP_TYPE_NON, COAP_PUT, coap_get_mid());
                  coap_set_payload(request, task->last_output,
                                   strlen((char *)task->last_output));
                  token_len = coap_generate_token(&token_ptr);
                  coap_set_token(request, token_ptr, token_len);
                  coap_set_header_uri_path(request, od->path);
                  static coap_transaction_t *t;
                  if ((t = coap_new_transaction(request->mid, od->addr, TRES_REMOTE_PORT)))
                  {
                    t->packet_len = coap_serialize_message(request, t->packet);
                    coap_send_transaction(t);
                    PRINT6ADDR(od->addr);
                    PRINTFLN();
                    process_poll(&pf_process);
                    PRINTF("EVENT %d\n", ev);
                    PRINTF("YIELD\n");
                    //PROCESS_YIELD_UNTIL(ev == PROCESS_EVENT_POLL);
                    PROCESS_YIELD();
                    PRINTF("AFTER YIELD\n");
                    coap_clear_transaction(t);
                  } else {
                    PRINTF("Could not allocate transaction buffer");
                  }*/
#endif //TRES_RELIABLE
                }
                PRINTFLN("--Done--");
              }
              lo_event_handler(task);
            }
        	static tres_idata_t *idata;
        	idata = list_pop(task->idata_list);
        	while(idata) {
        	  memb_free(&idata_mem, idata);
        	  idata = list_pop(task->idata_list);
        	}
            task->ticks = 0;
          }
          else{
            task->ticks ++;
          }
        }
      }
    etimer_reset(&et);
    }
  } /* while (1) */
  PROCESS_END();
}

/*----------------------------------------------------------------------------*/
static void
is_notification_callback(coap_observee_t *obs, void *notification,
                         coap_notification_flag_t flag)
{
  int len = 0;
  tres_res_t *task;
  const uint8_t *payload = NULL;
  tres_is_t *is;
  int16_t val;

  PRINTF("Notification handler\n");
  PRINTF("Subject URI: %s\n", obs->url);
  task = obs->data;
  is = find_is(task, obs);
  if(notification) {
    len = coap_get_payload(notification, &payload);
  }
  switch (flag) {
  case NOTIFICATION_OK:
    PRINTF("NOTIFICATION OK: %*s\n", len, (char *)payload);
    if(len > REST_MAX_CHUNK_SIZE) {
      len = REST_MAX_CHUNK_SIZE;
    }
    memcpy(task->last_input, payload, len);
    task->last_input[len] = '\0';
    task->last_input_tag = is->tag;
    val = (int16_t)strtol((const char *)payload, NULL, 10);
    new_input_data(task, val);
    break;
  case OBSERVE_OK:
    PRINTF("OBSERVE_OK: %*s\n", len, (char *)payload);
    // ignore response and check whether we must observe additional input 
    // resources
    for(is = list_head(task->is_list); is != NULL; is = list_item_next(is)) {
      if(is->obs == NULL) {
        is->obs = coap_obs_request_registration(is->addr, TRES_REMOTE_PORT,
                                                is->path,
                                                is_notification_callback, task);
        return;
      }
    }
    break;
  case OBSERVE_NOT_SUPPORTED:
    printf("T-Res: ERROR: observe not supported\n");
    PRINTF("OBSERVE_NOT_SUPPORTED: %*s\n", len, (char *)payload);
    is->obs = NULL;
    break;
  case ERROR_RESPONSE_CODE:
    printf("T-Res: ERROR: error response to observe request\n");
    PRINTF("ERROR_RESPONSE_CODE: %*s\n", len, (char *)payload);
    is->obs = NULL;
    break;
  case NO_REPLY_FROM_SERVER:
    printf("T-Res: ERROR: not reply to observe request\n");
    PRINTF("NO_REPLY_FROM_SERVER: "
           "removing observe registration with token %x%x\n",
           obs->token[0], obs->token[1]);
    is->obs = NULL;
    break;
  }
}

/*----------------------------------------------------------------------------*/
// FIXME: change to static when T-Res evaluation is completed
//static uint8_t
uint8_t
tres_start_monitoring(tres_res_t *task)
{
  PRINTF("tres_start_monitoring()\n");
  tres_is_t *is;

  // check if input sources list is not empty
  if(list_length(task->is_list) == 0) {
    task->monitoring = 1;
    return 1;
  }
  // start monitoring input resources:
  // find first resource to observe and issue an observe request, that will 
  // cause a chain reaction causing all other sources to be observed as well, 
  // see is_handle_notification().
  for(is = list_head(task->is_list); is != NULL; is = list_item_next(is)) {
    if(is->obs == NULL) {
      is->obs = coap_obs_request_registration(is->addr, TRES_REMOTE_PORT,
                                              is->path,
                                              is_notification_callback, task);

    }
  }
  task->monitoring = 1;
  return 1;
}

/*----------------------------------------------------------------------------*/
// FIXME: change to static when T-Res evaluation is completed
//static uint8_t
uint8_t
tres_stop_monitoring(tres_res_t *task)
{
  PRINTF("tres_stop_monitoring()\n");
  tres_is_t *is;

  // stop monitoring input resource
  for(is = list_head(task->is_list); is != NULL; is = list_item_next(is)) {
    coap_obs_remove_observee(is->obs);
    is->obs = NULL;
  }
  task->monitoring = 0;
  return 1;
}

/*----------------------------------------------------------------------------*/
uint8_t
tres_toggle_monitoring(tres_res_t *task)
{
  PRINTF("tres_toggle_monitoring()\n");

  if(task->monitoring) {
    tres_stop_monitoring(task);
  } else {
    tres_start_monitoring(task);
  }
  return task->monitoring;
}

/*----------------------------------------------------------------------------*/
/*                                Global functions                            */
/*----------------------------------------------------------------------------*/
void
tres_init(void)
{
  tres_mem_init();

  tres_interface_init();

  process_start(&pf_process, NULL);
  process_start(&periodic_output, NULL);
}

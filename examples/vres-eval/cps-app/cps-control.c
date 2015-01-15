
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "contiki.h"
#include "contiki-net.h"
#include "../common/pyot.h"
#include "node-id.h"
#include "dev/serial-line.h"
#include "uart1.h"

#include "er-coap.h"
#include "er-coap-engine.h"
#include "er-coap-transactions.h"
#include "powerlog.h"

static uip_ipaddr_t server_ipaddr;
static struct etimer et;

static uip_ipaddr_t input_sensor;
static uip_ipaddr_t output_actuator;

static process_event_t new_input_event;

static int wait_completion = 0;
PROCESS(cpa_app, "CPS-APP");
PROCESS(cpa_va, "CPS-VA");
AUTOSTART_PROCESSES(&cpa_app);

static
void
client_chunk_handler_b(void *response)
{
  coap_packet_t * pkt = (coap_packet_t *) response;
  if (pkt->type == COAP_TYPE_ACK){
    //PRINTF("ACK VA\n");
    return;
  }
}


PROCESS_THREAD(cpa_va, ev, data){
  PROCESS_BEGIN();
  new_input_event = process_alloc_event();
  SERVER_NODE(&server_ipaddr);
  static coap_packet_t request[1];
  char out_msg[20];
  static uint8_t *token_ptr;
  static uint8_t token_len;
  PRINT6ADDR(&output_actuator);PRINTF(" : %u\n", UIP_HTONS(REMOTE_PORT));
  while(1) {
    PROCESS_YIELD();
    if(ev == new_input_event) {
      wait_completion = 1;
      coap_init_message(request, COAP_TYPE_CON, COAP_PUT, 0);
      coap_set_header_uri_path(request, "/tasks/va/in");
      int input = atoi((char *)data);
      int output = input *2;
      sprintf(out_msg, "%d", output);
      //PRINTF("Requesting Va Service %s\n", out_msg);
      coap_set_payload(request, (uint8_t *)out_msg, strlen(out_msg));
      token_len = coap_generate_token(&token_ptr);
      coap_set_token(request, token_ptr, token_len);
      sprintf(out_msg, "%u", output);
      coap_set_payload(request, (uint8_t *)out_msg, strlen(out_msg));
      //PRINTF("Requesting Output %d", j);
      //PRINT6ADDR(&output_actuators[j]);
      //PRINTF(": %u\n" , UIP_HTONS(REMOTE_PORT));
      COAP_BLOCKING_REQUEST(&output_actuator, REMOTE_PORT, request,
                            client_chunk_handler_b);
      wait_completion = 0;
    }
  }
  PROCESS_END();
}



/* This function is will be passed to COAP_BLOCKING_REQUEST() to handle
 * responses. */
static
void
client_chunk_handler_a(void *response)
{
  coap_packet_t * pkt = (coap_packet_t *) response;

  if (pkt->type == COAP_TYPE_ACK){
    //PRINTF("ACK VS\n");
  }
  const uint8_t *chunk;
  int len = coap_get_payload(response, &chunk);
  //PRINTF("RECEIVED RESPONSE from VS\n");
  process_post(&cpa_va, new_input_event, (process_data_t)chunk);
}



PROCESS_THREAD(cpa_app, ev, data)
{
  PROCESS_BEGIN();
  srand(node_id);

  uip_ip6addr(&input_sensor, HEXPREFIX, 0, 0, 0, 0x200, 0, 0, 6);
  uip_ip6addr(&output_actuator, HEXPREFIX, 0, 0, 0, 0x200, 0, 0, 13);

  /* Initialize Serial Line */
  uart1_set_input(serial_line_input_byte);
  serial_line_init();

  /* Initialize the REST engine. */
  rest_init_engine();
  SERVER_NODE(&server_ipaddr);

  static coap_packet_t request[1]; /* This way the packet can be treated as pointer as usual. */

  etimer_set(&et, 1 * CLOCK_SECOND);
  serial_line_init();
  static uint8_t monitoring = 0;
  process_start(&cpa_va, NULL);
  while(1) {
    PROCESS_YIELD();
    if(etimer_expired(&et)) {

      if (monitoring == 0) {
        etimer_reset(&et);
        continue;
      }

      /* powerlog measures */
      pl_switch();

      if (wait_completion == 0){
        PRINTF("T: \n");
        //PRINTF("Requesting Vs Input\n");
        coap_init_message(request, COAP_TYPE_CON, COAP_GET, 0);
        coap_set_header_uri_path(request, "/tasks/vs/lo");

        //PRINT6ADDR(&server_ipaddr);
        //PRINTF(" : %u\n", UIP_HTONS(REMOTE_PORT));

        COAP_BLOCKING_REQUEST(&input_sensor, REMOTE_PORT, request,
                              client_chunk_handler_a);
      }else{
        PRINTF("M: \n");
      }
      etimer_reset(&et);
    }
    if(ev == serial_line_event_message) {
      PRINTF("Switching monitoring\n");
      if (monitoring)
        monitoring = 0;
      else
        monitoring = 1;
    }
  }
  PROCESS_END();
}


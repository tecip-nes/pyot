
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

uip_ipaddr_t server_ipaddr;
static struct etimer et;

/* Example URIs that can be queried. */
#define NUMBER_OF_URLS 2

static process_event_t new_input_event;

PROCESS(cpa_app, "CPS-APP");
PROCESS(cpa_va, "CPS-VA");
AUTOSTART_PROCESSES(&cpa_app);

PROCESS_THREAD(cpa_va, ev, data){
	PROCESS_BEGIN();
	new_input_event = process_alloc_event();
	SERVER_NODE(&server_ipaddr);
	static coap_packet_t request[1];
	char out_msg[20];

    PRINT6ADDR(&server_ipaddr);
    PRINTF(" : %u\n", UIP_HTONS(REMOTE_PORT));
    while(1) {
      PROCESS_YIELD();
      if(ev == new_input_event) {
    	coap_init_message(request, COAP_TYPE_CON, COAP_PUT, 0);
		coap_set_header_uri_path(request, "/rd/act/inst");

		int input = atoi((char *)data);
        int output = input *2;
		sprintf(out_msg, "%d", output);
		PRINTF("Requesting Va Service %s\n", out_msg);
	    coap_set_payload(request, (uint8_t *)out_msg, strlen(out_msg));
	    coap_transaction_t *transaction;
	    //TODO: Coap Blocking reqs
	    request->mid = coap_get_mid();
	    if ((transaction = coap_new_transaction(request->mid, &server_ipaddr,
	    		REMOTE_PORT)))
	    {
		  transaction->packet_len = coap_serialize_message(request,
				  transaction->packet);
		  coap_send_transaction(transaction);
	    }
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
  const uint8_t *chunk;

  int len = coap_get_payload(response, &chunk);
  process_post(&cpa_va, new_input_event, (process_data_t)chunk);

}



PROCESS_THREAD(cpa_app, ev, data)
{
  PROCESS_BEGIN();
  srand(node_id);

  /* Initialize Serial Line */
  uart1_set_input(serial_line_input_byte);
  serial_line_init();

  /* Initialize the REST engine. */
  rest_init_engine();
  SERVER_NODE(&server_ipaddr);

  static coap_packet_t request[1]; /* This way the packet can be treated as pointer as usual. */

  etimer_set(&et, 5 * CLOCK_SECOND);
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
      PRINTF("Requesting Vs Input\n");
      coap_init_message(request, COAP_TYPE_CON, COAP_GET, 0);
      coap_set_header_uri_path(request, "/rd/templ/inst");

      PRINT6ADDR(&server_ipaddr);
      PRINTF(" : %u\n", UIP_HTONS(REMOTE_PORT));

      COAP_BLOCKING_REQUEST(&server_ipaddr, REMOTE_PORT, request,
                            client_chunk_handler_a);
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



#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "contiki.h"
#include "contiki-net.h"
#include "../common/pyot.h"
#include "node-id.h"
#include "dev/serial-line.h"
#include "list.h"
#include "er-coap.h"
#include "er-coap-engine.h"
#include "er-coap-transactions.h"
#include "uart1.h"

uip_ipaddr_t server_ipaddr;
static struct etimer et;

/* Example URIs that can be queried. */
#define NUMBER_OF_URLS 2

#define INPUT_SENSORS     3
#define OUTPUT_ACTUATORS  3


static process_event_t new_input_event;

static uip_ipaddr_t input_sensors[INPUT_SENSORS];
static uip_ipaddr_t output_actuators[OUTPUT_ACTUATORS];

/* Input Data List */
typedef struct input_data_s {
  struct input_data_s *next;
  uint16_t data;
} idata_t;

LIST(idata_list);
MEMB(idata_mem, idata_t, INPUT_SENSORS);


static
void init_addresses()
{
  uip_ip6addr(&input_sensors[0], HEXPREFIX, 0, 0, 0, 0x200, 0, 0, 3);
  uip_ip6addr(&input_sensors[1], HEXPREFIX, 0, 0, 0, 0x200, 0, 0, 4);
  uip_ip6addr(&input_sensors[2], HEXPREFIX, 0, 0, 0, 0x200, 0, 0, 5);

  uip_ip6addr(&output_actuators[0], HEXPREFIX, 0, 0, 0, 0x200, 0, 0, 3);
  uip_ip6addr(&output_actuators[1], HEXPREFIX, 0, 0, 0, 0x200, 0, 0, 4);
  uip_ip6addr(&output_actuators[2], HEXPREFIX, 0, 0, 0, 0x200, 0, 0, 5);
}

PROCESS(cpa_app, "CPS-APP");
PROCESS(cpa_va, "CPS-VA");
AUTOSTART_PROCESSES(&cpa_app, &cpa_va);

static
void
client_chunk_handler_b(void *response)
{
  return;
}

PROCESS_THREAD(cpa_va, ev, data){
  PROCESS_BEGIN();
  static coap_packet_t request[1];
  char out_msg[20];
  static uint8_t *token_ptr;
  static uint8_t token_len;
  static unsigned int output;
  static int j;
  static idata_t *r_data;
  while(1) {
    PROCESS_YIELD();
    if(ev == new_input_event) {

	  PRINTF("Cleaning List\n");
	  r_data = list_pop(idata_list);
	  while(r_data) {
	    memb_free(&idata_mem, r_data);
	    r_data = list_pop(idata_list);
	  }
	  output = ((unsigned int)rand()) % 100;
	  for (j=0; j< INPUT_SENSORS; j++){
	    coap_init_message(request, COAP_TYPE_CON, COAP_PUT, 0);
	    coap_set_header_uri_path(request, "/actuators/leds");
	    token_len = coap_generate_token(&token_ptr);
	    coap_set_token(request, token_ptr, token_len);
	    sprintf(out_msg, "%u", output);
	    PRINTF("Requesting Va Service %s\n", out_msg);
	    coap_set_payload(request, (uint8_t *)out_msg, strlen(out_msg));
	    PRINTF("Requesting Output %d", j);
	    PRINT6ADDR(&output_actuators[j]);
        PRINTF(": %u\n" , UIP_HTONS(REMOTE_PORT));
        COAP_BLOCKING_REQUEST(&output_actuators[j], REMOTE_PORT, request,
		                      client_chunk_handler_b);
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
  uint16_t val = 0;
  int i;
  const uint8_t *token;
  static uint8_t last_token_len = 0;
  static uint8_t last_token[COAP_TOKEN_LEN];
  coap_get_payload(response, &chunk);
  //printf("|%.*s\n", len, (char *)chunk);
  //process_post(&cpa_va, new_input_event, (process_data_t)chunk);
  size_t token_len = coap_get_token(response, &token);
  //PRINTF("token LEN = %d\n", token_len);
  if(last_token_len == token_len) {
    for(i = 0; i < token_len && token[i] == last_token[i]; i++);
    //PRINTF("%d %d\n", token[i], last_token[i]);
    if(i == token_len) {
      PRINTF("DUPLICATE DETECTED ******************************************\n");
      // duplicated message
      return;
    }
  }
  last_token_len = token_len;
  for(i = 0; i < token_len; i++) {
    last_token[i] = token[i];
  }

  val = atoi((const char *)chunk);
  //printf("%d\n", val);

  idata_t *new_data;
  new_data = memb_alloc(&idata_mem);
  if(new_data == NULL) {
	PRINTF("NO MORE SPACE TO ALLOCATE NEW DATA IN THE LIST\n");
    return;
  }
  new_data->data = val;
  list_add(idata_list, new_data);

  int list_len = list_length(idata_list);
  if (list_len == INPUT_SENSORS){
	  PRINTF("+++ PROCESS INPUT +++\n");
	  process_post_synch(&cpa_va, new_input_event, (process_data_t)chunk);
  }
}



PROCESS_THREAD(cpa_app, ev, data)
{
  PROCESS_BEGIN();
  srand(node_id);
  list_init(idata_list);
  init_addresses();
  /* Initialize Serial Line */
  uart1_set_input(serial_line_input_byte);
  serial_line_init();

  /* Initialize the REST engine. */
  rest_init_engine();
  new_input_event = process_alloc_event();
  static int j;
  static coap_packet_t request[1]; /* This way the packet can be treated as pointer as usual. */
  static uint8_t *token_ptr;
  static uint8_t token_len;

  etimer_set(&et, 1 * CLOCK_SECOND);
  serial_line_init();
  static uint8_t monitoring = 0;
  //process_start(&cpa_va, NULL);
  while(1) {
    PROCESS_YIELD();
    if(etimer_expired(&et)) {
      if (monitoring == 0) {
    	  etimer_reset(&et);
    	  continue;
      }
      for (j=0; j< INPUT_SENSORS; j++){

		  coap_init_message(request, COAP_TYPE_CON, COAP_GET, 0);
		  coap_set_header_uri_path(request, "/sensors/light");
		  token_len = coap_generate_token(&token_ptr);
		  coap_set_token(request, token_ptr, token_len);
		  PRINTF("Requesting Input %d", j);
		  PRINT6ADDR(&input_sensors[j]);
		  PRINTF(":%u\n" , UIP_HTONS(REMOTE_PORT));
		  COAP_BLOCKING_REQUEST(&input_sensors[j], REMOTE_PORT, request,
								client_chunk_handler_a);
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

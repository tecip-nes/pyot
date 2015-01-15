#include "powerlog.h"
#include "common-conf.h"
#include "contiki.h"
#include "dev/serial-line.h"
#include "uart1.h"
#include <stdio.h>

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

#ifdef POWER_MEASURE

void pl_switch(){
  /* Energest vars */
  static int s;
  static unsigned long int cpu_start, tx_start, lst_start;
  static unsigned long int cpu_end, tx_end, lst_end;
  static unsigned long int cpu_tdiff, tx_tdiff, lst_tdiff;

  if (s==0) {
    s = 1;
    //PRINTF("P: starting powerlog\n");
    energest_flush(); //?
    cpu_start = energest_type_time(ENERGEST_TYPE_CPU);
    tx_start = energest_type_time(ENERGEST_TYPE_TRANSMIT);
    lst_start = energest_type_time(ENERGEST_TYPE_LISTEN);
  } else {
    //PRINTF("P: stopping powerlog\n");
    energest_flush(); //?
    cpu_end = energest_type_time(ENERGEST_TYPE_CPU);
    tx_end = energest_type_time(ENERGEST_TYPE_TRANSMIT);
    lst_end = energest_type_time(ENERGEST_TYPE_LISTEN);

    cpu_tdiff = (cpu_end - cpu_start) / PW_RATIO;
    tx_tdiff = (tx_end - tx_start) / PW_RATIO;
    lst_tdiff = (lst_end - lst_start) / PW_RATIO;
    PRINTF("P: time" TIME_UNIT "cpu, tx, lst: %lu  %lu  %lu \n", cpu_tdiff, tx_tdiff, lst_tdiff);
    /* start again */
    energest_flush(); //?
    cpu_start = energest_type_time(ENERGEST_TYPE_CPU);
    tx_start = energest_type_time(ENERGEST_TYPE_TRANSMIT);
    lst_start = energest_type_time(ENERGEST_TYPE_LISTEN);
  }
}


PROCESS(powerlog_process, "Power log");

PROCESS_THREAD(powerlog_process, ev, data)
{
  PROCESS_BEGIN();



  while(1) {
    PROCESS_YIELD();
    if(ev == serial_line_event_message) {
      PRINTF("starting powerlog\n");
      break;
    }
  }
  
  static struct etimer et;
  etimer_set(&et, CLOCK_SECOND * 1);
  while (1) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));
    etimer_reset(&et);
    pl_switch();
  }
  PROCESS_END();
}

void power_log_start(){

  /* Initialize Serial Line */
  uart1_set_input(serial_line_input_byte);
  serial_line_init();

  /* powerlog process start */
  process_start(&powerlog_process, NULL);
}

#endif //POWER_MEASURE

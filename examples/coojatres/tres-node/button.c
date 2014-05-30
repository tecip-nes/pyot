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

#include <stdio.h>

#include "contiki.h"
#include "dev/button-sensor.h"

/*----------------------------------------------------------------------------*/
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


/*----------------------------------------------------------------------------*/
void tres_eval_toggle_monitoring(void);

/*----------------------------------------------------------------------------*/
PROCESS(button_process, "T-Res Eval button process");

/*----------------------------------------------------------------------------*/
PROCESS_THREAD(button_process, ev, data)
{
  PROCESS_BEGIN();

  PRINTFLN("button_process: process starting");
  SENSORS_ACTIVATE(button_sensor);
  while(1) {
    PROCESS_WAIT_EVENT_UNTIL(ev == sensors_event && data == &button_sensor);
    printf("Button!\n");
  }
  PROCESS_END();
}
/*----------------------------------------------------------------------------*/
void
tres_eval_init_button()
{
  process_start(&button_process, NULL);
}

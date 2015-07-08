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
 *      T-Res Storage for the Seedeye platform.
 *
 * \author
 *      Daniele Alessandrelli - <d.alessandrelli@sssup.it>
 */


#include <stdio.h>
#include <string.h>

#include "contiki.h"
#include "tres.h"

/*----------------------------------------------------------------------------*/
#define DEBUG 0

#if DEBUG
#define DBG_PRINTF printf
#else
#define DBG_PRINTF(...)
#endif

// Section size in byte
#define SEG_SIZE 0x200
#define NUM_SLOT TRES_TASK_MAX_NUMBER
#define SLOT_SIZE   (4 * SEG_SIZE)

#define SEC_START   (&memory[0][0])

#define SLOT_START_ADDR(id)    (&memory[id][0])
#define SLOT_END_ADDR(id)      (&memory[id+1][0])
#define SLOT_CUR_ADDR(id)      (cur[id])

/*----------------------------------------------------------------------------*/
static uint8_t used[NUM_SLOT];  // keeps track of used slots
static uint8_t* cur[NUM_SLOT]; // keeps track of current position in each slot
static uint8_t memory[NUM_SLOT][SEG_SIZE];

/*----------------------------------------------------------------------------*/
static inline int
find_free_slot(void)
{
  int i;

  DBG_PRINTF("find_free_slot()\n");
  for(i = 0; i < NUM_SLOT; i++) {
    if(!used[i]) {
      DBG_PRINTF("Slot ID: %d\n", i);
      return i;
    }
  }
  printf("T-Res: Mem: Error: no free slot available\n");
  return -1;
}

/*----------------------------------------------------------------------------*/
void
tres_mem_arch_init(void)
{
  int i;

  DBG_PRINTF("tres_mem_arch_init()\n");
  for(i = 0; i < NUM_SLOT; i++) {
    used[i] = 0;
  }
}

/*----------------------------------------------------------------------------*/
// returns the number of slot to be used or -1 if there are no free slots
int
tres_mem_arch_pf_store_start(void)
{
  int id;

  DBG_PRINTF("tres_mem_arch_pf_store_start()\n");
  id = find_free_slot();
  if(id >= 0) {
    cur[id] = SLOT_START_ADDR(id);
    used[id] = 1;
  }
  return id;
}

/*----------------------------------------------------------------------------*/
int
tres_mem_arch_pf_store_step(int id, const uint8_t * buf, int len)
{
  DBG_PRINTF("tres_mem_arch_pf_store_step()\n");
  // ensure that we don't exceed the slot limit 
  DBG_PRINTF("Len: %d\n", len);
  DBG_PRINTF("Cur: %x\n", cur[id]);
  DBG_PRINTF("SLOT_END_ADDR: %x\n", SLOT_END_ADDR(id));
  if(((SLOT_END_ADDR(id)) - cur[id]) < len) {
    return -1;
  }
  memcpy(cur[id], buf, len);
  cur[id] += len;

  return 0;
}

/*----------------------------------------------------------------------------*/
uint8_t *
tres_mem_arch_pf_store_done(int id)
{
  return (uint8_t *) SLOT_START_ADDR(id);
}

/*----------------------------------------------------------------------------*/
void
tres_mem_arch_pf_clear(uint8_t * ptr)
{
  int id;

  if(ptr < SEC_START) {
    printf("T-Res: Mem: Warning: invalid pointer passed to pf_clear()\n");
    return;
  }
  id = (ptr - SEC_START) / SLOT_SIZE;
  used[id] = 0;
}

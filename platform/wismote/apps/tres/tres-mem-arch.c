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
 *      T-Res Storage for the Wismote platform.
 *
 * \author
 *      Daniele Alessandrelli - <d.alessandrelli@sssup.it>
 */


#include <sys/crtld.h>
#include <stdio.h>

#include "contiki.h"
#include "dev/flash.h"
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

// _etext points to the end of .text + .rodata
#define TEXT_END ((uintptr_t) _etext)
#define SEC_START   (TEXT_END - (TEXT_END % SEG_SIZE) + SEG_SIZE)

#define SLOT_START_ADDR(id)    SEC_START + id * SLOT_SIZE
#define SLOT_END_ADDR(id)      SEC_START + (id + 1) * SLOT_SIZE
#define SLOT_CUR_ADDR(id)    cur[id]

/*----------------------------------------------------------------------------*/
static uint8_t used[NUM_SLOT];  // keeps track of used slots
static uintptr_t cur[NUM_SLOT]; // keeps track of current position in each slot

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
static inline void
clear_slot(id)
{
  uintptr_t ptr;
  int j;

  ptr = SLOT_START_ADDR(id);
  for(j = 0; j < SLOT_SIZE / SEG_SIZE; j++) {
    flash_clear((unsigned short *)(ptr + j * SEG_SIZE));
  }
}

/*----------------------------------------------------------------------------*/
void
tres_mem_arch_init(void)
{
  int i, n;

  DBG_PRINTF("tres_mem_arch_init()\n");
  DBG_PRINTF("SEC_START: %x\n", SEC_START);
  DBG_PRINTF("_etext: %x\n", TEXT_END);
  // Chech if we actually have space for NUM_SLOT slots
  // FIXME: the upper bound should not be hardcoded
  n = (0xfe00 - SEC_START) / SLOT_SIZE;
  if(n < NUM_SLOT) {
    printf("T-Res: Mem: Warning: not enough space for %d slots", NUM_SLOT);
    for(i = n; i < NUM_SLOT; i++) {
      used[i] = 1;
    }
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
    clear_slot(id);
    cur[id] = SLOT_START_ADDR(id);
    used[id] = 1;
  }
  return id;
}

/*----------------------------------------------------------------------------*/
int
tres_mem_arch_pf_store_step(int id, const uint8_t * buf, int len)
{
  int j;
  uint16_t tmp;
  uint8_t *tmp8;

  DBG_PRINTF("tres_mem_arch_pf_store_step()\n");
  // ensure that we don't exceed the slot limit 
  DBG_PRINTF("Len: %d\n", len);
  DBG_PRINTF("Cur: %x\n", cur[id]);
  DBG_PRINTF("SLOT_END_ADDR: %x\n", SLOT_END_ADDR(id));
  if(((SLOT_END_ADDR(id)) - cur[id]) < len) {
    return -1;
  }
  flash_setup();
  // write to flash
  tmp8 = (uint8_t *) &tmp;
  for(j = 0; j < len; j += 2) {
    // we need this because buf may be misaligned
    tmp8[0] = buf[j];
    // don't worry about possible buffer overflow in read mode
    tmp8[1] = buf[j + 1];
    DBG_PRINTF("Writing @%x\n", cur[id]);
    flash_write((unsigned short *)cur[id], tmp);
    cur[id] += 2;
  }
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

  if(ptr < (uint8_t *) SEC_START) {
    printf("T-Res: Mem: Warning: invalid pointer passed to pf_clear()\n");
    return;
  }
  id = ((uintptr_t) ptr - SEC_START) / SLOT_SIZE;
  used[id] = 0;
}

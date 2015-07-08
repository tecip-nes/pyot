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
 * This file is part of the Contiki operating system.
 *
 */

/**
 * \file
 *      Stack-overflow detection for the Wismote platform.
 *
 * \author
 *      Daniele Alessandrelli - <d.alessandrelli@sssup.it>
 */



#ifndef __STACK_OVERFLOW_WATCHER_H__
#define __STACK_OVERFLOW_WATCHER_H__


#ifndef STACK_OVERFLOW_DETECTION
#define STACK_OVERFLOW_DETECTION 0
#endif

#if STACK_OVERFLOW_DETECTION

#include "contiki-conf.h"

#define msp430_stack_overflow_watcher_init()
#define msp430_stack_overflow_watcher_check()

#else /* STACK_OVERFLOW_DETECTION */

#include <sys/crtld.h>
#include <stdint.h>
#include <stdio.h>

/*----------------------------------------------------------------------------*/
static inline void
msp430_stack_overflow_watcher_init()
{
  uint32_t *eos;

  eos = (uint32_t *)&__noinit_end;
  *eos = 0xDEADBEEF;
}

/*----------------------------------------------------------------------------*/
static inline void
msp430_stack_overflow_watcher_check()
{
  uint32_t *eos;

  eos = (uint32_t *)&__noinit_end;
  if(*eos != 0xDEADBEEF) {
    printf("\nWarning: STACK OVERFLOW detected!\n");
  }
}

#endif /* STACK_OVERFLOW_DETECTION */

#endif /* __STACK_OVERFLOW_WATCHER_H__ */

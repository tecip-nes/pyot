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
 *      T-Res Storage header file.
 *
 * \author
 *      Daniele Alessandrelli - <d.alessandrelli@sssup.it>
 */

#ifndef __TRES_MEM__H__
#define __TRES_MEM__H__

#include "tres-mem-arch.h"

/*----------------------------------------------------------------------------*/
/*typedef struct tres_mem_segment_s {
  uint8_t *start;
  uint8_t *current;
} tres_mem_state_t;
*/
/*----------------------------------------------------------------------------*/
static inline void
tres_mem_init(void)
{
  tres_mem_arch_init();
}

/*----------------------------------------------------------------------------*/
static inline int
tres_mem_pf_store_start(void)
{
  return tres_mem_arch_pf_store_start();
}

/*----------------------------------------------------------------------------*/
static inline int
tres_mem_pf_store_step(int id, const uint8_t *buf, int len)
{
  return tres_mem_arch_pf_store_step(id, buf, len);
}

/*----------------------------------------------------------------------------*/
static inline uint8_t *
tres_mem_pf_store_done(int id)
{
  return tres_mem_arch_pf_store_done(id);
}

/*----------------------------------------------------------------------------*/
static inline void
tres_mem_pf_clear(uint8_t *ptr)
{
  tres_mem_arch_pf_clear(ptr);
}

#endif /* __TRES_MEM__H__ */

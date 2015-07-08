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
 *      T-Res Python API: native functions.
 *
 * \author
 *      Daniele Alessandrelli - <d.alessandrelli@sssup.it>
 * \author
 *      Andrea Azzarà - <a.azzara@sssup.it>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

#include "contiki.h"
#include "er-coap.h"

#include "tres-pymite.h"
#include "tres.h"

#undef __FILE_ID__
#define __FILE_ID__ 0xDA

#define TRES_ERR_NONE 0
#define TRES_ERR_STATE_EMPTY -1
#define TRES_ERR_STATE_FULL -2

/*----------------------------------------------------------------------------*/
// This variable is needed to compile pymite, but it is actually useless in
// T-res
pPmNativeFxn_t const usr_nat_fxn_table[] = { };

tres_pm_io_t tres_pm_io;

/*----------------------------------------------------------------------------*/
float
simple_atof(char *str)
{
  char *endptr;
  float fval;
  long ldec;
  float fdec;

  fval = strtol(str, &endptr, 10);
  if(*endptr != '.') {
    return fval;
  }
  str = endptr + 1;
  ldec = strtol(str, &endptr, 10);
  if(ldec) {
    fdec = ldec;
    while(str < endptr) {
      fdec /= 10;
      str++;
    }
    fval += fdec;
  }
  return fval;
}


/*----------------------------------------------------------------------------*/
PmReturn_t
tres_pm_get_input_tag(pPmFrame_t *ppframe)
{
  PmReturn_t retv = PM_RET_OK;
  pPmObj_t r_pstring;
  char **paddr;

  paddr = &tres_pm_io.tag;
  retv = string_new(paddr, &r_pstring);
  NATIVE_SET_TOS(r_pstring);

  return retv;
}

/*----------------------------------------------------------------------------*/
PmReturn_t
tres_pm_set_output(pPmFrame_t *ppframe)
{
  const char *ptr;
  int32_t ival;
  float fval;
  PmReturn_t retv = PM_RET_OK;
  pPmObj_t pa;

  /* Raise TypeError if wrong number of args */
  if(NATIVE_GET_NUM_ARGS() != 1) {
    PM_RAISE(retv, PM_RET_EX_TYPE);
    return retv;
  }
  pa = NATIVE_GET_LOCAL(0);
  switch (OBJ_GET_TYPE(pa)) {
  case OBJ_TYPE_STR:
    ptr = (char const *)&(((pPmString_t) pa)->val);
    snprintf(tres_pm_io.out, REST_MAX_CHUNK_SIZE, "%s", ptr);
    break;
  case OBJ_TYPE_INT:
    ival = ((pPmInt_t) pa)->val;
    snprintf(tres_pm_io.out, REST_MAX_CHUNK_SIZE, "%" PRId32, ival);
    break;
  case OBJ_TYPE_FLT:
    fval = ((pPmFloat_t) pa)->val;
    // we cannot use snprintf: float are not supported
    //snprintf(tres_pm_io.out, REST_MAX_CHUNK_SIZE, "%f", fval);
    //therefore we use pymite sli_ftoa, which, however requires a buffer => 15
    if(REST_MAX_CHUNK_SIZE >= 15) {
      sli_ftoa(fval, (uint8_t *)tres_pm_io.out, REST_MAX_CHUNK_SIZE);
    }
    break;
  default:
    /* Raise TypeError */
    PM_RAISE(retv, PM_RET_EX_TYPE);
  }
  tres_pm_io.output_set = 1;
  NATIVE_SET_TOS(PM_NONE);

  return retv;
}

/*----------------------------------------------------------------------------*/
// FIXME: this function returns a string for now. Must be changed when JSON 
// will be used  
PmReturn_t
tres_pm_get_input(pPmFrame_t *ppframe)
{
  PmReturn_t retv = PM_RET_OK;
  pPmObj_t r_pstring;
  char **paddr;

  paddr = &tres_pm_io.in;
  retv = string_new(paddr, &r_pstring);
  NATIVE_SET_TOS(r_pstring);

  return retv;
}

/*----------------------------------------------------------------------------*/
// FIXME: this function will be be removed when JSON will be used 
PmReturn_t
tres_pm_get_int_input(pPmFrame_t *ppframe)
{
  PmReturn_t retv = PM_RET_OK;
  pPmObj_t r_pint;
  int32_t val;

  val = (int32_t)strtol(tres_pm_io.in, NULL, 10);
  retv = int_new(val, &r_pint);
  NATIVE_SET_TOS(r_pint);

  return retv;
}

/*----------------------------------------------------------------------------*/
// FIXME: this function will be be removed when JSON will be used 
PmReturn_t
tres_pm_get_float_input(pPmFrame_t *ppframe)
{
  PmReturn_t retv = PM_RET_OK;
  pPmObj_t r_pflt;
  float val;

  val = simple_atof(tres_pm_io.in);
  //val = (float) strtod(tres_pm_io.in, NULL);
  retv = float_new(val, &r_pflt);
  NATIVE_SET_TOS(r_pflt);

  return retv;
}

/*----------------------------------------------------------------------------*/
PmReturn_t
tres_pm_get_od_count(pPmFrame_t *ppframe)
{
  PmReturn_t retv = PM_RET_OK;
  pPmObj_t r_pint;
  retv = int_new(tres_pm_io.od_count, &r_pint);
  NATIVE_SET_TOS(r_pint);
  return retv;
}

/*----------------------------------------------------------------------------*/
PmReturn_t
tres_pm_get_input_list(pPmFrame_t *ppframe)
{
  pPmObj_t pl;
  pPmObj_t pi = C_NULL;
  PmReturn_t retv = PM_RET_OK;

  retv = list_new(&pl);
  PM_RETURN_IF_ERROR(retv);

  tres_idata_t *idata;
  for(idata = list_head(tres_pm_io.io_data_list);
	  idata != NULL;
	  idata = list_item_next(idata)) {
	retv = int_new(idata->data, &pi);
    PM_RETURN_IF_ERROR(retv);
    retv = list_append(pl, pi);
    PM_RETURN_IF_ERROR(retv);
  }
  NATIVE_SET_TOS(pl);
  return retv;
}

/*----------------------------------------------------------------------------*/
static int
pop_int(int32_t *val)
{
  if(*tres_pm_io.state_len < sizeof(*val)) {
    return TRES_ERR_STATE_EMPTY;
  }
  *tres_pm_io.state_len -= sizeof(*val);
  memcpy(val, tres_pm_io.state + *tres_pm_io.state_len, sizeof(*val));
  return TRES_ERR_NONE;
}

/*----------------------------------------------------------------------------*/
static int
pop_float(float *val)
{
  uint8_t *st_ptr;

  if(*tres_pm_io.state_len < sizeof(*val)) {
    return TRES_ERR_STATE_EMPTY;
  }
  *tres_pm_io.state_len -= sizeof(*val);
  st_ptr = tres_pm_io.state + *tres_pm_io.state_len;
  memcpy(val, st_ptr, sizeof(*val));
  return TRES_ERR_NONE;
}

/*----------------------------------------------------------------------------*/
PmReturn_t
tres_pm_get_state(pPmFrame_t *ppframe)
{
  PmReturn_t retv = PM_RET_OK;
  pPmObj_t pobj;
  pPmObj_t pobj_new;
  pPmInstance_t pcli;
  pPmDict_t pdict;
  int16_t index;
  float fval;
  int32_t ival;

  if(NATIVE_GET_NUM_ARGS() != 1) {
    PM_RAISE(retv, PM_RET_EX_TYPE);
    return retv;
  }
  pobj = NATIVE_GET_LOCAL(0);
  if(OBJ_GET_TYPE(pobj) != OBJ_TYPE_CLI) {
    PM_RAISE(retv, PM_RET_EX_TYPE);
    return retv;
  }
  pcli = (pPmInstance_t)pobj;
  pdict = pcli->cli_attrs;

  if(*tres_pm_io.state_len > 0) {
    // restore each attribute of the object
    for(index = pdict->length - 1; index >= 0; index--) {
      seglist_getItem(pdict->d_keys, index, &pobj);
      retv = seglist_getItem(pdict->d_vals, index, &pobj);
      PM_RETURN_IF_ERROR(retv);
      switch (OBJ_GET_TYPE(pobj)) {
      case OBJ_TYPE_INT:
        //pop int
        pop_int(&ival);
        retv = int_new(ival, &pobj_new);
        break;
      case OBJ_TYPE_FLT:
        //pop float
        pop_float(&fval);
        retv = float_new(fval, &pobj_new);
        break;
      default:
        /* Raise TypeError */
        PM_RAISE(retv, PM_RET_EX_TYPE);
      }
      if (retv == PM_RET_OK) {
        seglist_setItem(pdict->d_vals, pobj_new, index);
      }
    }
  }
  NATIVE_SET_TOS((pPmObj_t)pcli);
  return retv;
}

/*----------------------------------------------------------------------------*/
static void
push_int(uint32_t val)
{
  if((*tres_pm_io.state_len + sizeof(val)) > TRES_STATE_SIZE) {
    return;
  }
  memcpy(tres_pm_io.state + *tres_pm_io.state_len, &val, sizeof(val));
  *tres_pm_io.state_len += sizeof(val);
}

/*----------------------------------------------------------------------------*/
static void
push_float(float val)
{
  uint8_t *st_ptr;

  st_ptr = &tres_pm_io.state[*tres_pm_io.state_len];
  memcpy(st_ptr, &val, sizeof(val));
  *tres_pm_io.state_len += sizeof(val);
}


/*----------------------------------------------------------------------------*/
PmReturn_t
tres_pm_save_state(pPmFrame_t *ppframe)
{
  PmReturn_t retv = PM_RET_OK;
  pPmObj_t pobj;
  pPmInstance_t pcli;
  pPmDict_t pdict;
  uint16_t index;

  if(NATIVE_GET_NUM_ARGS() != 1) {
    PM_RAISE(retv, PM_RET_EX_TYPE);
    return retv;
  }
  pobj = NATIVE_GET_LOCAL(0);
  if(OBJ_GET_TYPE(pobj) != OBJ_TYPE_CLI) {
    PM_RAISE(retv, PM_RET_EX_TYPE);
    return retv;
  }
  pcli = (pPmInstance_t)pobj;
  pdict = pcli->cli_attrs;

  // store each attribute of the object
  for(index = 0; index < pdict->length; index++) {
    seglist_getItem(pdict->d_keys, index, &pobj);
    retv = seglist_getItem(pdict->d_vals, index, &pobj);
    PM_RETURN_IF_ERROR(retv);
    switch (OBJ_GET_TYPE(pobj)) {
    case OBJ_TYPE_INT:
      push_int(((pPmInt_t) pobj)->val);
      break;
    case OBJ_TYPE_FLT:
      push_float(((pPmFloat_t) pobj)->val);
      break;
    }
  }
  NATIVE_SET_TOS(PM_NONE);
  return retv;
}


/*----------------------------------------------------------------------------*/
PmReturn_t
tres_pm_state_push(pPmFrame_t *ppframe)
{
  //const char *ptr;
  int32_t ival;
  float fval;
  PmReturn_t retv = PM_RET_OK;
  pPmObj_t pa;

  /* Raise TypeError if wrong number of args */
  pa = NATIVE_GET_LOCAL(0);
  if(NATIVE_GET_NUM_ARGS() != 1) {
    PM_RAISE(retv, PM_RET_EX_TYPE);
    return retv;
  }
  switch (OBJ_GET_TYPE(pa)) {
    //case OBJ_TYPE_STR:
    //  ptr = (char const *)&(((pPmString_t)pa)->val);
    //  // TODO: unimplemented
    //  break;
  case OBJ_TYPE_INT:
    ival = ((pPmInt_t) pa)->val;
    push_int(ival);
    break;
  case OBJ_TYPE_FLT:
    fval = ((pPmFloat_t) pa)->val;
    push_float(fval);
    break;
  default:
    /* Raise TypeError */
    PM_RAISE(retv, PM_RET_EX_TYPE);
  }
  NATIVE_SET_TOS(PM_NONE);

  return retv;
}

/*----------------------------------------------------------------------------*/
PmReturn_t
tres_pm_state_pop(pPmFrame_t *ppframe)
{
  PmReturn_t retv = PM_RET_OK;
  pPmObj_t r_pflt;
  pPmObj_t pa;
  float fval;
  int32_t ival;
  int pop_retv;

  /* Raise TypeError if wrong number of args */
  pa = NATIVE_GET_LOCAL(0);
  if(NATIVE_GET_NUM_ARGS() != 1) {
    PM_RAISE(retv, PM_RET_EX_TYPE);
    return retv;
  }
  switch (OBJ_GET_TYPE(pa)) {
    //case OBJ_TYPE_STR:
    //  ptr = (char const *)&(((pPmString_t)pa)->val);
    //  // TODO: unimplemented
    //  break;
  case OBJ_TYPE_INT:
    pop_retv = pop_int(&ival);
    if(pop_retv != TRES_ERR_NONE) {
      ival = ((pPmInt_t) pa)->val;
    }
    retv = int_new(ival, &r_pflt);
    break;
  case OBJ_TYPE_FLT:
    pop_retv = pop_float(&fval);
    if(pop_retv != TRES_ERR_NONE) {
      fval = ((pPmFloat_t) pa)->val;
    }
    retv = float_new(fval, &r_pflt);
    break;
  default:
    /* Raise TypeError */
    PM_RAISE(retv, PM_RET_EX_TYPE);
  }
  NATIVE_SET_TOS(r_pflt);

  return retv;
}

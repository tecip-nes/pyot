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
 *      T-Res RESTful interface.
 *
 * \author
 *      Daniele Alessandrelli - <d.alessandrelli@sssup.it>
 * \author
 *      Andrea Azzarà - <a.azzara@sssup.it>
 */


#include <string.h>
#include <inttypes.h>
#include <stdlib.h>
#include "contiki.h"
#include "er-coap.h"
#include "pm.h"

#include "tres.h"
#include "tres-pymite.h"
#include "list_unrename.h"

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
//! Length of the tasks resource's path (including trailing '/', i.e., "tasks/")
#define BASE_LEN sizeof(TRES_BASE_PATH)
//! Length of the name of a task subresource (i.e., 'is', 'od', 'pf', and 'lo')
#define SUBRES_LEN (2 + 1)

/*!
 * The maximum size of coap URL without a path, i.e., coap://[addr]/, 
 * including the terminating character ('\0')
 */
#define BASE_URL_LEN 50

#define ERR_NONE 0
#define ERR_NAME_TOO_LONG -1
#define ERR_SUBRES_INVALID_LENGTH -2
#define ERR_IS_NONE_FREE -3
#define ERR_IS_INVALID_URL -4
#define ERR_IS_INVALID_TAG -5
#define ERR_OD_INVALID_URL -6

#define TAG_ATTR ";tag=\""

#define strstr_p(str, pattern) (strstr(str, pattern) ?  (strstr(str, pattern) + \
                               strlen(pattern)) : 0)
#define SET_RESPONSE_TEXT_PAYLOAD(response, text)                              \
                        REST.set_response_payload(response, text, strlen(text));

#define BLOCK_SPRINTF(str, strpos, bufpos, offset, pref_size, buffer)          \
              if (strpos + strlen(str) >= *offset) {                           \
                bufpos += snprintf((char *) buffer + bufpos,                   \
                                   pref_size - bufpos + 1, str +               \
                            ((*offset - strpos > 0) ? (*offset - strpos) : 0));\
                if (bufpos >= pref_size) {                                     \
                  break;                                                       \
                }                                                              \
              }                                                                \
              strpos += strlen(str);

/*----------------------------------------------------------------------------*/

MEMB(tasks_mem, tres_res_t, TRES_TASK_MAX_NUMBER);
MEMB(is_mem, tres_is_t, TRES_IS_MAX_NUMBER);
MEMB(od_mem, tres_od_t, TRES_OD_MAX_NUMBER);

/*----------------------------------------------------------------------------*/
/*                            Forward Declarations                            */
/*----------------------------------------------------------------------------*/
static inline void is_handler_get(void *request, void *response,
                                  uint8_t *buffer, uint16_t preferred_size,
                                  int32_t *offset, tres_res_t *task);

static inline void is_handler_put(void *request, void *response,
                                  uint8_t *buffer, uint16_t preferred_size,
                                  int32_t *offset, tres_res_t *task);

static inline void is_handler_post(void *request, void *response,
                                   uint8_t *buffer, uint16_t preferred_size,
                                   int32_t *offset, tres_res_t *task);

static inline void od_handler_get(void *request, void *response,
                                  uint8_t *buffer, uint16_t preferred_size,
                                  int32_t *offset, tres_res_t *task);

static inline void od_handler_put(void *request, void *response,
                                  uint8_t *buffer, uint16_t preferred_size,
                                  int32_t *offset, tres_res_t *task);

static inline void od_handler_post(void *request, void *response,
                                   uint8_t *buffer, uint16_t preferred_size,
                                   int32_t *offset, tres_res_t *task);


static char *parse_tag(char *tag, const char *buf, uint16_t max_len);

static char *parse_url(const char *url, uip_ipaddr_t *addr, char *path,
                       uint16_t path_max_len);

void task_name_handler(void *request, void *response, uint8_t *buffer,
                       uint16_t preferred_size, int32_t *offset,
                       const char *name, const char *subres);

void subres_handler(void *request, void *response, uint8_t *buffer,
                    uint16_t preferred_size, int32_t *offset,
                    const char *subres, tres_res_t *task);

void is_handler(void *request, void *response, uint8_t *buffer,
                uint16_t preferred_size, int32_t *offset, tres_res_t *task);

void od_handler(void *request, void *response, uint8_t *buffer,
                uint16_t preferred_size, int32_t *offset, tres_res_t *task);

void pf_handler(void *request, void *response, uint8_t *buffer,
                uint16_t preferred_size, int32_t *offset, tres_res_t *task);

void lo_handler(void *request, void *response, uint8_t *buffer,
                uint16_t preferred_size, int32_t *offset, tres_res_t *task);

void in_handler(void *request, void *response, uint8_t *buffer,
                uint16_t preferred_size, int32_t *offset, tres_res_t *task);

static inline int16_t create_coap_base_url(char *url, int16_t max_len,
                                          uip_ipaddr_t *addr);

static void task_reset_state(tres_res_t *task);


static void task_is_delete_all(tres_res_t *task);

/*----------------------------------------------------------------------------*/
/*                         T-Res data Helper functions                        */
/*----------------------------------------------------------------------------*/


struct memb* get_tasks_mem(void)
{
  return &tasks_mem;
}

/*----------------------------------------------------------------------------*/
/*!
 * \breif Init a task struct
 *
 * Initializes the is_list field of the task
 *
 * @param task - the task to be initialized
 */
static void
task_init(tres_res_t *task)
{
  LIST_STRUCT_INIT(task, is_list);
  LIST_STRUCT_INIT(task, od_list);
  LIST_STRUCT_INIT(task, idata_list);
  task_reset_state(task);
}

/*----------------------------------------------------------------------------*/
/*!
 * \breif Resets task state
 *
 * Resets the state of the task passed as argument
 *
 * @param task - the task the state of which must be reset
 */
static void
task_reset_state(tres_res_t *task)
{
  task->state_len = 0;
  task->ticks = 0;
}

/*----------------------------------------------------------------------------*/
tres_res_t *
tres_add_task(const char *name, uint16_t period)
{
  tres_res_t *task;

  PRINTF("tres_add_task()\n");
  task = memb_alloc(&tasks_mem);
  if(task != NULL) {
    memcpy(task->name, name, TRES_TASK_NAME_MAX_LEN);
    snprintf(task->lo_url, sizeof(task->lo_url), TRES_BASE_PATH "/%s/lo",
             task->name);
    task->last_output[0] = '\0';
    task->obs_count = 0;
    task->period = period;
    task_init(task);
  }

  return task;                  // TODO: handle error
}

/*----------------------------------------------------------------------------*/
static void
task_od_delete_all(tres_res_t *task)
{
  tres_od_t *od;

  tres_stop_monitoring(task);
  od = list_pop(task->od_list);
  while(od) {
    memb_free(&od_mem, od);
    od = list_pop(task->od_list);
  }
  task_reset_state(task);
}

/*----------------------------------------------------------------------------*/
void
tres_del_task(tres_res_t *task)
{
  list_t obs_list;
  coap_observer_t *obs, *cur;

  tres_stop_monitoring(task);
  task->name[0] = '\0';         // a null name marks a deleted task
  // remove subscribers if any
  // TODO: can we notify the subscriber in some way?
  obs_list = coap_get_observers();
  obs = (coap_observer_t *)list_head(obs_list);
  while(obs) {
    cur = obs;
    // next is set to NULL if the observer is removed, so we must save it here
    obs = obs->next;
    if(cur->url == task->lo_url
       || memcmp(cur->url, task->lo_url, strlen(cur->url)) == 0) {
      coap_remove_observer(cur);
    }
  }
  task_is_delete_all(task);
  task_od_delete_all(task);
  if(task->pf_img) {
    tres_mem_pf_clear(task->pf_img);
  }
  task_reset_state(task);
  memb_free(&tasks_mem, task);
}

/*----------------------------------------------------------------------------*/
tres_res_t *
tres_find_task(const char *name)
{
  tres_res_t *task, *retv;
  int i;

  retv = NULL;
  // FIXME: we are using MEMB internals, is this acceptable? 
  for(i = 0; i < tasks_mem.num; i++) {
    task = &tasks_mem_memb_mem[i];
    if(strcmp(task->name, name) == 0) {
      retv = task;
    }
  }

  return retv;
}

/*----------------------------------------------------------------------------*/
static int
task_od_add(tres_res_t *task, const char *str)
{
  tres_od_t *od;

  od = memb_alloc(&od_mem);
  if(od == NULL) {
    return ERR_IS_NONE_FREE;
  }
  str = parse_url(str, od->addr, od->path, TRES_PATH_LEN_MAX);
  if(str == NULL) {
    memb_free(&od_mem, od);
    return ERR_IS_INVALID_URL;
  }
  list_add(task->od_list, od);
  return ERR_NONE;
}

/*----------------------------------------------------------------------------*/
static int
task_is_add(tres_res_t *task, const char *str)
{
  tres_is_t *is;

  is = memb_alloc(&is_mem);
  if(is == NULL) {
    return ERR_IS_NONE_FREE;
  }
  str = parse_url(str, is->addr, is->path, TRES_PATH_LEN_MAX);
  if(str == NULL) {
    memb_free(&is_mem, is);
    return ERR_IS_INVALID_URL;
  }
  str = parse_tag(is->tag, str, TRES_TAG_MAX_LEN);
  if(str == NULL) {
    memb_free(&is_mem, is);
    return ERR_IS_INVALID_TAG;
  }
  PRINTF("TAG: %s\n", is->tag);
  list_add(task->is_list, is);
  return ERR_NONE;
}

/*----------------------------------------------------------------------------*/
static void
task_is_delete_all(tres_res_t *task)
{
  tres_is_t *is;

  tres_stop_monitoring(task);
  is = list_pop(task->is_list);
  while(is) {
    memb_free(&is_mem, is);
    is = list_pop(task->is_list);
  }
  task_reset_state(task);
}


/*----------------------------------------------------------------------------*/
static int
parse_tasks_path(const char *path, uint16_t len, char *name, char *subres)
{
  uint16_t pi;

  name[0] = '\0';
  subres[0] = '\0';
  // check if path is zero-terminated
  if(path[len - 1] == '\0') {
    len--;
  }
  // remove the trailing '/' if any
  if(path[len - 1] == '/') {
    len--;
  }
  PRINTF("path: %.*s\n", len, path);
  PRINTF("len: %d\n", len);
  if(len <= BASE_LEN) {
    // no task (and, therefore, no subres)
    return ERR_NONE;
  }
  for(pi = BASE_LEN; pi < len && path[pi] != '/'; pi++) {
    name[pi - BASE_LEN] = path[pi];
  }
  if(pi - BASE_LEN >= TRES_TASK_NAME_MAX_LEN) {
    // task name too long
    return ERR_NAME_TOO_LONG;
  }
  memcpy(name, &path[BASE_LEN], pi - BASE_LEN);
  name[pi - BASE_LEN] = '\0';
  if(pi == len) {
    // no subres
    return ERR_NONE;
  }
  // skip the '/' after the name
  pi++;
  if(len - pi != SUBRES_LEN - 1) {
    return ERR_SUBRES_INVALID_LENGTH;
  }
  memcpy(subres, &path[pi], SUBRES_LEN - 1);
  subres[SUBRES_LEN - 1] = '\0';
  return ERR_NONE;
}

/*----------------------------------------------------------------------------*/
/*                            General /tasks Resource                         */
/*----------------------------------------------------------------------------*/
void
tasks_handler(void *request, void *response, uint8_t *buffer,
              uint16_t preferred_size, int32_t *offset);

PARENT_RESOURCE(tasks, 
                "title=\"T-Res tasks index\";ct=40",
                tasks_handler,
                tasks_handler,
                tasks_handler,
                tasks_handler);


/*----------------------------------------------------------------------------*/
void
tasks_handler(void *request, void *response, uint8_t *buffer,
              uint16_t preferred_size, int32_t *offset)
{
  const char *path;
  char name[TRES_TASK_NAME_MAX_LEN];
  char subres[SUBRES_LEN];
  int len;
  int retv;

#if TRES_COPPER_WORKAROUND
  uint32_t num = 0;
  uint8_t more = 0;
  uint16_t size = 0;
  uint32_t b1_offset = 0;
  int i;
  tres_res_t *task;
  int32_t strpos = 0;
  int16_t bufpos = 0;

  if(coap_get_header_block1(request, &num, &more, &size, &b1_offset)
     && more == 0) {
    coap_set_header_block1(response, num, more, size);
  }
#endif

  len = REST.get_url(request, &path);
  retv = parse_tasks_path(path, len, name, subres);
  if(retv < 0) {
    PRINTF("Invalid path: %d\n", retv);
    REST.set_response_status(response, REST.status.BAD_REQUEST);
    return;
  }
  if(*name) {
    PRINTF("name: %s\n", name);
    task_name_handler(request, response, buffer, preferred_size, offset, name,
                      subres);
    return;
  }

  for(i = 0; i < tasks_mem.num; i++) {
    task = &tasks_mem_memb_mem[i];
    if(task->name[0]) {
      /* </tasks/[task_name] */
      if(strpos == 0) {
        BLOCK_SPRINTF("</" TRES_BASE_PATH "/", strpos, bufpos, offset,
                      preferred_size, buffer);
      } else {
        BLOCK_SPRINTF(",</" TRES_BASE_PATH "/", strpos, bufpos, offset,
                      preferred_size, buffer);
      }
      BLOCK_SPRINTF(task->name, strpos, bufpos, offset, preferred_size, buffer);
      BLOCK_SPRINTF(">;ct=40", strpos, bufpos, offset, preferred_size, buffer);
    }
  }
  REST.set_response_payload(response, buffer, bufpos);
  REST.set_header_content_type(response, APPLICATION_LINK_FORMAT);

  if(bufpos >= preferred_size || *offset > 0) {
    if(i == tasks_mem.num) {
      *offset = -1;
    } else {
      *offset += preferred_size;
    }
  }
}

/*----------------------------------------------------------------------------*/
void
task_name_handler(void *request, void *response, uint8_t *buffer,
                  uint16_t preferred_size, int32_t *offset, const char *name,
                  const char *subres)
{
  rest_resource_flags_t method;
  tres_res_t *task;
  int32_t strpos;
  int16_t bufpos;
  const char *query = NULL;
  size_t len = 0;
  uint16_t period = TRES_DEFAULT_EXECUTION_PERIOD;
  PRINTF("task_name_handler()\n");
  method = REST.get_method_type(request);
  task = tres_find_task(name);
  if(task == NULL) {
    if(method == METHOD_PUT) {
      if ((len=REST.get_query_variable(request, "per", &query))) {
        period = atoi(query);
        PRINTF("period = %d\n", period);
      }
      //create task,  if error return internal server error
      task = tres_add_task(name, period);
      if(task == NULL) {
        REST.set_response_status(response, REST.status.INTERNAL_SERVER_ERROR);
        return;
      } else {
        REST.set_response_status(response, REST.status.CREATED);
      }
    } else {                    // not a PUT request
      REST.set_response_status(response, REST.status.NOT_FOUND);
      return;
    }
  }
  if(subres[0]) {
    subres_handler(request, response, buffer, preferred_size, offset, subres,
                   task);
    return;
  }
  PRINTF("Method: %d\n", method);
  // handle request to task
  switch (method) {
  case METHOD_GET:
    // retrieve task information
    do {
      strpos = 0;
      bufpos = 0;
      /* </tasks/[task_name]>/is>, */
      BLOCK_SPRINTF("</" TRES_BASE_PATH "/", strpos, bufpos, offset,
                    preferred_size, buffer);
      BLOCK_SPRINTF(task->name, strpos, bufpos, offset, preferred_size, buffer);
      BLOCK_SPRINTF("/is>;ct=40,", strpos, bufpos, offset, preferred_size,
                    buffer);
      /* </tasks/[task_name]>/od>, */
      BLOCK_SPRINTF("</" TRES_BASE_PATH "/", strpos, bufpos, offset,
                    preferred_size, buffer);
      BLOCK_SPRINTF(task->name, strpos, bufpos, offset, preferred_size, buffer);
      BLOCK_SPRINTF("/od>;ct=40,", strpos, bufpos, offset, preferred_size,
                    buffer);
      /* </tasks/[task_name]>/pf>, */
      BLOCK_SPRINTF("</" TRES_BASE_PATH "/", strpos, bufpos, offset,
                    preferred_size, buffer);
      BLOCK_SPRINTF(task->name, strpos, bufpos, offset, preferred_size, buffer);
      BLOCK_SPRINTF("/pf>,", strpos, bufpos, offset, preferred_size, buffer);
      /* </tasks/[task_name]>/lo>;obs */
      BLOCK_SPRINTF("</" TRES_BASE_PATH "/", strpos, bufpos, offset,
                    preferred_size, buffer);
      BLOCK_SPRINTF(task->name, strpos, bufpos, offset, preferred_size, buffer);
      BLOCK_SPRINTF("/lo>;obs", strpos, bufpos, offset, preferred_size, buffer);
      /* </tasks/[task_name]>/in> */
      BLOCK_SPRINTF("</" TRES_BASE_PATH "/", strpos, bufpos, offset,
                    preferred_size, buffer);
      BLOCK_SPRINTF(task->name, strpos, bufpos, offset, preferred_size, buffer);
      BLOCK_SPRINTF("/in>;ct=40,", strpos, bufpos, offset, preferred_size, buffer);
    } while(0);
    REST.set_response_payload(response, buffer, bufpos);
    REST.set_header_content_type(response, REST.type.APPLICATION_LINK_FORMAT);
    /* if we need or we are using block-wise transfer */
    if(bufpos >= preferred_size || *offset > 0) {
      if(bufpos < preferred_size) {
        *offset = -1;
      } else {
        *offset += preferred_size;
      }
    }

    break;
  case METHOD_PUT:
    // put is already handled before to reduce code redundancy
    break;
  case METHOD_POST:
    if ((len=REST.get_query_variable(request, "op", &query))) {
      PRINTF("query");
      if (strncmp(query, "on", len)==0) {
        PRINTF("start");
        if(!task->monitoring) {
          tres_start_monitoring(task);
        }
        SET_RESPONSE_TEXT_PAYLOAD(response, "Task now running");
           
      } else if (strncmp(query, "off", len)==0) {
        PRINTF("start");
        if(task->monitoring) {
          tres_stop_monitoring(task);
        }
        SET_RESPONSE_TEXT_PAYLOAD(response, "Task now halted");        
      }          
    }
    else{
      // toggle task activation
      if(tres_toggle_monitoring(task)) {
        SET_RESPONSE_TEXT_PAYLOAD(response, "Task now running");
      } else {
        SET_RESPONSE_TEXT_PAYLOAD(response, "Task now halted");
      }
    }
    break;
  case METHOD_DELETE:
    tres_del_task(task);
    REST.set_response_status(response, REST.status.DELETED);
    break;
  case HAS_SUB_RESOURCES:
    // dummy method
    break;
  default:
    break;    
  }
}

/*----------------------------------------------------------------------------*/
void
subres_handler(void *request, void *response, uint8_t *buffer,
               uint16_t preferred_size, int32_t *offset, const char *subres,
               tres_res_t *task)
{
  PRINTF("subres_handler()\n");
  if(strcmp(subres, "is") == 0) {
    is_handler(request, response, buffer, preferred_size, offset, task);
  } else if(strcmp(subres, "od") == 0) {
    od_handler(request, response, buffer, preferred_size, offset, task);
  } else if(strcmp(subres, "pf") == 0) {
    pf_handler(request, response, buffer, preferred_size, offset, task);
  } else if(strcmp(subres, "lo") == 0) {
    lo_handler(request, response, buffer, preferred_size, offset, task);
  } else if(strcmp(subres, "in") == 0) {
    in_handler(request, response, buffer, preferred_size, offset, task);
  } else {
    REST.set_response_status(response, REST.status.NOT_FOUND);
  }
}

/*----------------------------------------------------------------------------*/
/*                          Input Source Resoruce                             */
/*----------------------------------------------------------------------------*/
//RESOURCE(is, METHOD_GET | METHOD_POST | METHOD_PUT, "tasks/t1/is",             
//         "title=\"The input soruces for task 1\";rt=\"Text\"");


/*----------------------------------------------------------------------------*/
void
od_handler(void *request, void *response, uint8_t *buffer,
           uint16_t preferred_size, int32_t *offset, tres_res_t *task)
{
  rest_resource_flags_t method;

  method = REST.get_method_type(request);
  switch (method) {
  case METHOD_GET:
    od_handler_get(request, response, buffer, preferred_size, offset, task);
    break;
  case METHOD_PUT:
    od_handler_put(request, response, buffer, preferred_size, offset, task);
    break;
  case METHOD_POST:
    od_handler_post(request, response, buffer, preferred_size, offset, task);
    break;
  case METHOD_DELETE:
    task_od_delete_all(task);
    REST.set_response_status(response, REST.status.DELETED);
    break;
  case HAS_SUB_RESOURCES:
    // TODO
    break;
  default:
    break;
  }
}

/*----------------------------------------------------------------------------*/
static void
od_handler_get(void *request, void *response, uint8_t *buffer,
               uint16_t preferred_size, int32_t *offset, tres_res_t *task)
{
  tres_od_t *od;
  char base_url[BASE_URL_LEN];
  int32_t strpos;
  int16_t bufpos;

  PRINTF("od_handler_get()\n");
  strpos = 0;
  bufpos = 0;
  for(od = list_head(task->od_list); od != NULL; od = list_item_next(od)) {
    if(strpos == 0) {
      BLOCK_SPRINTF("<", strpos, bufpos, offset, preferred_size, buffer);
    } else {
      BLOCK_SPRINTF(",<", strpos, bufpos, offset, preferred_size, buffer);
    }
    create_coap_base_url(base_url, BASE_URL_LEN, od->addr);
    BLOCK_SPRINTF(base_url, strpos, bufpos, offset, preferred_size, buffer);
    BLOCK_SPRINTF(od->path, strpos, bufpos, offset, preferred_size, buffer);
    BLOCK_SPRINTF(">", strpos, bufpos, offset, preferred_size, buffer);
  }
  REST.set_response_payload(response, buffer, bufpos);
  REST.set_header_content_type(response, APPLICATION_LINK_FORMAT);
  if(bufpos >= preferred_size || *offset > 0) {
    if(od == NULL) {
      *offset = -1;
    } else {
      *offset += preferred_size;
    }
  }
}

/*----------------------------------------------------------------------------*/
static void
od_handler_post(void *request, void *response, uint8_t *buffer,
                uint16_t preferred_size, int32_t *offset, tres_res_t *task)
{
  const char *ptr;
  int retv;

  REST.get_request_payload(request, (const uint8_t **)&ptr);
  PRINTF("Req str len = %u\n", (unsigned int)strlen(ptr));
  retv = task_od_add(task, ptr);
  if(retv == ERR_NONE) {
    REST.set_response_status(response, REST.status.CHANGED);
    return;
  }
  if(retv == ERR_IS_INVALID_URL) {
    REST.set_response_status(response, REST.status.BAD_REQUEST);
    return;
  }
  if(retv == ERR_IS_NONE_FREE) {
    REST.set_response_status(response, REST.status.INTERNAL_SERVER_ERROR);
    return;
  }
}

/*----------------------------------------------------------------------------*/
static void
od_handler_put(void *request, void *response, uint8_t *buffer,
               uint16_t preferred_size, int32_t *offset, tres_res_t *task)
{
  uint16_t len;
  const char *ptr;
  int retv;

  len = REST.get_request_payload(request, (const uint8_t **)&ptr);
  PRINTF("Req str len = %u\n", (unsigned int)strlen(ptr));
  PRINTF("Req len = %d\n", len);
  task_od_delete_all(task);
  if(len != 0) {
    retv = task_od_add(task, ptr);
    if(retv == ERR_NONE) {
      REST.set_response_status(response, REST.status.CHANGED);
      return;
    }
    if(retv == ERR_IS_INVALID_URL) {
      REST.set_response_status(response, REST.status.BAD_REQUEST);
      return;
    }
    if(retv == ERR_IS_NONE_FREE) {
      REST.set_response_status(response, REST.status.INTERNAL_SERVER_ERROR);
      return;
    }
  }
}

/*----------------------------------------------------------------------------*/
void
is_handler(void *request, void *response, uint8_t *buffer,
           uint16_t preferred_size, int32_t *offset, tres_res_t *task)
{
  rest_resource_flags_t method;

  method = REST.get_method_type(request);
  switch (method) {
  case METHOD_GET:
    is_handler_get(request, response, buffer, preferred_size, offset, task);
    break;
  case METHOD_PUT:
    is_handler_put(request, response, buffer, preferred_size, offset, task);
    break;
  case METHOD_POST:
    is_handler_post(request, response, buffer, preferred_size, offset, task);
    break;
  case METHOD_DELETE:
    task_is_delete_all(task);
    REST.set_response_status(response, REST.status.DELETED);
    break;
  case HAS_SUB_RESOURCES:
    // TODO
    break;
  default:
    break;      
  }
}

/*----------------------------------------------------------------------------*/
static void
is_handler_get(void *request, void *response, uint8_t *buffer,
               uint16_t preferred_size, int32_t *offset, tres_res_t *task)
{
  tres_is_t *is;
  char base_url[BASE_URL_LEN];
  int32_t strpos;
  int16_t bufpos;

  PRINTF("is_handler_get()\n");
  strpos = 0;
  bufpos = 0;
  for(is = list_head(task->is_list); is != NULL; is = list_item_next(is)) {
    if(strpos == 0) {
      BLOCK_SPRINTF("<", strpos, bufpos, offset, preferred_size, buffer);
    } else {
      BLOCK_SPRINTF(",<", strpos, bufpos, offset, preferred_size, buffer);
    }
    create_coap_base_url(base_url, BASE_URL_LEN, is->addr);
    BLOCK_SPRINTF(base_url, strpos, bufpos, offset, preferred_size, buffer);
    BLOCK_SPRINTF(is->path, strpos, bufpos, offset, preferred_size, buffer);
    BLOCK_SPRINTF(">", strpos, bufpos, offset, preferred_size, buffer);
    if(is->tag[0] != '\0') {
      BLOCK_SPRINTF(TAG_ATTR, strpos, bufpos, offset, preferred_size, buffer);
      BLOCK_SPRINTF(is->tag, strpos, bufpos, offset, preferred_size, buffer);
      BLOCK_SPRINTF("\"", strpos, bufpos, offset, preferred_size, buffer);
    }
  }
  REST.set_response_payload(response, buffer, bufpos);
  REST.set_header_content_type(response, APPLICATION_LINK_FORMAT);
  if(bufpos >= preferred_size || *offset > 0) {
    if(is == NULL) {
      *offset = -1;
    } else {
      *offset += preferred_size;
    }
  }
}

/*----------------------------------------------------------------------------*/
static void
is_handler_post(void *request, void *response, uint8_t *buffer,
                uint16_t preferred_size, int32_t *offset, tres_res_t *task)
{
  const char *ptr;
  int retv;

  REST.get_request_payload(request, (const uint8_t **)&ptr);
  PRINTF("Req str len = %u\n", (unsigned int)strlen(ptr));
  retv = task_is_add(task, ptr);
  if(retv == ERR_NONE) {
    REST.set_response_status(response, REST.status.CHANGED);
    return;
  }
  if(retv == ERR_IS_INVALID_URL || retv == ERR_IS_INVALID_TAG) {
    REST.set_response_status(response, REST.status.BAD_REQUEST);
    return;
  }
  if(retv == ERR_IS_NONE_FREE) {
    REST.set_response_status(response, REST.status.INTERNAL_SERVER_ERROR);
    return;
  }
}

/*----------------------------------------------------------------------------*/
static void
is_handler_put(void *request, void *response, uint8_t *buffer,
               uint16_t preferred_size, int32_t *offset, tres_res_t *task)
{
  uint16_t len;
  const char *ptr;
  int retv;

  len = REST.get_request_payload(request, (const uint8_t **)&ptr);
  PRINTF("Req str len = %u\n", (unsigned int)strlen(ptr));
  PRINTF("Req len = %d\n", len);
  task_is_delete_all(task);
  if(len != 0) {
    retv = task_is_add(task, ptr);
    if(retv == ERR_NONE) {
      REST.set_response_status(response, REST.status.CHANGED);
      return;
    }
    if(retv == ERR_IS_INVALID_URL || retv == ERR_IS_INVALID_TAG) {
      REST.set_response_status(response, REST.status.BAD_REQUEST);
      return;
    }
    if(retv == ERR_IS_NONE_FREE) {
      REST.set_response_status(response, REST.status.INTERNAL_SERVER_ERROR);
      return;
    }
  }
}


/*----------------------------------------------------------------------------*/
/*                         Processing Function Resoruce                       */
/*----------------------------------------------------------------------------*/
//RESOURCE(pf, METHOD_GET | METHOD_POST | METHOD_PUT | METHOD_DELETE,
//   "tasks/t1/pf", "title=\"The processing function for task 1\";rt=\"Text\"");

/*----------------------------------------------------------------------------*/
void
pf_handler(void *request, void *response, uint8_t *buffer,
           uint16_t preferred_size, int32_t *offset, tres_res_t *task)
{
  rest_resource_flags_t method;
  uint32_t num = 0;
  uint8_t more = 0;
  uint16_t size = 0;
  uint32_t b1_offset = 0;
  uint16_t plen;
  const uint8_t *payload;

  method = REST.get_method_type(request);
  PRINTF("Method %d\n", method);
  switch (method) {
  case METHOD_GET:
    //TODO: retrieve python bytecode
    REST.set_response_status(response, REST.status.NOT_IMPLEMENTED);
    break;
  case METHOD_PUT:
    if(coap_get_header_block1(request, &num, &more, &size, &b1_offset)) {
      coap_set_header_block1(response, num, more, size);
    }

    PRINTF("Request on /pf: num = %"PRIu32", more = %"PRIu8", size = %"PRIu16
        ", offset = %"PRIu32"\n", num, more, size, b1_offset);
    // if it's the first packet, stop input resource monitoring
    if(b1_offset == 0) {
      tres_stop_monitoring(task);
      // if the user is actually updating the PF, clear it first
      if(task->pf_img) {
        tres_mem_pf_clear(task->pf_img);
        task_reset_state(task);
      }
    }
    plen = coap_get_payload(request, &payload);
    PRINTF("Payload len: %d\n", plen);
#if TRES_COPPER_WORKAROUND
    // if no block-wise transfer and payload len equal to maximum size, then
    // we probably need block wise transfer. FIXME: that may be not true
    if(size == 0 && plen == REST_MAX_CHUNK_SIZE) {
      more = 1;
      size = REST_MAX_CHUNK_SIZE;
      coap_set_header_block1(response, num, more, size);
    }
#endif
    // if it's the first packet, allocate a memory slot
    if(b1_offset == 0) {
      // ... but, if the first byte is not 0x0a than it is not python bytecode
      if(payload[0] != 0x0a) {
        PRINTF("First byte MUST be 0a\n");
        REST.set_response_status(response, REST.status.BAD_REQUEST);
        return;
      }
      task->sid = tres_mem_pf_store_start();
      if(task->sid < 0) {
        PRINTF("No memory slot available\n");
        // TODO: we should return a server error code
        return;
      }
    }
    // store the current block
    if(tres_mem_pf_store_step(task->sid, payload, plen) < 0) {
      PRINTF("PF too big\n");
      return;
    }
    // if it's the final block, finalize the memory slot
    if(more == 0) {
      task->pf_img = tres_mem_pf_store_done(task->sid);
      PRINTF("task->pf_img: %p\n", task->pf_img);
      REST.set_response_status(response, REST.status.CHANGED);
    }
    break;
  case METHOD_POST:
    REST.set_response_status(response, REST.status.METHOD_NOT_ALLOWED);
    break;
  case METHOD_DELETE:
    if(task->pf_img) {
      tres_stop_monitoring(task);
      tres_mem_pf_clear(task->pf_img);
      task_reset_state(task);
      task->pf_img = NULL;
    }
    REST.set_response_status(response, REST.status.DELETED);
    break;
  default:
    break;
  }
}

/*----------------------------------------------------------------------------*/
/*                             Last Output Resoruce                           */
/*----------------------------------------------------------------------------*/
void
lo_handler(void *request, void *response, uint8_t *buffer,
           uint16_t preferred_size, int32_t *offset, tres_res_t *task)
{
  rest_resource_flags_t method;
  resource_t r[1];
  int len;

  method = REST.get_method_type(request);
  if(method != METHOD_GET) {
    REST.set_response_status(response, REST.status.METHOD_NOT_ALLOWED);
    return;
  }
  len = strlen((char *)task->last_output);
  REST.set_response_payload(response, task->last_output, len);

  r->url = task->lo_url;
  coap_observe_handler(r, request, response);
}

/*----------------------------------------------------------------------------*/
/*                             Input Resoruce                                 */
/*----------------------------------------------------------------------------*/
void
in_handler(void *request, void *response, uint8_t *buffer,
           uint16_t preferred_size, int32_t *offset, tres_res_t *task)
{
  rest_resource_flags_t method;
  const uint8_t *payload;
  int len;
  int16_t val;
  method = REST.get_method_type(request);
  if(method != METHOD_PUT) {
    REST.set_response_status(response, REST.status.METHOD_NOT_ALLOWED);
    return;
  }
  len = coap_get_payload(request, &payload);
  if(len > 0){
	memcpy(task->last_input, payload, len);
	task->last_input[len] = '\0';
	val = (int16_t)strtol((const char *)payload, NULL, 10);
	new_input_data(task, val);
	REST.set_response_status(response, REST.status.CHANGED);
	return;
  }
  REST.set_response_status(response, REST.status.BAD_REQUEST);
}

/*----------------------------------------------------------------------------*/
void
lo_event_handler(tres_res_t *task)
{
  coap_packet_t notification[1];
  resource_t r;
  int len;

  // Build notification
  coap_init_message(notification, COAP_TYPE_CON, REST.status.OK, 0);
  len = strlen((char *)task->last_output);
  coap_set_payload(notification, task->last_output, len);

  // Notify the registered observers with the given message type, observe
  // option, and payload
  r.url = task->lo_url;
  task->obs_count++;
  //REST.notify_subscribers(&r, task->obs_count, notification);
  REST.notify_subscribers(&r); //TODO andrea: check this!!
}
/*----------------------------------------------------------------------------*/

void
tres_interface_init(void)
{
  rest_activate_resource(&tasks, TRES_BASE_PATH);
}


/*----------------------------------------------------------------------------*/
/*                        HELPER FUNCTIONS                                    */
/*----------------------------------------------------------------------------*/
typedef enum {
  ZG_NOT_DONE,
  ZG_IN_PROGESS,
  ZG_ALREADY_DONE
} zerogrouping_t;

static int16_t
create_coap_base_url(char *url, int16_t max_len, uip_ipaddr_t *addr)
{
  int16_t pos;
  int16_t len;
  int i;
  zerogrouping_t zg;

  zg = ZG_NOT_DONE;
  pos = snprintf(url, max_len, "coap://[");
  len = (max_len - pos > 0) ? max_len - pos : 0;
  for(i = 0; i < 7; i++) {
    if(addr->u16[i] || zg == 2) {
      pos += snprintf(url + pos, len, "%x:", UIP_HTONS(addr->u16[i]));
      if(zg == ZG_IN_PROGESS) {
        zg = ZG_ALREADY_DONE;
      }
    } else if(zg == ZG_NOT_DONE) {
      zg = ZG_IN_PROGESS;
      if(i == 0) {
        pos += snprintf(url + pos, len, "::");
      } else {
        pos += snprintf(url + pos, len, ":");
      }
    }
    len = (max_len - pos > 0) ? max_len - pos : 0;
  }
  pos += snprintf(url + pos, len, "%x]/", UIP_HTONS(addr->u16[7]));
  len = (max_len - pos > 0) ? max_len - pos : 0;

  return pos;
}



/*----------------------------------------------------------------------------*/
static char *
parse_tag(char *tag, const char *buf, uint16_t max_len)
{
  char *ptr_e;
  uint16_t len;

  PRINTF("parse_tag()\n");
  *tag = '\0';
  while(*buf == '\n') {
    buf++;
  }
  if(*buf == '\0') {
    return (char *)buf;
  }
  if(strncmp(TAG_ATTR, buf, strlen(TAG_ATTR)) != 0) {
    return NULL;
  }
  buf += strlen(TAG_ATTR);
  ptr_e = strstr(buf, "\"");
  if(ptr_e == NULL) {
    return NULL;
  }
  len = ptr_e - buf;
  snprintf(tag, max_len, "%.*s", (int)len, buf);

  return ptr_e + 1;
}

/*----------------------------------------------------------------------------*/
#define IPSTR_SIZE 50

static char *
parse_url(const char *url, uip_ipaddr_t *addr, char *path,
          uint16_t path_max_len)
{
  char *ptr_b;
  char *ptr_e;
  char ip[IPSTR_SIZE];
  uint16_t len;
  int retv;

  ptr_b = strstr_p(url, "<coap://[");
  if(!ptr_b) {
    return NULL;
  }
  // getting IP
  ptr_e = strstr(ptr_b, "]");
  if(!ptr_e) {
    return NULL;
  }
  len = ptr_e - ptr_b;
  if(len > IPSTR_SIZE - 1) {
    return NULL;
  }
  memcpy(ip, ptr_b, len);
  ip[len] = '\0';
  PRINTF("IP: %s\n", ip);
  retv = uiplib_ipaddrconv(ip, addr);
  if(retv == 0) {
    return NULL;
  }
  PRINT6ADDR(addr);
  PRINTF("\n");
  // getting path
  ptr_b = ptr_e + 1;
  if(*ptr_b == '>') {
    // no path
    return ptr_b + 1;
  }
  if(*ptr_b != '/') {
    // path does not start with '/'
    return NULL;
  }
  ptr_b++;
  ptr_e = strstr(ptr_b, ">");
  if(!ptr_e) {
    return NULL;
  }
  len = ptr_e - ptr_b;
  if(len > path_max_len - 1) {
    //len = path_max_len - 1;
    return NULL;
  }
  memcpy(path, ptr_b, len);
  path[len] = '\0';
  PRINTF("Path: %s\n", path);
  return ptr_e + 1;
}

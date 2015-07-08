/*
 * \file
 *        Extension to Erbium for enabling CoAP observe clients
 * \author
 *        Daniele Alessandrelli <d.alessandrelli@sssup.it>
 */

#include <stdio.h>
#include <string.h>

#include "er-coap.h"
#include "er-coap-observe-client.h"

#define DEBUG 1
#if DEBUG
#define PRINTF(...) printf(__VA_ARGS__)
#define PRINT6ADDR(addr) PRINTF("[%02x%02x:%02x%02x:%02x%02x:%02x%02x:"        \
                                "%02x%02x:%02x%02x:%02x%02x:%02x%02x]",        \
                                ((uint8_t *)addr)[0], ((uint8_t *)addr)[1],    \
                                ((uint8_t *)addr)[2], ((uint8_t *)addr)[3],    \
                                ((uint8_t *)addr)[4], ((uint8_t *)addr)[5],    \
                                ((uint8_t *)addr)[6], ((uint8_t *)addr)[7],    \
                                ((uint8_t *)addr)[8], ((uint8_t *)addr)[9],    \
                                ((uint8_t *)addr)[10], ((uint8_t *)addr)[11],  \
                                ((uint8_t *)addr)[12], ((uint8_t *)addr)[13],  \
                                ((uint8_t *)addr)[14], ((uint8_t *)addr)[15])
#define PRINTLLADDR(lladdr) PRINTF("[%02x:%02x:%02x:%02x:%02x:%02x]",          \
                                   (lladdr)->addr[0], (lladdr)->addr[1],       \
                                   (lladdr)->addr[2], (lladdr)->addr[3],       \
                                   (lladdr)->addr[4], (lladdr)->addr[5])
#else
#define PRINTF(...)
#define PRINT6ADDR(addr)
#define PRINTLLADDR(addr)
#endif


MEMB(obs_subjects_memb, coap_observee_t, COAP_MAX_OBSERVEES);
LIST(obs_subjects_list);

/*----------------------------------------------------------------------------*/
coap_observee_t *
coap_obs_add_observee(uip_ipaddr_t * addr, uint16_t port,
                     const uint8_t * token, size_t token_len, const char *url,
                     notification_callback_t notification_callback,
                     void *data)
{
  coap_observee_t *o;

  /* Remove existing observe relationship, if any. */
  coap_obs_remove_observee_by_url(addr, port, url);
  o = memb_alloc(&obs_subjects_memb);
  if(o) {
    o->url = url;
    uip_ipaddr_copy(&o->addr, addr);
    o->port = port;
    o->token_len = token_len;
    memcpy(o->token, token, token_len);
    //o->last_mid = 0;
    o->notification_callback = notification_callback;
    o->data = data;
    //stimer_set(&o->refresh_timer, COAP_OBSERVING_REFRESH_INTERVAL);
    PRINTF("Adding obs_subject for /%s [0x%02X%02X]\n", o->url, o->token[0],
           o->token[1]);
    list_add(obs_subjects_list, o);
  }

  return o;
}
/*----------------------------------------------------------------------------*/
void
coap_obs_remove_observee(coap_observee_t * o)
{
  PRINTF("Removing obs_subject for /%s [0x%02X%02X]\n", o->url, o->token[0],
         o->token[1]);
  memb_free(&obs_subjects_memb, o);
  list_remove(obs_subjects_list, o);
}

/*----------------------------------------------------------------------------*/
coap_observee_t *
coap_get_obs_subject_by_token(const uint8_t * token, size_t token_len)
{
  coap_observee_t *obs = NULL;

  for(obs = (coap_observee_t *) list_head(obs_subjects_list); obs;
      obs = obs->next) {
    PRINTF("Looking for token 0x%02X%02X\n", token[0], token[1]);
    if(obs->token_len == token_len
       && memcmp(obs->token, token, token_len) == 0) {
      return obs;
    }
  }

  return NULL;
}

/*----------------------------------------------------------------------------*/
int
coap_obs_remove_observee_by_token(uip_ipaddr_t * addr, uint16_t port,
                                 uint8_t * token, size_t token_len)
{
  int removed = 0;
  coap_observee_t *obs = NULL;

  for(obs = (coap_observee_t *) list_head(obs_subjects_list); obs;
      obs = obs->next) {
    PRINTF("Remove check Token 0x%02X%02X\n", token[0], token[1]);
    if(uip_ipaddr_cmp(&obs->addr, addr)
       && obs->port == port
       && obs->token_len == token_len
       && memcmp(obs->token, token, token_len) == 0) {
      coap_obs_remove_observee(obs);
      removed++;
    }
  }
  return removed;
}

/*----------------------------------------------------------------------------*/
int
coap_obs_remove_observee_by_url(uip_ipaddr_t * addr, uint16_t port,
                               const char *url)
{
  int removed = 0;
  coap_observee_t *obs = NULL;

  for(obs = (coap_observee_t *) list_head(obs_subjects_list); obs;
      obs = obs->next) {
    PRINTF("Remove check URL %s\n", url);
    if(uip_ipaddr_cmp(&obs->addr, addr)
       && obs->port == port
       && (obs->url == url || memcmp(obs->url, url, strlen(obs->url)) == 0)) {
      coap_obs_remove_observee(obs);
      removed++;
    }
  }
  return removed;
}

/*----------------------------------------------------------------------------*/
static void
simple_reply(coap_message_type_t type, uip_ip6addr_t * addr, uint16_t port,
             coap_packet_t * notification)
{
  static coap_packet_t response[1];
  size_t len;

  coap_init_message(response, type, NO_ERROR, notification->mid);
  len = coap_serialize_message(response, uip_appdata);
  coap_send_message(addr, port, uip_appdata, len);
}

/*----------------------------------------------------------------------------*/
static coap_notification_flag_t
classify_notification(void *response, int first)
{
  coap_packet_t *pkt;

  pkt = (coap_packet_t *) response;
  if(!pkt) {
    PRINTF("no response\n");
    return NO_REPLY_FROM_SERVER;
  }
  PRINTF("server replied\n");
  if(!IS_RESPONSE_CODE_2_XX(pkt)) {
    PRINTF("error response code\n");
    return ERROR_RESPONSE_CODE;
  }
  if(!IS_OPTION(pkt, COAP_OPTION_OBSERVE)) {
    PRINTF("server does not support observe\n");
    return OBSERVE_NOT_SUPPORTED;
  }
  if(first) {
    return OBSERVE_OK;
  }
  return NOTIFICATION_OK;
}

/*----------------------------------------------------------------------------*/
void
coap_handle_notification(uip_ipaddr_t * addr, uint16_t port,
                         coap_packet_t * notification)
{
  coap_packet_t *pkt;
  const uint8_t *token;
  int token_len;
  coap_observee_t *obs;
  coap_notification_flag_t flag;
  uint32_t observe;

  PRINTF("coap_handle_notification()\n");
  pkt = (coap_packet_t *) notification;
  token_len = coap_get_token(pkt, &token);
  PRINTF("Getting token\n");
  if(0 == token_len) {
    PRINTF("Error while handling coap observe notification: "
           "no token in message\n");
    return;
  }
  PRINTF("Getting observee info\n");
  obs = coap_get_obs_subject_by_token(token, token_len);
  if(NULL == obs) {
    PRINTF("Error while handling coap observe notification: "
           "no matching token found\n");
    simple_reply(COAP_TYPE_RST, addr, port, notification);
    return;
  }
  if(notification->type == COAP_TYPE_CON) {
    simple_reply(COAP_TYPE_ACK, addr, port, notification);
  }
  if(obs->notification_callback != NULL) {
    flag = classify_notification(notification, 0);
    // TODO: the following mechanism for discarding duplicates is too trivial
    // refer to Observe RFC for a better solution
    if(flag == NOTIFICATION_OK) {
      coap_get_header_observe(notification, &observe);
      if(observe == obs->last_observe) {
        PRINTF("Discarding duplicate\n");
        return;
      }
      obs->last_observe = observe;
    }
    obs->notification_callback(obs, notification, flag);
  }
}

/*----------------------------------------------------------------------------*/
static void
handle_obs_registration_response(void *data, void *response)
{
  coap_observee_t *obs;
  notification_callback_t notification_callback;
  coap_notification_flag_t flag;

  PRINTF("handle_obs_registration_response(): ");
  obs = (coap_observee_t *) data;
  notification_callback = obs->notification_callback;
  flag = classify_notification(response, 1);
  if(notification_callback) {
    notification_callback(obs, response, flag);
  }
  if(flag != OBSERVE_OK) {
    coap_obs_remove_observee(obs);
  }
}

/*----------------------------------------------------------------------------*/
uint8_t
coap_generate_token(uint8_t ** token_ptr)
{
  static uint8_t token = 0;

  token++;
  // FIXME: we should check that this token is not already used
  *token_ptr = (uint8_t *) & token;
  return sizeof(token);
}

/*----------------------------------------------------------------------------*/
coap_observee_t *
coap_obs_request_registration(uip_ipaddr_t * addr, uint16_t port, char *uri,
                              notification_callback_t notification_callback,
                              void *data)
{
  coap_packet_t request[1];
  coap_transaction_t *t;
  uint8_t *token;
  uint8_t token_len;
  coap_observee_t *obs;

  obs = NULL;
  coap_init_message(request, COAP_TYPE_CON, COAP_GET, coap_get_mid());
  coap_set_header_uri_path(request, uri);
  coap_set_header_observe(request, 0);
  token_len = coap_generate_token(&token);
  coap_set_token(request, token, token_len);
  t = coap_new_transaction(request->mid, addr, port);
  if(t) {
    obs = coap_obs_add_observee(addr, port, (uint8_t *) token, token_len, uri,
                               notification_callback, data);
    if(obs) {
      t->callback = handle_obs_registration_response;
      t->callback_data = obs;
      t->packet_len = coap_serialize_message(request, t->packet);
      coap_send_transaction(t);
    } else {
      PRINTF("Could not allocate obs_subject resource buffer");
      coap_clear_transaction(t);
    }
  } else {
    PRINTF("Could not allocate transaction buffer");
  }
  return obs;
}

/*
 * \file
 *        Extension to Erbium for enabling CoAP observe clients
 * \author
 *        Daniele Alessandrelli <d.alessandrelli@sssup.it>
 */

#ifndef COAP_OBSERVING_CLIENT_H_
#define COAP_OBSERVING_CLIENT_H_

#include "er-coap.h"
#include "er-coap-transactions.h"

#ifdef COAP_CONF_MAX_OBSERVEES
#define COAP_MAX_OBSERVEES COAP_CONF_MAX_OBSERVEES
#else
#define COAP_MAX_OBSERVEES      4
#endif /* COAP_CONF_MAX_OBSERVEES */

#if COAP_MAX_OPEN_TRANSACTIONS<COAP_MAX_OBSERVEES
#warning "COAP_MAX_OPEN_TRANSACTIONS smaller than COAP_MAX_OBSERVEES: "        \
         "this may be a problem"
#endif

#define IS_RESPONSE_CODE_2_XX(message) (64 < message->code                     \
                                        &&   message->code < 128)

/*----------------------------------------------------------------------------*/
typedef enum {
  OBSERVE_OK,
  NOTIFICATION_OK,
  OBSERVE_NOT_SUPPORTED,
  ERROR_RESPONSE_CODE,
  NO_REPLY_FROM_SERVER,
} coap_notification_flag_t;

/*----------------------------------------------------------------------------*/
typedef struct coap_observee_s coap_observee_t;

typedef void (*notification_callback_t) (coap_observee_t * subject,
                                         void *notification,
                                         coap_notification_flag_t);

struct coap_observee_s {
  coap_observee_t *next;        /* for LIST */
  uip_ipaddr_t addr;
  uint16_t port;
  const char *url;
  uint8_t token_len;
  uint8_t token[COAP_TOKEN_LEN];
  void *data;                   /* generic pointer for storing user data */
  notification_callback_t notification_callback;
  uint32_t last_observe;
};

/*----------------------------------------------------------------------------*/
coap_observee_t *coap_obs_add_observee(uip_ipaddr_t * addr, uint16_t port,
                                      const uint8_t * token, size_t token_len,
                                      const char *url,
                                      notification_callback_t
                                      notification_callback, void *data);

void coap_obs_remove_observee(coap_observee_t * o);

coap_observee_t *coap_obs_get_observee_by_token(const uint8_t * token,
                                               size_t token_len);

int coap_obs_remove_observee_by_token(uip_ipaddr_t * addr, uint16_t port,
                                     uint8_t * token, size_t token_len);

int coap_obs_remove_observee_by_url(uip_ipaddr_t * addr, uint16_t port,
                                   const char *url);

void coap_handle_notification(uip_ipaddr_t *, uint16_t port,
                              coap_packet_t * notification);

coap_observee_t *coap_obs_request_registration(uip_ipaddr_t * addr,
                                               uint16_t port, char *uri,
                                               notification_callback_t
                                               notification_callback,
                                               void *data);
/* TODO: this function may be moved to er-coap.c */
uint8_t coap_generate_token(uint8_t ** token_ptr);

#endif /* COAP_OBSERVING_CLIENT_H_ */

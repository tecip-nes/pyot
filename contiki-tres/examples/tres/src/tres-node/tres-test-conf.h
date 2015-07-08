#ifndef __TRES_TEST_CONF_H__
#define __TRES_TEST_CONF_H__

/******************************************************************************/
/*                       T-Res example specific conf                          */
/******************************************************************************/

// if enabled, sensors produce random value between 0 and 1999
#define TRES_EXAMPLE_CONF_RANDOM_SENSOR_VALUE 1

// workaround for copper always using blockwise transfer if debug is enabled
#define TRES_CONF_COPPER_WORKAROUND 1

// the period of the fake sensor
#define TRES_EXAMPLE_SENSOR_PERIOD 6

// enable stack overflow detection
#define STACK_OVERFLOW_DETECTION 1

// enable loopback communication
#define UIP_CONF_LOOPBACK 1

// if enabled, T-Res always uses CON messages
#ifndef TRES_CONF_RELIABLE
#define TRES_CONF_RELIABLE 1
#endif
#if TRES_CONF_RELIABLE
#define COAP_OBSERVING_CONF_REFRESH_INTERVAL 0
#else
#define COAP_OBSERVING_CONF_REFRESH_INTERVAL 1000000ul
#endif

/* Increase rpl-border-router IP-buffer when using 128. */
#ifndef REST_MAX_CHUNK_SIZE
#define REST_MAX_CHUNK_SIZE    64
#endif

/* Multiplies with chunk size, be aware of memory constraints. */
#ifndef COAP_MAX_OPEN_TRANSACTIONS
#define COAP_MAX_OPEN_TRANSACTIONS   5
#endif

#define TRES_CONF_OD_MAX_NUMBER 3


/* Must be <= open transaction number. */
#ifndef COAP_MAX_OBSERVERS
#define COAP_MAX_OBSERVERS      COAP_MAX_OPEN_TRANSACTIONS-2
#endif

#ifndef COAP_CONF_MAX_OBSERVEES
#define COAP_CONF_MAX_OBSERVEES      COAP_MAX_OPEN_TRANSACTIONS-2
#endif

/* Reduce 802.15.4 frame queue to save RAM. */
#undef QUEUEBUF_CONF_NUM
#define QUEUEBUF_CONF_NUM               3

#endif /* __TRES_TEST_CONF_H__ */

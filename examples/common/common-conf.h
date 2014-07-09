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

#ifndef __COMMON_CONF_H__
#define __COMMON_CONF_H__

/******************************************************************************/
/*                     T-Res example common configuration                     */
/******************************************************************************/
#ifdef RF_CHANNEL
#undef RF_CHANNEL
#endif /* RF_CHANNEL */
#define RF_CHANNEL              13 

#ifdef CC2420_CONF_CHANNEL
#undef CC2420_CONF_CHANNEL
#endif
#define CC2420_CONF_CHANNEL 13

/* wismote id */
#undef NODE_ID
#define NODE_ID 3

/* Use csma/ca */
#undef NETSTACK_CONF_MAC
#define NETSTACK_CONF_MAC     csma_driver
//#define NETSTACK_CONF_MAC     nullmac_driver

/* No RDC */
#undef NETSTACK_CONF_RDC
#define NETSTACK_CONF_RDC     nullrdc_driver
//#define NETSTACK_CONF_RDC_CHANNEL_CHECK_RATE 8

/* Disable ACK mechanism */
#undef NULLRDC_CONF_802154_AUTOACK
#define NULLRDC_CONF_802154_AUTOACK 0

#undef CC2520_CONF_AUTOACK
#define CC2520_CONF_AUTOACK 0

/* include support 6lowpan fragmentation */
#define SICSLOWPAN_CONF_FRAG	1

/* compress all ipv6 packets */
#undef SICSLOWPAN_CONF_COMPRESSION_THRESHOLD
#define SICSLOWPAN_CONF_COMPRESSION_THRESHOLD 0

#undef UIP_CONF_DS6_NBR_NBU
#define UIP_CONF_DS6_NBR_NBU     12
#undef UIP_CONF_MAX_ROUTES
#define UIP_CONF_MAX_ROUTES   12

#endif /* __COMMON_CONF_H__ */

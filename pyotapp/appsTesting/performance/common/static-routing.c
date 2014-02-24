/*
 * static-routing.c
 *
 *  Created on: Oct 12, 2010
 *      Author: simonduq
 */

#include <stdio.h>
#include "static-routing.h"
#include "static-routing-map.h"

#define DEBUG 1
#if DEBUG
#include <stdio.h>
#define PRINTF(...) printf(__VA_ARGS__)
#define PRINT6ADDR(addr) PRINTF(" %02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x ", ((uint8_t *)addr)[0], ((uint8_t *)addr)[1], ((uint8_t *)addr)[2], ((uint8_t *)addr)[3], ((uint8_t *)addr)[4], ((uint8_t *)addr)[5], ((uint8_t *)addr)[6], ((uint8_t *)addr)[7], ((uint8_t *)addr)[8], ((uint8_t *)addr)[9], ((uint8_t *)addr)[10], ((uint8_t *)addr)[11], ((uint8_t *)addr)[12], ((uint8_t *)addr)[13], ((uint8_t *)addr)[14], ((uint8_t *)addr)[15])
#define PRINTLLADDR(lladdr) PRINTF(" %02x:%02x:%02x:%02x:%02x:%02x ",(lladdr)->addr[0], (lladdr)->addr[1], (lladdr)->addr[2], (lladdr)->addr[3],(lladdr)->addr[4], (lladdr)->addr[5])
#else
#define PRINTF(...)
#define PRINT6ADDR(addr)
#define PRINTLLADDR(addr)
#endif

#include "contiki-net.h"
#include "node-id.h"

int node_rank;

struct id_to_addrs {
    int id;
    uint32_t addr;
};

const struct id_to_addrs motes_addrs[] = {
/*
 * Static routing requires a map nodeid => address.
 * The nodeid can be programmed with the sky-shell.
 * The addresses should also be added to /etc/hosts.
 *
 * aaaa::212:7400:1160:f62d        sky1
 * aaaa::212:7400:0da0:d748        sky2
 * aaaa::212:7400:116e:c325        sky3
 * aaaa::212:7400:116e:c444        sky4
 * aaaa::212:7400:115e:b717        sky5
 *
 * Add the nodeid and last 4 bytes of the address to the map.
 */
    {1, 0x1160f62d},
    {2, 0x0da0d748},
    {3, 0x116ec325},
    {4, 0x116ec444},
    {5, 0x115eb717},
};
/* Define the size of the map. */
#define NODES_IN_MAP    15

uint32_t get_mote_suffix(int rank) {
    if(--rank >=0 && rank<(sizeof(motes_addrs)/sizeof(struct id_to_addrs))) {
      return motes_addrs[rank].addr;
    }
    return 0;
}

int get_mote_id(uint32_t suffix) {
    return suffix & 0xff;
}

void set_global_address(void) {
  uip_ipaddr_t ipaddr;

  printf("Set global address\n");
  uip_ip6addr(&ipaddr, 0xaaaa, 0, 0, 0, 0, 0, 0, 0);
  uip_ds6_set_addr_iid(&ipaddr, &uip_lladdr);
  uip_ds6_addr_add(&ipaddr, 0, ADDR_AUTOCONF);
}

static void add_route_ext(int dest, int next) {
  PRINTF("add route ext %d %d\n", dest, next);
    uip_ipaddr_t ipaddr_dest, ipaddr_next;

    uip_ip6addr(&ipaddr_dest, 0xaaaa, 0, 0, 0, 0, 0, 0, dest);
    uip_ip6addr_u8(&ipaddr_next, 0xfe, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                               0x2, 0x12, 0x74, next, 0x0, next, next, next);

    uip_ds6_route_add(&ipaddr_dest, 128, &ipaddr_next);
}

void add_route(int dest, int next) {
  PRINTF("add route %d %d\n", dest, next);
  uip_ipaddr_t ipaddr_dest, ipaddr_next;

  uip_ip6addr_u8(&ipaddr_dest, 0xaa, 0xaa, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                             0x2, 0x12, 0x74, dest, 0x0, dest, dest, dest);
  uip_ip6addr_u8(&ipaddr_next, 0xfe, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                             0x2, 0x12, 0x74, next, 0x0, next, next, next);

  uip_ds6_route_add(&ipaddr_dest, 128, &ipaddr_next);
}

void add_nbr(int nbr) {
  PRINTF("add nbr %d\n", nbr);
  uip_ipaddr_t ipaddr_nbr;
  uip_lladdr_t lladdr = {{0,0x12,0x74,nbr,0,nbr,nbr,nbr}};

  uip_ip6addr_u8(&ipaddr_nbr, 0xfe, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                             0x2, 0x12, 0x74, nbr, 0x0, nbr, nbr, nbr);

  uip_ds6_nbr_add(&ipaddr_nbr, &lladdr, 0, NBR_REACHABLE);
}

void configure_routing(void) {
  int i;

  node_rank = node_id;

  printf("configure_routing, node_id=%d, node_rank %d\n", node_id, node_rank);

  for (i = 0; i < NODES_IN_MAP; i++) {
    printf("i: %d, val: %d\n", i, nbr_map[node_rank-1][i]);
    if (nbr_map[node_rank-1][i]) {
      add_nbr(i+1);
    }
  }
  
  if (routing_map[node_rank-1][0]) {
    add_route_ext(1, routing_map[node_rank-1][0]);
  }

  for (i = 1; i <= NODES_IN_MAP; i++) {
    if (routing_map[node_rank-1][i]) {
      add_route(i, routing_map[node_rank-1][i]);
    }
  }
}

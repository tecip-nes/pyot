REST interface for RPL state
============================

Provides a set of RESTful resources for the state of RPL in Contiki OS
using the Erbuim engine.

Setup:
------

Add to your Makefile:

    PROJECTDIRS += rplinfo
    PROJECT_SOURCEFILES += rplinfo.c

Then wherever you activate your resources all:

      rplinfo_activate_resources();

Resources:
----------


###/rplinfo/parents

GET returns the number of parents known.

Using the `index` query string returns the specified parent.

    GET /rplinfo/parents?index=1
	
Returns:

    { "eui": "05022a0c9c8cd0af", "pref": true,  "etx":0},

"eui" is the EUI64 mac address of the devices. "pref" marks if this is
the preferred parent. Link metrics follow. Currently, only "etx" is
supported.

"etx" is currently in raw units (read the Contiki code for the
conversion).

###/rplinfo/routes

GET returns the number of routes known.

Using the `index` query string returns the specified parent.

    GET /rplinfo/routes?index=1
	
returns a JSON of the parents such as:

    {"dest":"aaaa::ee47:3c4d:1200:3","next":fe80::ee47:3c4d:1200:3"},

Where dest is the IP address of the destination and next is the IP
address of the next hop.

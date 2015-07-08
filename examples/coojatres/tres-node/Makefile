CONTIKI=../../../contiki-tres/
ifndef TARGET
  TARGET = wismote
endif

PROJECTDIRS += ../../rplinfo
PROJECTDIRS += ../../common
PROJECT_SOURCEFILES += rplinfo.c

WITH_COAP=13

#CONTIKI=/home/andrea/icsi/t-res
APPS = tres pymite
CONTIKI_PROJECT = tres-node
# additional files to be deleted when make clean is invoked
CLEAN = pmstdlib_nat.c pmstdlib_img.c pmfeatures.h symbols.c symbols.h

# for static routing, if enabled
PROJECT_SOURCEFILES += button.c

CFLAGS += -DPROJECT_CONF_H=\"project-conf.h\" 

# variable for root Makefile.include
WITH_UIP6=1
# for some platforms
UIP_CONF_IPV6=1

# new variable since slip-radio
ifneq ($(TARGET), minimal-net)
UIP_CONF_RPL=1
else
ifndef IPV6_ADDR
  IPV6_ADDR = fdfd::9
endif
# minimal-net does not support RPL under Linux and is mostly used to test CoAP only
${info INFO: compiling without RPL}
UIP_CONF_RPL=0
CFLAGS += -DUIP_CONF_ND6_DEF_MAXDADNS=0
CFLAGS += -DHARD_CODED_ADDRESS=\"$(IPV6_ADDR)\"
CFLAGS += -DUIP_CONF_BUFFER_SIZE=1280
#CFLAGS += -D DEBUG=1
endif

# linker optimizations
#SMALL=1

APPS += rest-engine
APPS += er-coap

# optional rules to get assembly
#CUSTOM_RULE_C_TO_OBJECTDIR_O = 1
#CUSTOM_RULE_S_TO_OBJECTDIR_O = 1


# optional rules to get assembly
#$(OBJECTDIR)/%.o: asmdir/%.S
#	$(CC) $(CFLAGS) -MMD -c $< -o $@
#	@$(FINALIZE_DEPENDENCY)
#
#asmdir/%.S: %.c
#	$(CC) $(CFLAGS) -MMD -S $< -o $@

ifeq ($(TARGET), seedeye)
MV_COMMAND = mv $(CONTIKI_PROJECT).$(TARGET) $(CONTIKI_PROJECT).elf
endif

all: pmfeatures.h $(CONTIKI_PROJECT)
	$(MV_COMMAND)
#mv $(CONTIKI_PROJECT).$(TARGET) $(CONTIKI_PROJECT).elf

include $(CONTIKI)/Makefile.include

# border router rules
$(CONTIKI)/tools/tunslip6:	$(CONTIKI)/tools/tunslip6.c
	(cd $(CONTIKI)/tools && $(MAKE) tunslip6)

connect-router:	$(CONTIKI)/tools/tunslip6
	sudo $(CONTIKI)/tools/tunslip6 aaaa::1/64

connect-router-cooja:	$(CONTIKI)/tools/tunslip6
	sudo $(CONTIKI)/tools/tunslip6 -a 127.0.0.1 aaaa::1/64

connect-minimal:
	sudo ip address add fdfd::1/64 dev tap0

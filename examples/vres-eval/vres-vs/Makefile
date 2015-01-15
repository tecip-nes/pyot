ifndef TARGET
  TARGET = wismote
endif

PROJECTDIRS += ../../common
PROJECTDIRS += ../
PROJECT_SOURCEFILES += powerlog.c
PROJECT_SOURCEFILES += pmusrlib_img.c 
WITH_COAP=13

APPS = tres pymite
CONTIKI_PROJECT = tres-vs
# additional files to be deleted when make clean is invoked
CLEAN = pmstdlib_nat.c pmstdlib_img.c pmfeatures.h symbols.c symbols.h

# for static routing, if enabled
PROJECT_SOURCEFILES += button.c

PYMITE_PM_FEATURES = pmfeatures.py
PM_USR_SOURCES += vs.py

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

ifeq ($(TARGET), seedeye)
MV_COMMAND = mv $(CONTIKI_PROJECT).$(TARGET) $(CONTIKI_PROJECT).elf
endif

all: pmusrlib_img.c pmusrlib_nat.c pmfeatures.h $(CONTIKI_PROJECT)
	$(MV_COMMAND)
#mv $(CONTIKI_PROJECT).$(TARGET) $(CONTIKI_PROJECT).elf
CONTIKI = /home/andrea/mygithub/contiki-tres
include $(CONTIKI)/Makefile.include

pmusrlib_nat.c pmusrlib_img.c: usrlib

# target for generating pymite_nat.c pymite_img.c
#usrlib: $(PM_USR_SOURCES) $(PYMITE_IMG_CREATOR) pmfeatures.py
usrlib: $(PM_USR_SOURCES) $(PYMITE_IMG_CREATOR)
	$(PYMITE_IMG_CREATOR) -f pmfeatures.py -c -u -o pmusrlib_img.c          \
			--native-file=pmusrlib_nat.c $(PM_USR_SOURCES)


# border router rules
$(CONTIKI)/tools/tunslip6:	$(CONTIKI)/tools/tunslip6.c
	(cd $(CONTIKI)/tools && $(MAKE) tunslip6)

connect-router:	$(CONTIKI)/tools/tunslip6
	sudo $(CONTIKI)/tools/tunslip6 aaaa::1/64

connect-router-cooja:	$(CONTIKI)/tools/tunslip6
	sudo $(CONTIKI)/tools/tunslip6 -a 127.0.0.1 aaaa::1/64

connect-minimal:
	sudo ip address add fdfd::1/64 dev tap0


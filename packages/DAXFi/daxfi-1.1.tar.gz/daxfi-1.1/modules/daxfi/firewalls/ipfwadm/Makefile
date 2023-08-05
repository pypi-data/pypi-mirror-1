
include ../config.mk

# NOTE: you can download the latest ipfwadm's source at
#       http://www.xos.nl/resources/ipfwadm/

_ipfwadm$(MODNAME).so: _ipfwadm.c
	$(CC) $(CFLAGS) -c _ipfwadm.c -I$(PYHPATH) \
	-DMODNAME="init_ipfwadm$(MODNAME)" \
	-DMODNAMESTR=\"_ipfwadm$(MODNAME)\" \
	-o _ipfwadm.o
	$(CC) -shared _ipfwadm.o -o _ipfwadm$(MODNAME).so
	$(RM) -f _ipfwadm.o
	$(STRIP) _ipfwadm$(MODNAME).so

ipfwadm: _ipfwadm$(MODNAME).so


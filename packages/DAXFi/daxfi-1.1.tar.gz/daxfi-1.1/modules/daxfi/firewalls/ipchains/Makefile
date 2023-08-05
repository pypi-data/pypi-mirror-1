
include ../config.mk

# NOTE: modify this option according to your system; ipchains' source
#       can be found at http://people.netfilter.org/~rusty/ipchains/
IPCHPATH	= /usr/src/ipchains-1.3.10/


_ipchains$(MODNAME).so: _ipchains.c
	$(CC) $(CFLAGS) -c _ipchains.c -I$(PYHPATH) -I$(IPCHPATH) \
		-DMODNAME="init_ipchains$(MODNAME)" \
		-DMODNAMESTR=\"_ipchains$(MODNAME)\" \
		-o _ipchains.o
	$(CC) -shared _ipchains.o -o _ipchains$(MODNAME).so
	$(RM) -f _ipchains.o
	$(STRIP) _ipchains$(MODNAME).so

ipchains: _ipchains$(MODNAME).so



include ../config.mk

# NOTE: modify these options according to your system; the latest netfilter's
#       source can be found at http://www.netfilter.org/projects/iptables/
NETFILTER_VERSION	= 1.3.7
IPTHPATH1	= /usr/src/iptables-$(NETFILTER_VERSION)
IPTHPATH2	= /usr/src/iptables-$(NETFILTER_VERSION)/include/


_iptables$(MODNAME).so: _iptables.c
	$(CC) $(CFLAGS) -c _iptables.c \
		-I$(PYHPATH) -I$(IPTHPATH1) -I$(IPTHPATH2) \
		-DMODNAME="init_iptables$(MODNAME)" \
		-DMODNAMESTR=\"_iptables$(MODNAME)\" \
		-DNETFILTER_VERSION=\"$(NETFILTER_VERSION)\" -o _iptables.o
	$(CC) -shared _iptables.o -o _iptables$(MODNAME).so
	$(RM) -f _iptables.o
	$(STRIP) _iptables$(MODNAME).so

iptables: _iptables$(MODNAME).so


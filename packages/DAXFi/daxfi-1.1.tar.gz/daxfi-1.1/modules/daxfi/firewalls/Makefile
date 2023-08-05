#
# A brutal makefile for the C modules of DAXFi.
# Copyright 2001, 2002 Davide Alberani <alberanid@libero.it>
#
#

FIREWALLS = iptables ipfilter ipchains ipfwadm


default:
	@echo "    I's much better if you enter the subdirectory of"
	@echo "    your running firewall and then you run 'make' there."
	@echo ""
	@echo "    Otherwise, if you want to rebuild every modules,"
	@echo "    run here: make all"
	@echo ""


all:
	for firewall in $(FIREWALLS) ; do \
		(cd $$firewall; ${MAKE} $$firewall); \
	done



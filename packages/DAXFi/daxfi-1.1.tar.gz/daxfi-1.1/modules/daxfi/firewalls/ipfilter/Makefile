include ../config.mk

# I don't know how to set a variable with the output of a shell
# command using BSD make.  So that I define here MODNAME.
MODNAME	= `../getarch.py`

# NOTE: you can download the latest ipfilter's source at
#       http://coombs.anu.edu.au/~avalon/

ipfilter: _ipfilter.c
	$(CC) $(CFLAGS) -c _ipfilter.c -I $(PYHPATH) \
	-DMODNAME="init_ipfilter$(MODNAME)" \
	-DMODNAMESTR=\"_ipfilter$(MODNAME)\" \
	-o _ipfilter.o
	$(CC) -shared -lkvm _ipfilter.o -o _ipfilter$(MODNAME).so
	$(RM) -f _ipfilter.o
	$(STRIP) _ipfilter$(MODNAME).so



CC	= gcc
COPTS	= -O2
CFLAGS	= -Wall $(COPTS)

STRIP	= /usr/bin/strip
RM	= /bin/rm

# NOTE: if you're using Python != 2.4, you need to change this!
#       Moreover, maybe that your includes file are under /usr/local/include;
#       modify PYHPATH according to your system.
PYHPATH	= /usr/include/python2.4/

MODNAME	= $(shell ../getarch.py)


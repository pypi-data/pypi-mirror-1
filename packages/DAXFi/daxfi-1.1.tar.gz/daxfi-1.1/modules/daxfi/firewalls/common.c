/*
 * Common functions for DAXFi C modules.
 * Copyright 2001, 2002 Davide Alberani <alberanid@libero.it>
 *
 * This code is released under GPL license.
 *
 */


#include <netinet/in.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>


/* The begin of a XML string. */
#define XML_HEADER	"<?xml version=\"1.0\"?>\n\n" \
			"<append>\n  <rule "

/* Convert a string to upper or lower. */
static char *
conv_case(char *s, char *d, int upper)
{
	int i = 0;
	for (i = 0; i < strlen(s); i++) {
		if (upper)
			d[i] = toupper(s[i]);
		else
			d[i] = tolower(s[i]);
	}
	d[i] = '\0';

	return d;
}


/* Append to dest the string attributeName="attributeValue". */
static void
addval(char *dest, char *name, char *value)
{
	strcat(dest, name);
	strcat(dest, "=\"");
	strcat(dest, value);
	strcat(dest, "\" ");
}


/* Translate an in_addr address to the dotted notation. */
static char *
addr_to_dotted(const struct in_addr *addrp)
{
	static char buf[16];
	const unsigned char *bytep;

	bytep = (const unsigned char *) &(addrp->s_addr);
	sprintf(buf, "%d.%d.%d.%d", bytep[0], bytep[1], bytep[2], bytep[3]);
	return buf;
}



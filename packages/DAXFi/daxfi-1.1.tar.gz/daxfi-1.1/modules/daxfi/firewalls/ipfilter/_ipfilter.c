/*
 * Ipfilter functions for DAXFi.
 * Copyright 2002 Davide Alberani <alberanid@libero.it>
 *
 * Many portions of this code are 'stolen' from works copyrighted
 * by other people, mainly Darren Reed.
 * Obviously if this code sucks (and it *really* sucks) it's only
 * my fault. :-)
 *
 * This code is released under GPL license.
 *
 */


#include <unistd.h>
#include <Python.h>

#include "../common.c"

#include <fcntl.h>
#include <kvm.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <syslog.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <netinet/in.h>
#ifdef __OpenBSD__
#	include <netinet/ip_fil_compat.h>
#else
#	include <netinet/ip_compat.h>
#endif
#include <netinet/ip_fil.h>
#include <netinet/ip_nat.h>


#ifndef TH_SYN
#	define TH_SYN 0x02
#endif
#ifndef TH_RST
#	define TH_RST 0x04
#endif
#ifndef TH_ACK
#	define TH_ACK 0x10
#endif
#ifndef TH_FIN
#	define TH_FIN 0x01
#endif
#ifndef TH_PUSH
#	define TH_PUSH 0x08
#endif
#ifndef TH_URG
#	define TH_URG 0x20
#endif
#ifndef TH_ECN
#	define TH_ECN 0x40
#endif
#ifndef TH_CWR
#	define TH_CWR 0x80
#endif
#ifndef IPN_FRAG
#	define IPN_FRAG 0x200000
#endif



static int
kmemcpy(register char *buf, long pos, register int n)
{
        register int r;
	kvm_t *kvm_f = NULL;
        if (!n)
                return 0;
        if (kvm_f == NULL) {
		kvm_f = kvm_open(NULL, NULL, NULL, O_RDONLY, NULL);
		if (kvm_f == NULL)
			return -1;
	}
	while ((r = kvm_read(kvm_f, pos, buf, n)) < n)
		if (r <= 0)
                        return -1;
                else {
			buf += r;
			pos += r;
			n -= r;
		}
	return 0;
}


/* String version of the log priority. */
struct log_names {
	const char *name;
	unsigned int value;
};

static struct log_names prio_names[] = {
	{"alert", LOG_ALERT},
	{"crit", LOG_CRIT},
	/* {"debug", LOG_DEBUG}, */
	{"emerg", LOG_EMERG},
	{"err", LOG_ERR},
	{"info", LOG_INFO},
	{"notice", LOG_NOTICE},
	{"panic", LOG_EMERG},
	{"warning", LOG_WARNING},
	{NULL, -1}
};

static struct log_names fac_names[] = {
	{"auth", LOG_AUTH},
	{"authpriv", LOG_AUTHPRIV},
	{"cron", LOG_CRON},
	{"daemon", LOG_DAEMON},
	{"ftp", LOG_FTP},
	{"kern", LOG_KERN},
	{"lpr", LOG_LPR},
	{"mail", LOG_MAIL},
	{"news", LOG_NEWS},
	{"syslog", LOG_SYSLOG},
	{"user", LOG_USER},
	{"uucp", LOG_UUCP},
	{"local0", LOG_LOCAL0},
	{"local1", LOG_LOCAL1},
	{"local2", LOG_LOCAL2},
	{"local3", LOG_LOCAL3},
	{"local4", LOG_LOCAL4},
	{"local5", LOG_LOCAL5},
	{"local6", LOG_LOCAL6},
	{"local7", LOG_LOCAL7},
	{NULL, -1}
};


/* Return 1 if the kernel support ipfilter. */
static PyObject*
daxfiIsSupported(PyObject *self, PyObject *args)
{
	char *device = IPL_NAME;
	friostat_t fio;
	friostat_t *fiop = &fio;
	int fd;

	if (PyTuple_Size(args) != 0) {
		PyErr_SetString(PyExc_AttributeError,
				"is_supported() requires no arguments");
		return NULL;
	}

	if ((fd = open(device, O_RDONLY)) == -1) {
		return Py_BuildValue("i", 0);
	}
	if ((ioctl(fd, SIOCGETFS, &fiop)) == -1) {
		return Py_BuildValue("i", 0);
	}

	return Py_BuildValue("i", 1);
}

char *icmpcodes[] = {
	"3/0", "3/1", "3/2", "3/3", "3/4", "3/5", "3/6", "3/7", "3/8",
	"3/9", "3/10", "3/11", "3/12", "3/13", "3/14", "3/15"
};


/* Return a list of chain names. */
static PyObject*
daxfiListChains(PyObject *self, PyObject *args)
{
	PyObject *result = PyList_New(0);
	PyList_Append(result, PyString_FromString("in"));
	PyList_Append(result, PyString_FromString("out"));
	return Py_BuildValue("O", result);
}


/* Return a list of XML strings for NAT rules. */
static PyObject*
daxfiListNat(PyObject *self, PyObject *args)
{
	PyObject *result = PyList_New(0);
	natstat_t ns;
	natstat_t *nsp = &ns;
	ipnat_t ipn;
	int fd;

	/* Requires no options */
	if (!PyArg_ParseTuple(args, ""))
		return NULL;

	bzero((char *)&ns, sizeof(ns));

	if ((fd = open(IPL_NAT, O_RDONLY)) == -1) {
		PyErr_SetString(PyExc_OSError,
					"unable to open the device");
		return NULL;
	}

	if (ioctl(fd, SIOCGNATS, &nsp) == -1) {
		PyErr_SetString(PyExc_OSError,
					"error reading from the device");
		return NULL;
	}

	while (nsp->ns_list) {
		char xml[10240];
		char strnfix[1024];
		char strnfix2[1024];
		xml[0] = '\0';
		strnfix[1023] = '\0';
		strnfix2[1023] = '\0';
		strnfix[0] = '\0';
		strnfix2[0] = '\0';

		if (kmemcpy((char *)&ipn, (long)nsp->ns_list,
				sizeof(ipn)) == -1) {
			PyErr_SetString(PyExc_OSError,
						"unable to copy the buffer");
			return NULL;
		}

		strcat(xml, XML_HEADER);

		addval(xml, "interface", ipn.in_ifname);

		if (ipn.in_flags & IPN_FILTER) {
			struct in_addr a;
			if (ipn.in_flags & IPN_NOTSRC)
				sprintf(strnfix, "! ");
			if (ipn.in_redir == NAT_REDIRECT) {
				a.s_addr = ipn.in_srcip;
				strcat(strnfix, inet_ntoa(a));
				strcat(strnfix, "/");
				a.s_addr = ipn.in_srcmsk;
				strcat(strnfix, inet_ntoa(a));
			} else {
				a.s_addr = ipn.in_inip;
				strcat(strnfix, inet_ntoa(a));
				strcat(strnfix, "/");
				a.s_addr = ipn.in_inmsk;
				strcat(strnfix, inet_ntoa(a));
			}
			if (strcmp(strnfix, "0.0.0.0/0.0.0.0")) 
				addval(xml, "source-ip", strnfix);

			strnfix[0] = '\0';
			if (ipn.in_flags & IPN_NOTDST)
				sprintf(strnfix, "! ");
			if (ipn.in_redir == NAT_REDIRECT) {
				a.s_addr = ipn.in_outip;
				strcat(strnfix, inet_ntoa(a));
				strcat(strnfix, "/");
				a.s_addr = ipn.in_outmsk;
				strcat(strnfix, inet_ntoa(a));
			} else {
				a.s_addr = ipn.in_srcip;
				strcat(strnfix, inet_ntoa(a));
				strcat(strnfix, "/");
				a.s_addr = ipn.in_srcmsk;
				strcat(strnfix, inet_ntoa(a));
			}
			if (strcmp(strnfix, "0.0.0.0/0.0.0.0"))
				addval(xml, "destination-ip", strnfix);
		} else {
			char tmp[16];
			char tmp2[16];
			if (ipn.in_redir != NAT_REDIRECT) {
				sprintf(tmp, "%s", inet_ntoa(ipn.in_in[0]));
				sprintf(tmp2, "%s", inet_ntoa(ipn.in_in[1]));
			} else {
				sprintf(tmp, "%s", inet_ntoa(ipn.in_out[0]));
				sprintf(tmp2, "%s", inet_ntoa(ipn.in_out[1]));
			}
			sprintf(strnfix, "%s/%s", tmp, tmp2);
			if (strcmp(strnfix, "0.0.0.0/0.0.0.0")) {
				if (ipn.in_redir != NAT_REDIRECT)
					addval(xml, "source-ip", strnfix);
				else
					addval(xml, "destination-ip", strnfix);
			}
		}

		if (ipn.in_flags & IPN_FRAG)
			addval(xml, "fragment-only", strnfix);

		strcat(xml, "/>\n");

		if ((ipn.in_scmp || ipn.in_dcmp ||
				ipn.in_pmin || ipn.in_pmax) &&
				ipn.in_redir != NAT_REDIRECT) {
			strcat(xml, "  <protocol ");
			strnfix[0] = '\0';
			if (ipn.in_scmp == FR_EQUAL) {
				sprintf(strnfix, "%u", ipn.in_sport);
			} else if (ipn.in_scmp == FR_NEQUAL) {
				sprintf(strnfix, "! %u", ipn.in_sport);
			} else if (ipn.in_scmp == FR_LESST) {
				sprintf(strnfix, "1:%u", ipn.in_sport - 1);
			} else if (ipn.in_scmp == FR_LESSTE) {
				sprintf(strnfix, "1:%u", ipn.in_sport);
			} else if (ipn.in_scmp == FR_GREATERT) {
				sprintf(strnfix, "%u:65535", ipn.in_sport + 1);
			} else if (ipn.in_scmp == FR_GREATERTE) {
				sprintf(strnfix, "%u:65535", ipn.in_sport);
			} else if (ipn.in_scmp == FR_OUTRANGE) {
				sprintf(strnfix, "! %u:%u", ipn.in_sport,
							ipn.in_stop);
			} else if (ipn.in_scmp == FR_INRANGE) {
				sprintf(strnfix, "%u:%u", ipn.in_sport,
							ipn.in_stop);
			}
			if (strcmp(strnfix, "0:65535") &&
					strcmp(strnfix, "1:65535") &&
					strcmp(strnfix, "0"))
				addval(xml, "source-port", strnfix);

			strnfix[0] = '\0';
			if (ipn.in_dcmp == FR_EQUAL) {
				sprintf(strnfix, "%u", ipn.in_dport);
			} else if (ipn.in_dcmp == FR_NEQUAL) {
				sprintf(strnfix, "! %u", ipn.in_dport);
			} else if (ipn.in_dcmp == FR_LESST) {
				sprintf(strnfix, "1:%u", ipn.in_dport - 1);
			} else if (ipn.in_dcmp == FR_LESSTE) {
				sprintf(strnfix, "1:%u", ipn.in_dport);
			} else if (ipn.in_dcmp == FR_GREATERT) {
				sprintf(strnfix, "%u:65535", ipn.in_dport + 1);
			} else if (ipn.in_dcmp == FR_GREATERTE) {
				sprintf(strnfix, "%u:65535", ipn.in_dport);
			} else if (ipn.in_dcmp == FR_OUTRANGE) {
				sprintf(strnfix, "! %u:%u", ipn.in_dport,
							ipn.in_dtop);
			} else if (ipn.in_dcmp == FR_OUTRANGE) {
				sprintf(strnfix, "! %u:%u", ipn.in_dport,
							ipn.in_dtop);
			} else if (ipn.in_dcmp == FR_INRANGE) {
				sprintf(strnfix, "%u:%u", ipn.in_dport,
							ipn.in_dtop);
			}
			if (strcmp(strnfix, "0:65535") &&
					strcmp(strnfix, "1:65535") &&
					strcmp(strnfix, "0"))
				addval(strnfix2, "destination-port", strnfix);

			if (ipn.in_pmin || ipn.in_pmax) {
				if (ipn.in_flags & IPN_TCP)
					addval(xml, "protocol", "6");
				else if (ipn.in_flags & IPN_UDP)
					addval(xml, "protocol", "17");
			}

			strcat(xml, "/>\n");
		} else if (ipn.in_redir == NAT_REDIRECT) {
			if (ipn.in_flags & IPN_TCP)
				addval(strnfix2, "protocol", "6");
			if (ipn.in_flags & IPN_UDP)
				addval(strnfix2, "protocol", "17");
			if (ipn.in_pmin) {
				sprintf(strnfix, "%d", ntohs(ipn.in_pmin));
				addval(strnfix2, "destination-port", strnfix);
			}
			if (strlen(strnfix2) > 0) {
				strcat(xml, "  <protocol ");
				strcat(xml, strnfix2);
				strcat(xml, " />\n");
			}
		}

		strcat(xml, "  <nat ");

		switch (ipn.in_redir) {

			case NAT_REDIRECT:
				sprintf(strnfix, "%s", inet_ntoa(ipn.in_in[0]));
				if (strcmp(strnfix, "0.0.0.0/0.0.0.0") &&
				strcmp(strnfix,"127.0.0.1/255.255.255.255"))
					addval(xml, "to-address", strnfix);
				if (strcmp(strnfix,"127.0.0.1/255.255.255.255"))
					addval(xml, "nat", "redirect");
				else
					addval(xml, "nat", "dnat");
				if (ipn.in_pnext) {
					sprintf(strnfix, "%d",
							ntohs(ipn.in_pnext));
					addval(xml, "to-port", strnfix);
				}
				break;

			case NAT_MAP:
				sprintf(strnfix, "%s",
						inet_ntoa(ipn.in_out[0]));
				if (ipn.in_flags & IPN_IPRANGE)
					strcat(strnfix, ":");
				else
					strcat(strnfix, "/");
				sprintf(strnfix2, "%s",
					inet_ntoa(ipn.in_out[1]));
				strcat(strnfix, strnfix2);

				if (!strcmp(strnfix, "0.0.0.0/255.255.255.255"))
					addval(xml, "nat", "masq");
				else
					addval(xml, "nat", "snat");

				sprintf(strnfix, "%s",
						inet_ntoa(ipn.in_out[0]));
				if (ipn.in_flags & IPN_IPRANGE)
					strcat(strnfix, ":");
				else
					strcat(strnfix, "/");
				sprintf(strnfix2, "%s",
						inet_ntoa(ipn.in_out[1]));
				strcat(strnfix, strnfix2);
				if (strcmp(strnfix, "0.0.0.0/0.0.0.0") &&
						strcmp(strnfix,
						"0.0.0.0/255.255.255.255"))
				addval(xml, "to-address", strnfix);
				if (ipn.in_pmin || ipn.in_pmax) {
					sprintf(strnfix, "%d",
						ntohs(ipn.in_pmin));
					if (ipn.in_pmax != ipn.in_pmin) {
						sprintf(strnfix2, ":%d",
							ntohs(ipn.in_pmax));
						strcat(strnfix, strnfix2);
					}
					addval(xml, "to-port", strnfix);
				}
				break;

			default:
				nsp->ns_list = ipn.in_next;
				continue;
				break;
		}

		strcat(xml, "/>\n");
		strcat(xml, "</rule></append>");

		PyList_Append(result, PyString_FromString(xml));

		nsp->ns_list = ipn.in_next;
	}
	return result;
}


/* Return a string representing the policy for the given chain. */
static PyObject*
daxfiGetPolicy(PyObject *self, PyObject *args)
{
	if (PyTuple_Size(args) != 1) {
		PyErr_SetString(PyExc_AttributeError,
				"get_policy() requires a single argument");
		return NULL;
	}

	return PyString_FromString("");
}


/* Return a list of XML strings that represents the rule.
   Requires a chain name as parameter. */
static PyObject*
daxfiListRules(PyObject *self, PyObject *args)
{
	PyObject *chain;
	char chain_name[42];
	int input_chain = 1;
	PyObject *result = PyList_New(0);

	friostat_t fio;
	frentry_t *fp;
	friostat_t *fiop = &fio;
	struct frentry fb;

	int n = 1;
	char *device = IPL_NAME;
	int fd;
	int set = 0;

	if (!PyArg_ParseTuple(args, "O!", &PyString_Type, &chain))
		return NULL;

	snprintf(chain_name, 41, PyString_AsString(chain));

	if (!strcmp(chain_name, "in")) {
		input_chain = 1;
	} else if (!strcmp(chain_name, "out")) {
		input_chain = 0;
	} else {
		PyErr_SetString(PyExc_OSError,
			"direction name must be one of 'in' or 'out'");
		return NULL;
	}

	bzero((char *)&fio, sizeof(fio));

	if ((fd = open(device, O_RDONLY)) == -1) {
		PyErr_SetString(PyExc_OSError,
				"unable to open the device");
		return NULL;
	}
	
	if ((ioctl(fd, SIOCGETFS, &fiop)) == -1) {
		PyErr_SetString(PyExc_OSError,
				"error reading from the device");
		return NULL;
	}
	set = fiop->f_active;

#ifdef USE_INET6
	if (input_chain)
		fp = (struct frentry *)fiop->f_fin6[set];
	else
		fp = (struct frentry *)fiop->f_fout6[set];
#else
	if (input_chain)
		fp = (struct frentry *)fiop->f_fin[set];
	else
		fp = (struct frentry *)fiop->f_fout[set];
#endif

	for (n = 1; fp; n++) {
		char xml[10240];
		char strnfix[1024];
		char strnfix2[1024];

		xml[0] = '\0';
		strnfix[1023] = '\0';
		strnfix2[1023] = '\0';
		strnfix[0] = '\0';
		strnfix2[0] = '\0';

		if (kmemcpy((char *)&fb, (long)fp, sizeof(fb)) == -1) {
			PyErr_SetString(PyExc_OSError,
					"unable to copy the buffer");
			return NULL;
		}
		fp = &fb;

		strcat(xml, XML_HEADER);
		/* chain name */
		addval(xml, "direction", chain_name);

		/* source IP */
		strcat(strnfix, fp->fr_flags & FR_NOTSRCIP ? "! " : "");
		strcat(strnfix, inet_ntoa(fp->fr_ip.fi_src.in4));
		strcat(strnfix, "/");
		strcat(strnfix, inet_ntoa(fp->fr_smsk));
		if (strcmp(strnfix, "0.0.0.0/0.0.0.0"))
			addval(xml, "source-ip", strnfix);

		/* destination IP */
		strnfix[0] = '\0';
		strcat(strnfix, fp->fr_flags & FR_NOTDSTIP ? "! " : "");
		strcat(strnfix, inet_ntoa(fp->fr_ip.fi_dst.in4));
		strcat(strnfix, "/");
		strcat(strnfix, inet_ntoa(fp->fr_dmsk));
		if (strcmp(strnfix, "0.0.0.0/0.0.0.0"))
			addval(xml, "destination-ip", strnfix);

		/* interface */
		if (fp->fr_ifname[0]) {
			addval(xml, "interface", fp->fr_ifname);
		}

		/* fragment */
		strnfix[0] = '\0';
		if (fp->fr_mip.fi_fl & FI_FRAG) {
			if (!(fp->fr_ip.fi_fl & FI_FRAG))
				addval(xml, "fragment-only", "no");
			addval(xml, "fragment-only", "yes");
                }
		strcat(xml, ">\n");

		/* protocol */
		strnfix[0] = '\0';
		strnfix2[0] = '\0';
		if (fp->fr_proto == IPPROTO_TCP &&
				(fp->fr_tcpf || fp->fr_tcpfm)) {
			if ((fp->fr_tcpf & TH_SYN) &&
					(fp->fr_tcpfm & TH_SYN) &&
					(fp->fr_tcpfm & TH_RST) &&
					(fp->fr_tcpfm & TH_ACK)) {
				addval(strnfix2, "syn-only", "yes");
			} else if ((fp->fr_tcpf & TH_SYN) &&
					(fp->fr_tcpf & TH_ACK)) {
				addval(strnfix2, "syn-only", "no");
			}
		}

		sprintf(strnfix, "%d", fp->fr_proto);
		if (strcmp(strnfix, "0")) {
			addval(strnfix2, "protocol", strnfix);
		}

		strnfix[0] = '\0';
		if (fp->fr_proto == IPPROTO_TCP &&
				(fp->fr_tcpf || fp->fr_tcpfm)) {
			int j = 0;
			u_char  flags[] = { TH_ACK, TH_CWR, TH_ECN, TH_FIN, \
					TH_PUSH, TH_RST, TH_SYN, TH_URG };
			char *flagset[] = {"ack", "cwr", "ecn", "fin", "push", \
						"rst", "syn", "urg"};
			for (j = 0; j < 8; j++) {
				if (fp->fr_tcpf & flags[j]) {
					if (strlen(strnfix) > 0)
						strcat(strnfix, ",");
					strcat(strnfix, flagset[j]);
				}
			}
			if (fp->fr_tcpfm) {
				strcat(strnfix, "/");
				for (j = 0; j < 8; j++) {
					if (fp->fr_tcpfm & flags[j]) {
						if (j != 0)
							strcat(strnfix, ",");
						strcat(strnfix, flagset[j]);
					}
				}
			}
			addval(strnfix2, "tcp-flags", strnfix);
		}

		strnfix[0] = '\0';
		if (fp->fr_scmp != FR_NONE) {
			if (fp->fr_scmp == FR_EQUAL) {
				sprintf(strnfix, "%u", fp->fr_sport);
			} else if (fp->fr_scmp == FR_NEQUAL) {
				sprintf(strnfix, "! %u", fp->fr_sport);
			} else if (fp->fr_scmp == FR_LESST) {
				sprintf(strnfix, "1:%u", fp->fr_sport - 1);
			} else if (fp->fr_scmp == FR_LESSTE) {
				sprintf(strnfix, "1:%u", fp->fr_sport);
			} else if (fp->fr_scmp == FR_GREATERT) {
				sprintf(strnfix, "%u:65535", fp->fr_sport + 1);
			} else if (fp->fr_scmp == FR_GREATERTE) {
				sprintf(strnfix, "%u:65535", fp->fr_sport);
			} else if (fp->fr_scmp == FR_OUTRANGE) {
				sprintf(strnfix, "! %u:%u", fp->fr_sport,
								fp->fr_stop);
			} else if (fp->fr_scmp == FR_INRANGE) {
				sprintf(strnfix, "%u:%u", fp->fr_sport,
								fp->fr_stop);
			}
			if (strlen(strnfix) > 0 &&
					strcmp(strnfix, "0:65535") &&
					strcmp(strnfix, "1:65535") &&
					strcmp(strnfix, "0"))
				addval(strnfix2, "source-port", strnfix);
		}

		strnfix[0] = '\0';
		if (fp->fr_dcmp != FR_NONE) {
			if (fp->fr_dcmp == FR_EQUAL) {
				sprintf(strnfix, "%u", fp->fr_dport);
			} else if (fp->fr_dcmp == FR_NEQUAL) {
				sprintf(strnfix, "! %u", fp->fr_dport);
			} else if (fp->fr_dcmp == FR_LESST) {
				sprintf(strnfix, "1:%u", fp->fr_dport - 1);
			} else if (fp->fr_dcmp == FR_LESSTE) {
				sprintf(strnfix, "1:%u", fp->fr_dport);
			} else if (fp->fr_dcmp == FR_GREATERT) {
				sprintf(strnfix, "%u:65535", fp->fr_dport + 1);
			} else if (fp->fr_dcmp == FR_GREATERTE) {
				sprintf(strnfix, "%u:65535", fp->fr_dport);
			} else if (fp->fr_dcmp == FR_OUTRANGE) {
				sprintf(strnfix, "! %u:%u", fp->fr_dport,
								fp->fr_dtop);
			} else if (fp->fr_dcmp == FR_INRANGE) {
				sprintf(strnfix, "%u:%u", fp->fr_dport,
								fp->fr_dtop);
			}
			if (strlen(strnfix) > 0 &&
					strcmp(strnfix, "0:65535") &&
					strcmp(strnfix, "1:65535") &&
					strcmp(strnfix, "0"))
				addval(strnfix2, "destination-port", strnfix);
		}

		/* icmp */
		strnfix[0] = '\0';
		if (fp->fr_proto == IPPROTO_ICMP) {
			char tmp[32];
			int type = fp->fr_icmp, code;
			tmp[0] = '\0';
			type = ntohs(fp->fr_icmp);
			code = type & 0xff;
			type /= 256;

			if (ntohs(fp->fr_icmpm) & 0xFF)
				sprintf(tmp, "%d/%d", type, code);
			else
				sprintf(tmp, "%d", type);
			if (strcmp(tmp, "0"))
				addval(strnfix2, "icmp-type", tmp);
		}

		if (strlen(strnfix2) > 0) {
			strcat(xml, "  <protocol ");
			if (fp->fr_flags & FR_KEEPSTATE) {
				addval(xml, "state", "related");
			}
			strcat(xml, strnfix2);
			strcat(xml, " />\n");
		}

		if (fp->fr_flags & FR_BLOCK) {
			if ((fp->fr_flags & FR_RETICMP) ||
					(fp->fr_flags & FR_RETRST) ||
					(fp->fr_flags & FR_FAKEICMP)) {
				strcat(xml, "  <target target=\"reject\" ");
				if (fp->fr_flags & FR_RETRST)
					addval(xml, "reject-with","tcp-reset");
				if ((fp->fr_flags & FR_RETICMP) &&
						fp->fr_icode && \
						(fp->fr_icode < 16)) {
					addval(xml, \
						"reject-with", \
						icmpcodes[(int)fp->fr_icode]);
					}
				strcat(xml, "/>\n");
			} else 
				strcat(xml, "  <target target=\"drop\" />\n");
		}

		if (fp->fr_flags & FR_PASS)
			strcat(xml, "  <target target=\"accept\" />\n");

		if (fp->fr_flags & FR_LOG) {
			strcat(xml, "  <log ");
			if (fp->fr_loglevel & LOG_FACMASK) {
				int i;
				unsigned int f, p;
				f = LOG_FAC(fp->fr_loglevel);
				p = LOG_PRI(fp->fr_loglevel);
				for (i = 0; prio_names[i].name; i++) {
					if (prio_names[i].value == p) {
						addval(xml, "priority", \
						(char *)prio_names[i].name);
						break;
					}
				}
				for (i = 0; fac_names[i].name; i++) {
					if (fac_names[i].value == f) {
						addval(xml, "facility", \
						(char *)fac_names[i].name);
						break;
					}
				}
			}
			strcat(xml, "/>\n");
		}

		strcat(xml, "</append>");

		PyList_Append(result, PyString_FromString(xml));

                fp = fp->fr_next;
        }

	return Py_BuildValue("O", result);
}


/* Exported functions. */
static PyMethodDef _IpfilterMethods[] = {
	{"list_rules",		daxfiListRules,		METH_VARARGS},
	{"list_chains",		daxfiListChains,	METH_VARARGS},
	{"is_supported",	daxfiIsSupported,	METH_VARARGS},
	{"list_nat",		daxfiListNat,		METH_VARARGS},
	{"get_policy",		daxfiGetPolicy,		METH_VARARGS},
	{NULL,			NULL,			0}
};

/* Initialize the module. */
void
MODNAME()
{
	(void) Py_InitModule(MODNAMESTR, _IpfilterMethods);
}



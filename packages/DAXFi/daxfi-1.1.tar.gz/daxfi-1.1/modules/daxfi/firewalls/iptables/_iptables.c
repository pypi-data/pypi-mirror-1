/*
 * Iptables functions for DAXFi.
 * Copyright 2001, 2002 Davide Alberani <alberanid@libero.it>
 *
 * Many portions of this code are 'stolen' from GPLed works of
 * others people, mainly Paul `Rusty' Russell and the authors of
 * the GNU C Library.
 * Obviously if this code sucks (and it *really* sucks) it's only
 * my fault. :-)
 *
 * This code is released under GPL license.
 *
 */


#include <Python.h>
#include <syslog.h>

#include "../common.c"

#include <libiptc/libip4tc.c>
#include <linux/netfilter_ipv4/ipt_limit.h>
#include <linux/netfilter_ipv4/ipt_state.h>
#include <linux/netfilter_ipv4/ip_conntrack.h>
#include <linux/netfilter_ipv4/ipt_LOG.h>
#include <linux/netfilter_ipv4/ipt_REJECT.h>
#include <linux/netfilter_ipv4/ip_nat.h>


/* String version of the log priority. */
struct ipt_log_names {
	const char *name; 
	unsigned int level;
};

static struct ipt_log_names ipt_log_names[] = {
	{ "alert", LOG_ALERT },
	{ "crit", LOG_CRIT },
	{ "debug", LOG_DEBUG },
	{ "emerg", LOG_EMERG },
	{ "err", LOG_ERR },
	{ "info", LOG_INFO },
	{ "notice", LOG_NOTICE },
	{ "panic", LOG_EMERG },
	{ "warning", LOG_WARNING }
};


/* Names of the tcp flags. */
struct tcp_flag_names {
	const char *name;
	unsigned int flag;
};

static struct tcp_flag_names tcp_flag_names[] = {
	{ "ack", 0x10 },
	{ "fin", 0x01 },
	{ "push", 0x08 },
	{ "rst", 0x04 },
	{ "syn", 0x02 },
	{ "urg", 0x20 },
	{ "none", 0 }
};


/* Used with the REJECT target. */
struct reject_names {
	const char *name;
	const char *alias;
	enum ipt_reject_with with;
	const char *desc;
};

static const struct reject_names reject_table[] = {
	{"3/0", "net-unreach",
		IPT_ICMP_NET_UNREACHABLE, "ICMP network unreachable"},
	{"3/1", "host-unreach",
		IPT_ICMP_HOST_UNREACHABLE, "ICMP host unreachable"},
	{"3/3", "port-unreach",
		IPT_ICMP_PORT_UNREACHABLE, "ICMP port unreachable (default)"},
	{"3/2", "proto-unreach",
		IPT_ICMP_PROT_UNREACHABLE, "ICMP protocol unreachable"},
	{"3/9", "net-prohib",
		IPT_ICMP_NET_PROHIBITED, "ICMP network prohibited"},
	{"3/10", "host-prohib",
		IPT_ICMP_HOST_PROHIBITED, "ICMP host prohibited"},
	{"tcp-reset", "tcp-reset",
		IPT_TCP_RESET, "TCP RST packet"}
};


/* Here we collect informations about many matches. */
struct data_struct
{
	/* TCP/UDP */
	u_int16_t spts[2];	/* Source port range. */
	u_int16_t dpts[2];	/* Destination port range. */
	u_int8_t proto_invflags; /* TCP/UDP/ICMP */

	/* TCP */
	u_int8_t option;	/* TCP Option iff non-zero*/
	u_int8_t flg_mask;	/* TCP flags mask byte */
	u_int8_t flg_cmp;	/* TCP flags compare byte */

	/* ICMP */
	u_int8_t type;		/* type to match */
	u_int8_t code[2];	/* range of code */

	/* LIMIT */
	u_int32_t avg;		/* Average secs between packets*scale */
	u_int32_t burst;	/* Period multiplier for upper limit. */

	/* STATE */
	unsigned int statemask;
};

static struct data_struct data_empty = {
	{0, 0}, {0, 0}, 0,	/* TCP/UDP */
	0, 0, 0,		/* TCP */
	0, {0, 0},		/* ICMP */
	0, 0,			/* LIMIT */
	0			/* STATE */
};


/* Infos in the target. */
struct target_struct
{
	/* LOG */
	unsigned char level;
	unsigned char logflags;
	char prefix[30];

	/* REJECT */
	enum ipt_reject_with with;

	/* SNAT/DNAT */
	unsigned int natflags;
	u_int32_t min_ip, max_ip;
	union ip_conntrack_manip_proto min, max;
};

static struct target_struct target_empty = {
	'\0', '\0', "",		/* LOG */
	0,			/* REJECT */
	0, 0, 0			/* NAT */
};


/* 's' will point to a string with the priority level. */
static void
get_log_level(unsigned char level,
		char *s)
{
	unsigned int i = 0;
	for (i = 0;
		i < sizeof(ipt_log_names) / sizeof(struct ipt_log_names);
		i++) {
		if (level == ipt_log_names[i].level) {
			strncpy(s, ipt_log_names[i].name, 32);
			break;
		}
	}
}


/* Get the parameter for the --reject-with option. */
static void
get_reject_with(enum ipt_reject_with with,
		char *s)
{
	unsigned int i;
	for (i = 0;
		i < sizeof(reject_table)/sizeof(struct reject_names);
		i++) {
		if (reject_table[i].with == with)
			break;
	}
	strncpy(s, reject_table[i].name, 64);
}


/* has_match() return true if the given rule have a 'name' match. */
static int
match_name(const struct ipt_entry_match *m,
		const struct ipt_ip *ip,
		unsigned short int *ret,
		char *name)
{
	unsigned short int ok = 1;
	if (!strcmp(m->u.user.name, name)) {
		memcpy(ret, &ok, sizeof(unsigned short int));
		return 1;
	}
	return 0;
}

static int
has_match(const struct ipt_entry *e,
		char *name)
{
	unsigned short int ret = 0;
	IPT_MATCH_ITERATE(e, match_name, &e->ip, &ret, name);
	return ret;
}


/* Return true if the target of this rule is 'name'. */
static int
target_is(struct ipt_entry_target *t,
		char *name)
{
	if (!strncmp(t->u.user.name, name, 32))
		return 1;
	return 0;
}


/* Gather infos from the matches. */
static int
collect_info(const struct ipt_entry_match *m,
		const struct ipt_ip *ip, struct data_struct *d)
{

	if (!strcmp(m->u.user.name, "tcp")) {
		const struct ipt_tcp *tcpinfo =
			(struct ipt_tcp *)m->data;
		memcpy(d->spts, tcpinfo->spts, sizeof(u_int16_t)*2);
		memcpy(d->dpts, tcpinfo->dpts, sizeof(u_int16_t)*2);
		d->option = tcpinfo->option;
		d->flg_mask = tcpinfo->flg_mask;
		d->flg_cmp = tcpinfo->flg_cmp;
		d->proto_invflags = tcpinfo->invflags;
	}

	else if (!strcmp(m->u.user.name, "udp")) {
		const struct ipt_udp *udpinfo = 
			(struct ipt_udp *)m->data;
		memcpy(d->spts, udpinfo->spts, sizeof(u_int16_t)*2);
		memcpy(d->dpts, udpinfo->dpts, sizeof(u_int16_t)*2);
		d->proto_invflags = udpinfo->invflags;
	}

	else if (!strcmp(m->u.user.name, "icmp")) {
		const struct ipt_icmp *icmpinfo =
			(struct ipt_icmp *)m->data;
		memcpy(d->code, icmpinfo->code, sizeof(u_int8_t)*2);
		d->type = icmpinfo->type;
		d->proto_invflags = icmpinfo->invflags;
	}

	else if (!strcmp(m->u.user.name, "limit")) {
		const struct ipt_rateinfo *limitinfo =
			(struct ipt_rateinfo *)m->data;
		d->avg = limitinfo->avg;
		d->burst = limitinfo->burst;
	}

	else if (!strcmp(m->u.user.name, "state")) {
		const struct ipt_state_info *stateinfo =
			(struct ipt_state_info *)m->data;
		d->statemask = stateinfo->statemask;
	}

	return 0;
}


/* Get infos from the target structure. */
static void
get_target_info(struct ipt_entry_target *t,
		struct target_struct *ts)
{
	if (!strncmp(t->u.user.name, "LOG", 32)) {
		const struct ipt_log_info *loginfo =
			(struct ipt_log_info *)t->data;
		ts->level = loginfo->level;
		ts->logflags = loginfo->logflags;
		strncpy(ts->prefix, loginfo->prefix, 30);
	}

	else if (!strncmp(t->u.user.name, "REJECT", 32)) {
		const struct ipt_reject_info *reject =
			(struct ipt_reject_info *)t->data;
		ts->with = reject->with;
	}

	else if (!strcmp(t->u.user.name, "SNAT") ||
			!strcmp(t->u.user.name, "DNAT") ||
			!strcmp(t->u.user.name, "MASQUERADE") ||
			!strcmp(t->u.user.name, "REDIRECT")) {
		const struct ip_nat_multi_range *snat =
			(struct ip_nat_multi_range *)t->data;
		ts->natflags = snat->range[0].flags;
		ts->min_ip = snat->range[0].min_ip;
		ts->max_ip = snat->range[0].max_ip;
		ts->min = snat->range[0].min;
		ts->max = snat->range[0].max;
	}
}


/* Return 1 if the kernel supports iptables. */
static PyObject*
daxfiIsSupported(PyObject *self, PyObject *args)
{
	iptc_handle_t handle = NULL;
	char *table = "filter";

	if (PyTuple_Size(args) != 0) {
		PyErr_SetString(PyExc_AttributeError,
			"is_supported() requires no arguments");
		return NULL;
	}

	handle = iptc_init(table);
	if (!handle)
		return Py_BuildValue("i", 0);

	return Py_BuildValue("i", 1);
}


/* Return a string representing the policy for the given chain. */
static PyObject*
daxfiGetPolicy(PyObject *self, PyObject *args)
{
	iptc_handle_t handle = NULL;
	char *table = "filter";
	struct ipt_counters counters;
	PyObject *chain = NULL;
	char chain_name[IPT_TABLE_MAXNAMELEN];
	char *policy = NULL;
	char pol[42];

	pol[0] = '\0';
	if (!PyArg_ParseTuple(args, "O!", &PyString_Type, &chain))
		return NULL;

	handle = iptc_init(table);
	if (handle == NULL) {
		PyErr_SetString(PyExc_OSError, "error initializing `filter'" \
				" table; iptables support missing, or you" \
				" have not root privileges");
		return NULL;
	}

	sprintf(chain_name, PyString_AsString(chain));

	if (!strcmp(chain_name, "in"))
		sprintf(chain_name, "INPUT");
	if (!strcmp(chain_name, "out"))
		sprintf(chain_name, "OUTPUT");

	policy = (char *)iptc_get_policy(chain_name, &counters, &handle);
	if (policy == NULL) {
		return PyString_FromString("");
	}

	sprintf(pol, iptc_get_policy(chain_name, &counters, &handle));

	if (!strcmp(pol, "ACCEPT"))
		sprintf(pol, "accept");
	if (!strcmp(pol, "DROP"))
		sprintf(pol, "drop");
	if (!strcmp(pol, "REJECT"))
		sprintf(pol, "reject");

	return PyString_FromString(pol);
}


/* Return a list of chain names. */
static PyObject*
daxfiListChains(PyObject *self, PyObject *args)
{
	iptc_handle_t handle = NULL;
	char *table = "filter";
	PyObject *result = PyList_New(0);
	PyObject *s = NULL;
	const char *str;

	if (PyTuple_Size(args) != 0) {
		PyErr_SetString(PyExc_AttributeError,
			"list_chains() requires no arguments");
		return NULL;
	}

	handle = iptc_init(table);
	if (handle == NULL) {
		PyErr_SetString(PyExc_OSError, "error initializing `filter'" \
				" table; iptables support missing, or you" \
				" have not root privileges");
		return NULL;
	}

	for (str = iptc_first_chain(&handle);
			str;
			str = iptc_next_chain(&handle)) {
		if (!strcmp(str, "INPUT"))
			s = PyString_FromString("in");
		else if (!strcmp(str, "OUTPUT"))
			s = PyString_FromString("out");
		else if (!strcmp(str, "FORWARD"))
			s = PyString_FromString("forward");
		else
			s = PyString_FromString(str);
		PyList_Append(result, s);
	}

	return Py_BuildValue("O", result);
}


/* Return a list of XML strings that represents the rule.
   Requires a chain name as parameter. */
static PyObject*
daxfiListRules(PyObject *self, PyObject *args)
{
	PyObject *chain;
	iptc_handle_t handle = NULL;
	char *table_filter = "filter";
	char *table_nat = "nat";
	char *table = table_filter;
	int nat = 0;
	char chain_name[IPT_TABLE_MAXNAMELEN];
	const struct ipt_entry *e;
	struct ipt_entry_target *tg;
	PyObject *result = PyList_New(0);

	if (!PyArg_ParseTuple(args, "O!|i", &PyString_Type, &chain, &nat))
		return NULL;

	if (nat)
		table = table_nat;

	handle = iptc_init(table);
	if (handle == NULL) {
		PyErr_SetString(PyExc_OSError, "error initializing `filter'" \
				" table; iptables support missing, or you" \
			       	" do not have root privileges");
		return NULL;
	}

	snprintf(chain_name, IPT_TABLE_MAXNAMELEN-1, PyString_AsString(chain));

	if (!strcmp(chain_name, "in"))
		sprintf(chain_name, "INPUT");
	else if (!strcmp(chain_name, "out"))
		sprintf(chain_name, "OUTPUT");

	e = iptc_first_rule(chain_name, &handle);

	while (e) {
		struct data_struct data = data_empty;
		struct target_struct targetdata = target_empty;
		char strnfix[1024];
		/* XXX: Ugly! */
		int has_proto = 0;
		char xml[10240];

		strnfix[1023] = '\0';
		xml[0] = '\0';

		strcat(xml, XML_HEADER);
		/* collect rule's informations */
		/* iterate over matches */
		IPT_MATCH_ITERATE(e, collect_info, &e->ip, &data);
		/* get target's infos */
		tg=(STRUCT_ENTRY_TARGET *)GET_TARGET((STRUCT_ENTRY *)e);
		get_target_info(tg, &targetdata);

		if (!nat) {
			if (!strcmp(chain_name, "INPUT"))
				addval(xml, "direction", "in");
			else if (!strcmp(chain_name, "OUTPUT"))
				addval(xml, "direction", "out");
		}

		/* source ip */
		if (e->nfcache & NFC_IP_SRC) {
			if (e->ip.invflags & IPT_INV_SRCIP)
				snprintf(strnfix, 34,
					"! %u.%u.%u.%u/%u.%u.%u.%u",
					IP_PARTS(e->ip.src.s_addr),
					IP_PARTS(e->ip.smsk.s_addr));
			else
				snprintf(strnfix, 32,
					"%u.%u.%u.%u/%u.%u.%u.%u",
					IP_PARTS(e->ip.src.s_addr),
					IP_PARTS(e->ip.smsk.s_addr));

			if (strcmp(strnfix, "0.0.0.0/0.0.0.0"))
				addval(xml, "source-ip", strnfix);
		}

		/* destination ip */
		if (e->nfcache & NFC_IP_DST) {
			if (e->ip.invflags & IPT_INV_DSTIP)
				snprintf(strnfix, 34,
					"! %u.%u.%u.%u/%u.%u.%u.%u",
					IP_PARTS(e->ip.dst.s_addr),
					IP_PARTS(e->ip.dmsk.s_addr));
			else
				snprintf(strnfix, 32,
					"%u.%u.%u.%u/%u.%u.%u.%u",
					IP_PARTS(e->ip.dst.s_addr),
					IP_PARTS(e->ip.dmsk.s_addr));

			if (strcmp(strnfix, "0.0.0.0/0.0.0.0"))
				addval(xml, "destination-ip", strnfix);
		}
		
		/* interface */
		if (e->nfcache & NFC_IP_IF_IN) {
			int i = 0;
			int len = 0;
			int slen = 0;
			if (e->ip.invflags & IPT_INV_VIA_IN)
				snprintf(strnfix, IFNAMSIZ + 2,
					"! %s", e->ip.iniface);
			else
				snprintf(strnfix, IFNAMSIZ,
					"%s", e->ip.iniface);

			while (i < IFNAMSIZ) {
				if (e->ip.iniface_mask[i])
					len++;
				i++;
			}
			slen = strlen(strnfix);
			if (e->ip.invflags & IPT_INV_VIA_IN)
				slen = slen - 2;
			if (len == slen) {
				slen = strlen(strnfix);
				strnfix[slen] = '+';
				strnfix[slen+1] = '\0';
			}
			addval(xml, "interface", strnfix);
		} else if (e->nfcache & NFC_IP_IF_OUT) {
			/* out interface */
			int i = 0;
			int len = 0;
			int slen = 0;
			if (e->ip.invflags & IPT_INV_VIA_OUT)
				snprintf(strnfix, IFNAMSIZ + 2,
					"! %s", e->ip.outiface);
			else
				snprintf(strnfix, IFNAMSIZ,
					"%s", e->ip.outiface);
			while (i < IFNAMSIZ) {
				if (e->ip.outiface_mask[i])
					len++;
				i++;
			}
			slen = strlen(strnfix);
			if (e->ip.invflags & IPT_INV_VIA_IN)
				slen = slen - 2;
			if (len == slen) {
				slen = strlen(strnfix);
				strnfix[slen] = '+';
				strnfix[slen+1] = '\0';
			}
			addval(xml, "interface", strnfix);
		}

		/* fragment */
		if (e->nfcache & NFC_IP_FRAG) {
			if (e->ip.invflags & IPT_INV_FRAG) {
				addval(xml, "fragment-only", "no");
			}
			else if (e->ip.flags & IPT_F_FRAG) {
				addval(xml, "fragment-only", "yes");
			}
		}

		strncat(xml, ">\n", 2);

		strcat(xml, "    <protocol ");
		/* source port */
		if (e->nfcache & NFC_IP_SRC_PT) {
			if (data.proto_invflags & IPT_TCP_INV_SRCPT) {
				if (data.spts[0] != data.spts[1])
					snprintf(strnfix, 14,
						"! %u:%u",
						data.spts[0],
						data.spts[1]);
				else
					snprintf(strnfix, 8,
						"! %u", data.spts[0]);
			} else {
				if (data.spts[0] != data.spts[1])
					snprintf(strnfix, 12,
						"%u:%u",
						data.spts[0],
						data.spts[1]);
				else
					snprintf(strnfix, 6,
						"%u", data.spts[0]);
			}
			if (strcmp(strnfix, "0") &&
					strcmp(strnfix, "! 0")) {
				if (strcmp(strnfix, "1:65535") &&
						strcmp(strnfix, "0:65535"))
					addval(xml, "source-port", strnfix);
				has_proto = 1;
			}
		}

		/* destination port */
		if (e->nfcache & NFC_IP_DST_PT) {
			if (data.proto_invflags & IPT_TCP_INV_DSTPT) {
				if (data.dpts[0] != data.dpts[1])
					snprintf(strnfix, 14,
						 "! %u:%u",
						 data.dpts[0],
						 data.dpts[1]);
				else
					snprintf(strnfix, 8,
						"! %u", data.dpts[0]);
			} else {
				if (data.dpts[0] != data.dpts[1])
					snprintf(strnfix, 12,
						"%u:%u",
						data.dpts[0],
						data.dpts[1]);
				else
					snprintf(strnfix, 6,
						"%u", data.dpts[0]);
			}
			if (strcmp(strnfix, "0") &&
					strcmp(strnfix, "! 0")) {
				if (strcmp(strnfix, "1:65535") &&
						strcmp(strnfix, "0:65535"))
					addval(xml,"destination-port",strnfix);
				has_proto = 1;
			}
		}

		/* protocol */
		if (e->nfcache & NFC_IP_PROTO) {
			if (e->ip.invflags & IPT_INV_PROTO)
				snprintf(strnfix, 8, "! %u", e->ip.proto);
			else
				snprintf(strnfix, 6, "%u", e->ip.proto);
			addval(xml, "protocol", strnfix);
			has_proto = 1;
		}

		/* tcp packet */
		if (has_match(e, "tcp")) {
			if (data.flg_mask || (data.proto_invflags &
				IPT_TCP_INV_FLAGS)) {
				char *s = strnfix;
				int have_flag = 0;

				if (data.proto_invflags &
						IPT_TCP_INV_FLAGS) {
					snprintf(s, 3, "! ");
					s = s + 2;
				}

				while (data.flg_cmp) {
					unsigned int i;
					for (i = 0;
						(data.flg_cmp &
						 tcp_flag_names[i].flag) == 0;
						i++);
					if (have_flag) {
						sprintf(s, ",");
						s = s + 1;
					}
					snprintf(s, 5, "%s",
						tcp_flag_names[i].name);
					s = s +	strlen(tcp_flag_names[i].name);
					have_flag = 1;
					data.flg_cmp &= \
						~tcp_flag_names[i].flag;
				}
				sprintf(s, "/");
				s = s + 1;
				have_flag = 0;
				while (data.flg_mask) {
					unsigned int i;
					for (i = 0; (data.flg_mask & \
						tcp_flag_names[i].flag) == 0; \
						i++);
					if (have_flag) {
						snprintf(s, 2, ",");
						s = s + 1;
					}
					snprintf(s, 5, "%s",
						tcp_flag_names[i].name);
					s = s + strlen(tcp_flag_names[i].name);
					have_flag = 1;
					data.flg_mask&=~tcp_flag_names[i].flag;
				}
				if (!strcmp(strnfix, "! syn/ack,rst,syn")) {
					addval(xml, "syn-only", "no");
				} else if (!strcmp(strnfix,
							"syn/ack,rst,syn")) {
					addval(xml, "syn-only", "yes");
				} else {
					addval(xml, "tcp-flags", strnfix);
				}
				has_proto = 1;
			}
		}

		/* icmp packet */
		if (has_match(e, "icmp")) {
			char tmp[32];
			tmp[0] = '\0';
			strnfix[0] = '\0';
			if (data.proto_invflags & IPT_ICMP_INV)
				strcat(strnfix, "! ");

			sprintf(tmp, "%u", data.type);
			strcat(strnfix, tmp);
			if (data.code[0] != 0xFF) {
				sprintf(tmp, "/%u", data.code[0]);
				strcat(strnfix, tmp);
			}
			addval(xml, "icmp-type", strnfix);
			has_proto = 1;
		}

		strnfix[0] = '\0';
		/* state */
		if (has_match(e, "state")) {
			if (data.statemask & IPT_STATE_INVALID ||
					data.statemask & \
					IPT_STATE_BIT(IP_CT_NEW)) {
				snprintf(strnfix, 4, "new");
			}
			if (data.statemask &
					IPT_STATE_BIT(IP_CT_RELATED) ||
					data.statemask & \
					IPT_STATE_BIT(IP_CT_ESTABLISHED)) {
				snprintf(strnfix, 8, "related");
			}
			addval(xml, "state", strnfix);
			has_proto = 1;
		}

		if (has_proto) {
			strcat(xml, "/>\n");
		} else {
			xml[strlen(xml) - 12] = '\0';
		}

		/* limit */
		if (has_match(e, "limit")) {
			strcat(xml, "    <limit ");
			snprintf(strnfix, 11, "%u", data.avg);
			/* FIXME: limit always set rate and burst... */
			addval(xml, "rate", strnfix);
			snprintf(strnfix, 11, "%u", data.burst);
			addval(xml, "burst", strnfix);
			strcat(xml, "/>\n");
		}

		strnfix[0] = '\0';

		/* log target */
		if (target_is(tg, "LOG")) {
			strcat(xml, "    <log ");
			get_log_level(targetdata.level, strnfix);
			/* FIXME: define a default value... */
			if (strcmp(strnfix, "warning"))
				addval(xml, "priority", strnfix);
			strcat(xml, "/>\n");
		}

		/* target */
		strnfix[0] = '\0';
		if (strcasecmp(tg->u.user.name, "LOG")) {
			if (strcmp(tg->u.user.name, STANDARD_TARGET) == 0) {
				int pos = *(int *)tg->data;
				if (pos < 0) {
					switch (pos) {
						case -NF_ACCEPT-1:
							sprintf(strnfix,
								"accept");
							break;
						case -NF_DROP-1:
							sprintf(strnfix,
								"drop");
							break;
						case RETURN:
							sprintf(strnfix, 
								"return");
					}
				}
			} else {
				char tgname[256];
				tgname[0] = '\0';
				if (strlen(tg->u.user.name) > 0 &&
						strcasecmp(tg->u.user.name,
							"LOG")) {
					conv_case(tg->u.user.name, tgname, 0);
					sprintf(strnfix, tgname);
				} 
			}

			if (!nat) {
				if (target_is(tg, "REDIRECT") ||
						target_is(tg, "MASQUERADE") ||
						target_is(tg, "SNAT") ||
						target_is(tg, "DNAT")) {
					e = iptc_next_rule(e, &handle);
					continue;
				}
				/* user-defined chains */
				if (strlen(strnfix) == 0) {
					sprintf(strnfix,
						iptc_get_target(e, &handle));
				}
				if (strlen(strnfix) > 0) {
					strcat(xml, "    <target ");
					addval(xml, "target", strnfix);
				}
			} else {
				if (!(target_is(tg, "REDIRECT") ||
						target_is(tg, "MASQUERADE") ||
						target_is(tg, "SNAT") ||
						target_is(tg, "DNAT"))) {
					e = iptc_next_rule(e, &handle);
					continue;
				}
				strcat(xml, "    <nat ");
				if (!strcmp(strnfix, "masquerade"))
					sprintf(strnfix, "masq");
				addval(xml, "nat", strnfix);
				if (targetdata.natflags &
					       IP_NAT_RANGE_MAP_IPS) {
					struct in_addr a;
					a.s_addr = targetdata.min_ip;
					sprintf(strnfix, "%s",
							addr_to_dotted(&a));
					if (targetdata.min_ip !=
							targetdata.max_ip) {
						a.s_addr = targetdata.max_ip;
						strcat(strnfix, ":");
						strcat(strnfix,
							addr_to_dotted(&a));
					}
					addval(xml, "to-address", strnfix);
				}

				if (targetdata.natflags &
						IP_NAT_RANGE_PROTO_SPECIFIED) {
					sprintf(strnfix, "%hu",
						ntohs(targetdata.min.tcp.port));
					if (targetdata.max.tcp.port !=
						targetdata.min.tcp.port) {
						char tmp[32];
						strcat(strnfix, ":");
						sprintf(tmp, "%hu",
						ntohs(targetdata.max.tcp.port));
						strcat(strnfix, tmp);
					}
					addval(xml, "to-port", strnfix);
				}
			}

			/* reject target */
			if (target_is(tg, "REJECT")) {
				get_reject_with(targetdata.with, strnfix);
				if (strncmp(strnfix, "3/3", 22))
					addval(xml, "reject-with", strnfix);
			}
			strcat(xml, "/>\n");
		}

		strcat(xml, "  </rule>\n</append>\n");

		PyList_Append(result, PyString_FromString(xml));

		e = iptc_next_rule(e, &handle);
	}

	return Py_BuildValue("O", result);
}


/* Exported functions. */
static PyMethodDef _IptablesMethods[] = {
	{"list_rules",		daxfiListRules,		METH_VARARGS},
	{"list_chains",		daxfiListChains,	METH_VARARGS},
	{"is_supported",	daxfiIsSupported,	METH_VARARGS},
	{"get_policy",		daxfiGetPolicy,		METH_VARARGS},
	{NULL,			NULL,			0}
};


/* Initialize the module. */
void
MODNAME()
{
	(void) Py_InitModule(MODNAMESTR, _IptablesMethods);
}



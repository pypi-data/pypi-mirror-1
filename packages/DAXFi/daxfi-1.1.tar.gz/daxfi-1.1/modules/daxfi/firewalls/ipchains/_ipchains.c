/*
 * Ipchains functions for DAXFi.
 * Copyright 2001, 2002 Davide Alberani <alberanid@libero.it>
 *
 * Many portions of this code are 'stolen' from GPLed works of
 * other people, mainly Paul `Rusty' Russell and the authors of
 * the GNU C Library.
 * Obviously if this code sucks (and it *really* sucks) it's only
 * my fault. :-)
 *
 * This code is released under GPL license.
 *
 */


#include <Python.h>
#include <libipfwc/libipfwc.c>

#include "../common.c"


/* Return 1 if kernel supports for ipchains is present. */
static PyObject*
daxfiIsSupported(PyObject *self, PyObject *args)
{
	unsigned int num_chains;
	struct ipfwc_fwchain *chains;

	if (PyTuple_Size(args) != 0) {
		PyErr_SetString(PyExc_AttributeError,
				"is_supported() requires no arguments");
		return NULL;
	}

	chains = ipfwc_get_chainnames(&num_chains);
	if (!chains)
		return Py_BuildValue("i", 0);

	return Py_BuildValue("i", 1);
}


/* Return a string representing the policy for the given chain. */
static PyObject*
daxfiGetPolicy(PyObject *self, PyObject *args)
{
	PyObject *chain;
	char chain_name[IP_FW_MAX_LABEL_LENGTH];
	char pol[42];
	unsigned int num_chains = 0;
	struct ipfwc_fwchain *chains;
	int i = 0;

	if (!PyArg_ParseTuple(args, "O!", &PyString_Type, &chain))
		return NULL;

	snprintf(chain_name, IP_FW_MAX_LABEL_LENGTH-1,
		PyString_AsString(chain));

	if (!strcmp(chain_name, "in"))
		snprintf(chain_name, IP_FW_MAX_LABEL_LENGTH-1, "input");
	else if (!strcmp(chain_name, "out"))
		snprintf(chain_name, IP_FW_MAX_LABEL_LENGTH-1, "output");
	
	chains = ipfwc_get_chainnames(&num_chains);

	if (!chains) {
		PyErr_SetString(PyExc_OSError, "error: ipchains support"
				" missing, or you have not root privileges");
		return NULL;
	}

	pol[0] = '\0';
	for (i = 0; i < num_chains; i++) {
		if (!strcmp(chain_name, chains[i].label)) {
			sprintf(pol, chains[i].policy);
			break;
		}
	}

	if (!strcmp(pol, "ACCEPT"))
		sprintf(pol, "accept");
	else if (!strcmp(pol, "DENY"))
		sprintf(pol, "drop");
	else if (!strcmp(pol, "REJECT"))
		sprintf(pol, "reject");

	return PyString_FromString(pol);
}


/* Return the list of chains. */
static PyObject*
daxfiListChains(PyObject *self, PyObject *args)
{
	int i = 0;
	unsigned int num_chains;
	struct ipfwc_fwchain *chains;
	PyObject *result = PyList_New(0);
	PyObject *s = NULL;

	if (PyTuple_Size(args) != 0) {
		PyErr_SetString(PyExc_AttributeError,
				"list_chains() requires no arguments");
		return NULL;
	}

	chains = ipfwc_get_chainnames(&num_chains);
	if (!chains) {
		PyErr_SetString(PyExc_OSError, "error: ipchains support"
			       " missing, or you have not root privileges");
		return NULL;
	}

	for (i = 0; i < num_chains; i++) {
		if (!strcmp(chains[i].label, "input"))
			s = PyString_FromString("in");
		else if (!strcmp(chains[i].label, "output"))
			s = PyString_FromString("out");
		else
			s = PyString_FromString(chains[i].label);
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
	char chain_name[IP_FW_MAX_LABEL_LENGTH];
	struct ipfwc_fwrule *rules;
	unsigned int num_rules, cur_rule_num;
	int nat = 0;
	PyObject *result = PyList_New(0);

	if (!PyArg_ParseTuple(args, "O!|i", &PyString_Type, &chain, &nat))
		return NULL;

	snprintf(chain_name, IP_FW_MAX_LABEL_LENGTH-1,
			PyString_AsString(chain));

	if (!strcmp(chain_name, "in"))
		snprintf(chain_name, IP_FW_MAX_LABEL_LENGTH-1, "input");
	else if (!strcmp(chain_name, "out"))
		snprintf(chain_name, IP_FW_MAX_LABEL_LENGTH-1, "output");

	rules = ipfwc_get_rules(&num_rules, 0);
	if (!rules) {
		PyErr_SetString(PyExc_OSError, "cannot read the rules;" \
				" ipchains support missing, or you have not" \
			       	" root privileges");
		return NULL;
	}

	for (cur_rule_num = 0;
			cur_rule_num < num_rules;
			cur_rule_num++) {
		if (strcmp(rules[cur_rule_num].chain->label,
					chain_name) == 0) {
			const struct ip_fwuser *fw = &rules[cur_rule_num].ipfw;
			char xml[10240];

			char strnfix[1024];
			char strnfix2[1024];
			char strtmp[1024];

			strnfix[1023] = '\0';
			strnfix2[1023] = '\0';

			strtmp[0] = '\0';
			xml[0] = '\0';

			strcat(xml, XML_HEADER);

			strnfix[0] = '\0';
			strnfix2[0] = '\0';
			if (!strcmp(chain_name, "input"))
				sprintf(strnfix, "in");
			else if (!strcmp(chain_name, "output"))
				sprintf(strnfix, "out");
			/* the chain */
			if (!nat && strlen(strnfix))
				addval(xml, "direction", strnfix);
			strnfix[0] = '\0';

			/* source ip */
			if (fw->ipfw.fw_invflg & IP_FW_INV_SRCIP)
				strncpy(strnfix, "! ", 3);
			else
				strnfix[0] = '\0';
			strncat(strnfix,addr_to_dotted(&(fw->ipfw.fw_src)),15);
			strncat(strnfix, "/", 1);
			strncat(strnfix,addr_to_dotted(&(fw->ipfw.fw_smsk)),15);
			if (strcmp(strnfix, "0.0.0.0/0.0.0.0"))
				addval(xml, "source-ip", strnfix);

			/* destination ip */
			if (fw->ipfw.fw_invflg & IP_FW_INV_DSTIP)
				strncpy(strnfix, "! ", 3);
			else
				strnfix[0] = '\0';
			strncat(strnfix,addr_to_dotted(&(fw->ipfw.fw_dst)),15);
			strncat(strnfix, "/", 1);
			strncat(strnfix,addr_to_dotted(&(fw->ipfw.fw_dmsk)),15);
			if (strcmp(strnfix, "0.0.0.0/0.0.0.0"))
				addval(xml, "destination-ip", strnfix);

			/* interface */
			if (fw->ipfw.fw_invflg & IP_FW_INV_VIA)
				strncpy(strnfix, "! ", 3);
			else
				strnfix[0] = '\0';
			strncat(strnfix, fw->ipfw.fw_vianame, IFNAMSIZ+1);
			if (fw->ipfw.fw_flg & IP_FW_F_WILDIF)
				strncat(strnfix, "+", 1);
			if (strlen(strnfix) > 1) {
				addval(xml, "interface", strnfix);
			}

			/* fragment */
			if (fw->ipfw.fw_flg & IP_FW_F_FRAG) {
				if (fw->ipfw.fw_invflg & IP_FW_INV_FRAG)
					addval(xml, "fragment-only", "no");
				else
					addval(xml, "fragment-only", "yes");
			}
			strncat(xml, ">\n", 2);

			if ((fw->ipfw.fw_proto == IPPROTO_TCP ||
				fw->ipfw.fw_proto == IPPROTO_UDP)
				&& !(fw->ipfw.fw_invflg & IP_FW_INV_PROTO)) {

				/* source port */
				if (fw->ipfw.fw_invflg & IP_FW_INV_SRCPT)
					strncpy(strnfix, "! ", 3);
				else
					strnfix[0] = '\0';
				if (fw->ipfw.fw_spts[0] == \
						fw->ipfw.fw_spts[1]) {
					snprintf(strnfix2, 6, "%u", \
							fw->ipfw.fw_spts[0]);
					strncat(strnfix, strnfix2, 5);
				} else {
					snprintf(strnfix2, 6, "%u", \
							fw->ipfw.fw_spts[0]);
					strncat(strnfix, strnfix2, 5);
					strncat(strnfix, ":", 1);
					snprintf(strnfix2, 6, "%u", \
							fw->ipfw.fw_spts[1]);
					strncat(strnfix, strnfix2, 5);
				}
				if (strcmp(strnfix, "1:65535") &&
						strcmp(strnfix, "0:65535"))
					addval(strtmp, "source-port", strnfix);

				/* destination port */
				if (fw->ipfw.fw_invflg & IP_FW_INV_DSTPT)
					strncpy(strnfix, "! ", 3);
				else
					strnfix[0] = '\0';
				if (fw->ipfw.fw_dpts[0] == \
						fw->ipfw.fw_dpts[1]) {
					snprintf(strnfix2, 6, "%u", \
							fw->ipfw.fw_dpts[0]);
					strncat(strnfix, strnfix2, 5);
				} else {
					snprintf(strnfix2, 6, "%u", \
							fw->ipfw.fw_dpts[0]);
					strncat(strnfix, strnfix2, 5);
					strncat(strnfix, ":", 1);
					snprintf(strnfix2, 6, "%u", \
							fw->ipfw.fw_dpts[1]);
					strncat(strnfix, strnfix2, 5);
				}
				if (strcmp(strnfix, "1:65535") &&
						strcmp(strnfix, "0:65535"))
					addval(strtmp, "destination-port",
							strnfix);
			} /* end of source/destination ports */

			if (fw->ipfw.fw_flg & IP_FW_F_TCPSYN) {
				if (fw->ipfw.fw_invflg & IP_FW_INV_SYN)
					addval(strtmp, "syn-only", "no");
				else
					addval(strtmp, "syn-only", "yes");
			}

			/* protocol */
			if (fw->ipfw.fw_invflg & IP_FW_INV_PROTO)
				strncpy(strnfix, "! ", 3);
			else
				strnfix[0] = '\0';
			snprintf(strnfix2, 6, "%u", fw->ipfw.fw_proto);
			strncat(strnfix, strnfix2, 5);
			if (strcmp(strnfix, "0"))
				addval(strtmp, "protocol", strnfix);

			/* ICMP handled specially. */
			strnfix2[0] = '\0';
			if ((fw->ipfw.fw_invflg & IP_FW_INV_SRCPT) ||
				(fw->ipfw.fw_invflg & IP_FW_INV_DSTPT))
				strcat(strnfix2, "! ");
			else
				strnfix[0] = '\0';
			if (fw->ipfw.fw_proto == IPPROTO_ICMP) {
				sprintf(strnfix2, "%u", fw->ipfw.fw_spts[0]);
				strcat(strnfix, strnfix2);
				if (fw->ipfw.fw_dpts[1] != 0xFFFF) {
					sprintf(strnfix2, "/%u",
							fw->ipfw.fw_dpts[1]);
					strcat(strnfix, strnfix2);
				}
				if (strlen(strnfix) > 0 &&
						strcmp(strnfix, "0"))
					addval(strtmp, "icmp-type", strnfix);
			}
			if (strlen(strtmp) > 0) {
				strcat(xml, "    <protocol ");
				strcat(xml, strtmp);
				strcat(xml, "/>\n");
			}

			/* target */
			if (!nat) {
				strcat(xml, "    <target ");
				strnfix[0] = '\0';
				conv_case((char *)fw->label, strnfix, 0);
				if (!strcmp(strnfix, "redirect") ||
						!strcmp(strnfix, "masq"))
					continue;
				if (!strcasecmp(strnfix, "DENY"))
					strcpy(strnfix, "drop");
				addval(xml, "target", strnfix);
				strncat(xml, "/>\n", 3);
			} else {
				strcat(xml, "    <nat ");
				conv_case((char *)fw->label, strnfix, 0);
				if (strcmp(strnfix, "redirect") &&
						strcmp(strnfix, "masq"))
					continue;
				addval(xml, "nat", strnfix);
				if (!strcmp(strnfix, "redirect")) {
					sprintf(strnfix, "%u",
							fw->ipfw.fw_redirpt);
					addval(xml, "to-port", strnfix);
				}
				strcat(xml, "/>\n");
			}

			/* log */
			if (fw->ipfw.fw_flg & IP_FW_F_PRN) {
				strcat(xml, "    <log />\n");
			}

			strcat(xml, "  </rule>\n</append>\n");

			PyList_Append(result, PyString_FromString(xml));
		}
	}

	return Py_BuildValue("O", result);
}


/* Functions defined in this module. */
static PyMethodDef _IpchainsMethods[] = {
	{"list_rules",		daxfiListRules,		METH_VARARGS},
	{"list_chains",		daxfiListChains,	METH_VARARGS},
	{"is_supported",	daxfiIsSupported,	METH_VARARGS},
	{"get_policy",		daxfiGetPolicy,		METH_VARARGS},
	{NULL,			NULL,			0}
};


/* Initialize this module. */
void
MODNAME()
{
	(void) Py_InitModule(MODNAMESTR, _IpchainsMethods);
}



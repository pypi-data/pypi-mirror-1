/*
 * Ipfwadm functions for DAXFi.
 * Copyright 2001, 2002 Davide Alberani <alberanid@libero.it>
 *
 * Many portions of this code are 'stolen' from GPLed works of
 * others people, mainly Jos Vos and the authors of the GNU C Library.
 * Obviously if this code sucks (and it *really* sucks) it's only
 * my fault. :-)
 *
 * This code is released under GPL license.
 *
 */


#include <Python.h>
#include <unistd.h>
#include <netinet/in.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <linux/icmp.h>
#include <linux/if.h>
#include <linux/netfilter_ipv4/ipfwadm_core.h>

#include "../common.c"


static char *procfiles[5] = {"/proc/net/ip_forward", "/proc/net/ip_input",
	"/proc/net/ip_output", "/proc/net/ip_acct", "/proc/net/ip_masquerade"};

static int
read_procinfo(FILE *fp, struct ip_fw *fw)
{
	unsigned long temp[5];
	int n, i;
	unsigned short tosand, tosxor;

	n = fscanf(fp, "%lX/%lX->%lX/%lX %16s %lX %hX %hu %hu %lu %lu",
			&temp[0], &temp[1], &temp[2], &temp[3],
			fw->fw_vianame, &temp[4],
				&fw->fw_flg, &fw->fw_nsp, &fw->fw_ndp,
				&fw->fw_pcnt, &fw->fw_bcnt);
	if (n == 11) {
		for (i = 0; i < IP_FW_MAX_PORTS; i++)
			if (fscanf(fp, "%hu", &fw->fw_pts[i]) != 1)
				return n;
		if (fscanf(fp, " A%hX X%hX", &tosand, &tosxor) != 2)
			return n;
		if (!strcmp("-", fw->fw_vianame))
			(fw->fw_vianame)[0] = '\0';
		fw->fw_tosand = (unsigned char) tosand;
		fw->fw_tosxor = (unsigned char) tosxor;

		fw->fw_src.s_addr = (__u32) htonl(temp[0]);
		fw->fw_dst.s_addr = (__u32) htonl(temp[2]);
		fw->fw_via.s_addr = (__u32) htonl(temp[4]);
		fw->fw_smsk.s_addr = (__u32) htonl(temp[1]);
		fw->fw_dmsk.s_addr = (__u32) htonl(temp[3]);
	}
	return n;
}

/* Return 1 if the kernel support ipfwadm. */
static PyObject*
daxfiIsSupported(PyObject *self, PyObject *args)
{
	if (PyTuple_Size(args) != 0) {
		PyErr_SetString(PyExc_AttributeError,
				"is_supported() requires no arguments");
		return NULL;
	}

	if ((fopen("/proc/net/ip_input", "r") == NULL) ||
			(getuid() != 0))
		return Py_BuildValue("i", 0);
	return Py_BuildValue("i", 1);
}


/* Return a list of chain names. */
static PyObject*
daxfiListChains(PyObject *self, PyObject *args)
{
	int chn = 1;
	FILE *fp;
	char *procfile;
	PyObject *result = PyList_New(0);

	procfile = procfiles[chn];
	if ((fp = fopen(procfile, "r")) == NULL) {
		PyErr_SetString(PyExc_OSError, "ipfwadm not supported, or" \
				" /proc filesystem not mounted");
		return NULL;
	}

	PyList_Append(result, PyString_FromString("in"));
	PyList_Append(result, PyString_FromString("out"));
	PyList_Append(result, PyString_FromString("forward"));
	fclose(fp);
	return Py_BuildValue("O", result);
}


/* Return a string representing the policy for the given chain. */
static PyObject*
daxfiGetPolicy(PyObject *self, PyObject *args)
{
	PyObject *chain;
	char chain_name[42];
	int chn = 1;
	FILE *fp;
	char *procfile;
	int policy;
	struct ip_fw *fw;
	char buf[256];
	char pol[42];

	if (!PyArg_ParseTuple(args, "O!", &PyString_Type, &chain))
		return NULL;

	snprintf(chain_name, 41, PyString_AsString(chain));

	if (!strcmp(chain_name, "in") || !strcmp(chain_name, "input"))
		chn = 1;
	else if (!strcmp(chain_name, "out")|| !strcmp(chain_name, "output"))
		chn = 2;
	else if (!strcmp(chain_name, "forward"))
		chn = 0;
	else {
		PyErr_SetString(PyExc_OSError, "only in, forward and" \
				" out are valid direction names");
		return NULL;
	}

	procfile = procfiles[chn];
	if ((fp = fopen(procfile, "r")) == NULL) {
		PyErr_SetString(PyExc_OSError, "ipfwadm not supported, or" \
				" /proc filesystem not mounted");
		return NULL;
	}

	fw = (struct ip_fw *) malloc(sizeof(struct ip_fw));
	fscanf(fp, "%[^,], default %d", buf, &policy);

	pol[0] = '\0';
	switch (policy) {
		case IP_FW_F_ACCEPT:
			sprintf(pol, "accept");
			break;
		case IP_FW_F_ICMPRPL:
			sprintf(pol, "reject");
			break;
		case 0:
			sprintf(pol, "drop");
			break;
	}

	return PyString_FromString(pol);
}


/* Return a list of XML strings that represents the rule.
   Requires a chain name as parameter. */
static PyObject*
daxfiListRules(PyObject *self, PyObject *args)
{
	PyObject *chain;
	char chain_name[42];
	int chn = 1;

	FILE *fp;
	char *procfile;
	int policy;
	char buf[256];
	int n;
	struct ip_fw *fw;
	int nat = 0;

	PyObject *result = PyList_New(0);

	if (!PyArg_ParseTuple(args, "O!|i", &PyString_Type, &chain, &nat))
		return NULL;

	snprintf(chain_name, 41, PyString_AsString(chain));

	if (!strcmp(chain_name, "in") || !strcmp(chain_name, "input"))
		chn = 1;
	else if (!strcmp(chain_name, "out")|| !strcmp(chain_name, "output"))
		chn = 2;
	else if (!strcmp(chain_name, "forward"))
		chn = 0;
	else {
		PyErr_SetString(PyExc_OSError, "only in, forward and" \
				" out are valid direction names");
		return NULL;
	}

	procfile = procfiles[chn];
	if ((fp = fopen(procfile, "r")) == NULL) {
		PyErr_SetString(PyExc_OSError, "ipfwadm not supported, or" \
				" /proc filesystem not mounted");
		return NULL;
	}

	fw = (struct ip_fw *) malloc(sizeof(struct ip_fw));
	/* Eat first line */
	fscanf(fp, "%[^,], default %d", buf, &policy);

	while (1) {
		int kind = 0;
		char xml[10240];
		char strnfix[1024];
		char strnfix2[1024];
		char tmp[1024];

		n = read_procinfo(fp, fw);
		if (n != 11)
			break;

		xml[0] = '\0';
		strnfix[0] = '\0';
		strnfix2[0] = '\0';
		tmp[0] = '\0';
		strcat(xml, XML_HEADER);

		if (!nat) {
			switch (chn) {
				case 1:
					addval(xml, "direction", "in");
					break;
				case 2:
					addval(xml, "direction", "out");
					break;
				case 0:
					addval(xml, "direction", "forward");
					break;
			}
		}

		strncat(strnfix, addr_to_dotted(&(fw->fw_src)), 15);
		strncat(strnfix, "/", 1);
		strncat(strnfix, addr_to_dotted(&(fw->fw_smsk)), 15);
		if (strcmp(strnfix, "0.0.0.0/0.0.0.0"))
			addval(xml, "source-ip", strnfix);

		strnfix[0] = '\0';
		strncat(strnfix, addr_to_dotted(&(fw->fw_dst)), 15);
		strncat(strnfix, "/", 1);
		strncat(strnfix, addr_to_dotted(&(fw->fw_dmsk)), 15);
		if (strcmp(strnfix, "0.0.0.0/0.0.0.0"))
			addval(xml, "destination-ip", strnfix);

		strnfix[0] = '\0';
		strncat(strnfix, fw->fw_vianame, IFNAMSIZ);
		if (strlen(strnfix) > 0)
			addval(xml, "interface", fw->fw_vianame);

		strncat(xml, ">\n", 2);

		kind = (fw->fw_flg) & IP_FW_F_KIND;
		switch (kind) {
			case IP_FW_F_TCP:
				addval(tmp, "protocol", "6");
				break;
			case IP_FW_F_UDP:
				addval(tmp, "protocol", "17");
				break;
			case IP_FW_F_ICMP:
				addval(tmp, "protocol", "1");
				break;
		}
		strnfix[0] = '\0';
		if (fw->fw_nsp) {
			sprintf(strnfix, "%i", fw->fw_pts[0]);
			if (fw->fw_flg & IP_FW_F_SRNG) {
				strcat(strnfix, ":");
				strnfix2[0] = '\0';
				sprintf(strnfix2, "%i", fw->fw_pts[1]);
				strcat(strnfix, strnfix2);
			}
			if (kind == IP_FW_F_TCP ||
					kind == IP_FW_F_UDP) {
				if (strcmp(strnfix, "1:65535") &&
						strcmp(strnfix, "0:65535"))
				addval(tmp, "source-port", strnfix);
			}
			else if (kind == IP_FW_F_ICMP)
				addval(tmp, "icmp-type", strnfix);
		}

		if (fw->fw_flg & IP_FW_F_TCPSYN)
			addval(tmp, "syn-only", "yes");
		else if (fw->fw_flg & IP_FW_F_TCPACK)
			addval(tmp, "syn-only", "no");

		strnfix[0] = '\0';
		if (fw->fw_ndp) {
			sprintf(strnfix, "%i", fw->fw_pts[fw->fw_nsp]);
			if (fw->fw_flg & IP_FW_F_DRNG) {
				strcat(strnfix, ":");
				strnfix2[0] = '\0';
				sprintf(strnfix2, "%i", \
						fw->fw_pts[fw->fw_nsp+1]);
				strcat(strnfix, strnfix2);
			}
			if (strcmp(strnfix, "1:65535") &&
					strcmp(strnfix, "0:65535"))
				addval(tmp, "destination-port", strnfix);
		}

		strnfix[0] = '\0';
		if (strlen(tmp) > 0) {
			strcat(xml, "    <protocol ");
			strcat(xml, tmp);
			strcat(xml, "/>\n");
		}

		if (!nat) {
			if (fw->fw_flg & IP_FW_F_MASQ ||
					fw->fw_flg & IP_FW_F_REDIR)
				continue;
			strcat(xml, "    <target ");
			if (fw->fw_flg & IP_FW_F_ACCEPT)
				addval(xml, "target", "accept");
			else if (fw->fw_flg & IP_FW_F_ICMPRPL)
				addval(xml, "target", "reject");
			else
				addval(xml, "target", "drop");
			strcat(xml, "/>\n");
		} else {
			strcat(xml, "    <nat ");
			if (fw->fw_flg & IP_FW_F_MASQ)
				addval(xml, "nat", "masq");
			else if (fw->fw_flg & IP_FW_F_REDIR) {
				addval(xml, "nat", "redirect");
				strnfix[0] = '\0';
				sprintf(strnfix, "%i", \
					fw->fw_pts[fw->fw_nsp+fw->fw_ndp]);
				addval(xml, "to-port", strnfix);
			} else
				continue;
			strcat(xml, "/>\n");
		}

		if (fw->fw_flg & IP_FW_F_PRN)
			strcat(xml, "    <log />\n");

		strcat(xml, "  </rule>\n</append>\n");

		PyList_Append(result, PyString_FromString(xml));
	}
	fclose(fp);
	return Py_BuildValue("O", result);
}


/* Exported functions. */
static PyMethodDef _IpfwadmMethods[] = {
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
	(void) Py_InitModule(MODNAMESTR, _IpfwadmMethods);
}



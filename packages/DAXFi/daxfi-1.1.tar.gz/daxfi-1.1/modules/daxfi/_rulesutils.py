"""
_rulesutils module (daxfi package).

This module provide utilities for both the RuleBuilder and Rule classes.

  Copyright 2001, 2002 Davide Alberani <alberanid@libero.it>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import socket

from daxfi._exceptions import *
from daxfi._syslog import *
from daxfi import iplib


# --- Strings that are XML tags

# - Valid XML tags.

# Names of the firewall actions as used in the XML.
xml_actions = ('append', 'delete', 'replace', 'insert', 'flush')

# Supported protocols.
xml_protocols = ('tcp', 'udp', 'icmp')

# Known targets.
xml_targets = ('accept', 'reject', 'drop')

# NAT types.
xml_nat = ('snat', 'dnat', 'masq', 'redirect')

# Misc tags.
xml_extensions = ('log', 'limit')

# The current DTD.
DTD_NAME = 'daxfifw_0.5.dtd'


# --- Flags for converter/first_tranformation/section_transformation dicts

# A simple flag.
# The value is never considered; only the option string is returned.
FLAG = 0x01

# The option followed by the value are returned.
VALUE = 0x02

# Call a function and use the returned string.
CALL = 0x04

# The corresponding option is returned if the value is 'true',
# the negation of the option is returned for 'false'.
BOOLEAN = 0x08

# Remove the attribute or section.
# A warning is issued only for sections; an attribute is
# silently discarded.
REMOVE = 0x10

# If this section or attribute is present, a rule for this firewall
# can't be build.
FATAL = 0x20


# --- Functions used by both Rule and RuleBuilder objects

def modifyRuleData(rd, convAttributes={}, convSections={},
                        forEveryAttribute=None):
    """Modify the given RuleData object.  The object is modified in place."""
    # Run forEveryAttribute() for every attribute.
    if callable(forEveryAttribute):
        for node in rd.listNodes():
            for attribute in rd.list(node):
                value = forEveryAttribute(rd.get(node, attribute))
                rd.set(node, attribute, value)
    # For every node.
    for node in rd.intersection(convSections):
        flag = convSections[node]
        if flag & REMOVE:
            sl_print_warning('the "' + node + '" section' +
                                ' will be ignored for this firewall')
            rd.popNode(node)
        elif flag & FATAL:
            sl_print_error('cannot build a rule with the "' +
                                node + '" section')
            rd.reset()
            return rd
        else:
            sl_print_warning('flag "' + hex(flag) + '" is not allowed for' +
                                ' sections')
    # For every attribute.
    for node, attribute in [(x, y) for x in rd.intersection(convAttributes)
                                for y in rd.intersection(convAttributes, x)]:
        value = rd.get(node, attribute)
        cont, flag = convAttributes[node][attribute]
        if flag & FLAG:
            rd.set(node, attribute, cont)
        elif flag & VALUE:
            if cont: cont += ' '
            rd.set(node, attribute, cont + value)
        elif flag & BOOLEAN:
            if value== 'yes':
                rd.set(node, attribute, cont)
            elif value == 'no':
                rd.set(node, attribute, '! ' + cont)
            else:
                sl_print_error('"' + attribute + '" must be a boolean' +
                                ' value (yes|no)')
        elif flag & CALL:
            try:
                neg = ''
                if len(value) > 1 and value[0:2] == '! ':
                    neg = '! '
                    value = value[2:]
                value = cont(value)
                if neg: value = '! ' + value
                rd.set(node, attribute, value)
            except RemoveOptionError:
                rd.pop(node, attribute)
            except RemoveSectionError, e:
                sl_print_warning('the "' + node + '" section' +
                                    ' will be ignored for this firewall (' +
                                    str(e) + ')')
                rd.popNode(node)
            except CreateRulesError, e:
                sl_print_error('cannot build a rule with the "' +
                                node + '" section or the "' + attribute +
                                '" attribute (' + str(e) + ')')
                rd.reset()
                return rd
            except Exception, e:
                sl_print_error('exception raised running a transf_*()' +
                                ' function; the "' + node + '" option will' +
                                ' be remove (' + str(e) + ')')
                rd.pop(node, attribute)
        elif flag & REMOVE:
            rd.pop(node, attribute)
        elif flag & FATAL:
            sl_print_error('cannot build a rule with the "' +
                                attribute + '" attribute')
            rd.reset()
            return rd
    return rd


# --- Functions used to transform rule's attributes.

icmp_map = {
    'echo-reply':   (0,),
    'pong':         (0,),
    'destination-unreachable':      (3,),
    'network-unreachable':          (3, 0),
    'host-unreachable':             (3, 1),
    'protocol-unreachable':         (3, 2),
    'port-unreachable':             (3, 3),
    'fragmentation-needed':         (3, 4),
    'source-route-failed':          (3, 5),
    'network-unknown':              (3, 6),
    'host-unknown':                 (3, 7),
    'network-isolated':             (3, 8),
    'network-prohibited':           (3, 9),
    'host-prohibited':              (3, 10),
    'TOS-network-unreachable':      (3, 11),
    'TOS-host-unreachable':         (3, 12),
    'communication-prohibited':     (3, 13),
    'host-precedence-violation':    (3, 14),
    'precedence-cutoff':            (3, 15),
    'source-quench':    (4,),
    'redirect':             (5,),
    'network-redirect':     (5, 0),
    'host-redirect':        (5, 1),
    'TOS-network-redirect': (5, 2),
    'TOS-host-redirect':    (5, 3),
    'echo-request': (8,),
    'pong':         (8,),
    'router-advertisement': (9,),
    'router-solicitation':  (10,),
    'time-exceeded':                (11,),
    'ttl-exceeded':                 (11,),
    'ttl-zero-during-transit':      (11, 0),
    'ttl-zero-during-reassembly':   (11, 1),
    'parameter-problem':        (12,),
    'ip-header-bad':            (12, 0),
    'required-option-missing':  (12, 1),
    'timestamp-request':    (13,),
    'timestamp-reply':      (14,),
    'information-request':  (15,),
    'information-reply':    (16,),
    'address-mask-request': (17,),
    'address-mask-reply':   (18,)
}

def transf_icmp(v):
    """Return a numeric representation of icmp type/code."""
    x = icmp_map.get(v)
    if x:
        v = str(x[0])
        if len(x) == 2: 
            v += '/' + str(x[1])
    return v

def transf_sort(v):
    """For options that need to be sorted.

    Given a string with comma separated items, these items are sorted;
    if portions of the string are sparated by slashes, the order of these
    groups is preserved.
    """
    r = []
    o = ''
    for s in v.split('/'):
        x = s.split(',')
        x.sort()
        r.append(x)
    for s in r:
        o2 = ''
        for t in s:
            if o2: o2 += ','
            o2 += t
        o += o2 + '/'
    return o[:-1]

def transf_ip(v):
    """Manage IP address.

    Return an IP in dotted notation with the right netmask.
    """
    host = v
    mask = '255.255.255.255'
    if v.find('/') != -1:
        host, mask = v.split('/')
    if host == '0':
        host = '0.0.0.0'
    # We have a host name.
    if not host.replace('.', '').isdigit():
        try:
            host = socket.gethostbyname(host)
        except socket.error:
            pass
    # Normalize host and mask.
    try:
        host = iplib.convert(host, notation=iplib.IP_DOT)
    except ValueError:
        pass
    try:
        mask = iplib.convert_nm(mask, notation=iplib.NM_DOT)
    except ValueError:
        pass
    if mask == '0.0.0.0':
        host = '0.0.0.0'
    if host == '0.0.0.0':
        mask = '0.0.0.0'
    hp = host.split('.')
    mp = mask.split('.')
    if len(hp) == len(mp) == 4:
        i = 0 
        while i < 4:
            if mp[i] == '0':
                hp[i] = '0'
            i = i + 1
        host = hp[0] + '.' + hp[1] + '.' + hp[2] + '.' + hp[3]
    v = host + '/' + mask
    return v

def transf_ip_nomask(v):
    """Return an IP without the netmask."""
    return transf_ip(v).split('/')[0]

def transf_ip_remove_default(v):
    """Remove the default value for IP addresses."""
    if v == '0.0.0.0/0.0.0.0':
        raise RemoveOptionError, 'remove the default value'
    return v

def transf_proto(v):
    """Return the protocol number.

    Given a protocol name, return the protocol number.
    """
    try:
        v = str(socket.getprotobyname(v))
    except socket.error:
        pass
    return v

def transf_port(v):
    """Return the port number.

    Given a port name, return the protocol number.
    """
    plist = v.split(':')
    index = 0
    for i in plist:
        try:
            i = str(socket.getservbyname(i, 'tcp'))
        except socket.error:
            try:
                i = str(socket.getservbyname(i, 'udp'))
            except socket.error:
                pass
        plist[index] = i
        index += 1
    return ':'.join(plist)

def transf_port_remove_default(v):
    """Remove the default value for port numbers."""
    if v == '1:65535':
        raise RemoveOptionError, 'remove the default value'
    return v

def transf_normalize(v):
    """Check for a space after an exclamation mark and strip white spaces."""
    v = v.strip()
    if len(v) > 0 and v[0] == '!':
        return '! ' + v[1:].strip()
    return v

def transf_remove(v):
    """Simply remove an entry."""
    raise RemoveOptionError, 'remove this option'

def transf_fatal(v):
    """Raise an exception because a rule with this option/extension
    cannot be built with the currently used firewall."""
    raise CreateRulesError, 'Cannot insert a key in a rule for ' + \
                            'this firewall'

def transf_remove_section(v):
    """Raise an exception that force the modify_option function to
    completely discard the current section."""
    raise RemoveSectionError, 'cannot use this extension with this firewall'


# - Function used to flatten user-defined chains.

def mergeRuleWithUDC(rule, chains):
    """Merge a rule, with a user-defined target, with the
    referred chain (and recurse in sub-chains)."""
    target_chain = chains.get(rule.getTarget())
    if target_chain is None:
        return [rule]
    result = []
    for r in target_chain:
        if r.getTarget() not in chains.keys():
            result.append(rule ^ r)
        else:
            for i in mergeRuleWithUDC(r, chains):
                result.append(rule ^ i)
    return result



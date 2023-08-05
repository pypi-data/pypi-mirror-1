"""
iptables package (daxfi.firewalls package).

Class used to manage iptables rules.

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

from daxfi.Rule import *

module = import_C_module('iptables')


def list_rules(direction):
    if direction == 'nat':
        return module.list_rules('POSTROUTING', 1) + \
                module.list_rules('PREROUTING', 1) + \
                module.list_rules('OUTPUT', 1)
    return module.list_rules(direction)

def list_chains():
    return module.list_chains()

def is_supported():
    return module.is_supported()

def get_policy(direction):
    return module.get_policy(direction)


def transf_iptables_chain(v):
    if v == 'in': return 'INPUT'
    if v == 'out': return 'OUTPUT'
    if v == 'forward': return 'FORWARD'
    return v

def transf_iptables_target(v):
    if v in ('drop', 'reject', 'accept'):
        return '-j ' + v.upper()
    return '-j ' + v

def transf_iptables_rate(v):
    """Transform the rate of the iptables' limit extension."""
    ret = v
    index = v.find('/')
    if index != -1:
        try:
            val = int(v[:index])
        except ValueError:
            raise RemoveOptionError, 'removing absurd rate value.'
        if val <= 0:
            raise RemoveOptionError, 'removing absurd rate value.'
        unit = v[index+1:]
        mul = 1
        if unit == 's' or unit == 'second':
            mul = 1
        elif unit == 'm' or unit == 'minute':
            mul = 60
        elif unit == 'h' or unit == 'hour':
            mul = 60*60
        elif unit == 'd' or unit == 'day':
            mul = 24*60*60
        ret = str(mul * val)
    else:
        try:
            val = int(v)
            ret = str(val / 10000)
        except ValueError:
            raise RemoveOptionError, 'removing absurd rate value.'
    try:
        r = int(ret)
        for mul, unit in ((60*60*24, 'd'), (60*60, 'h'),
                            (60, 'm'), (1, 's')):
            di = r / mul
            if di != 0:
                ret = str(di) + '/' + unit
                break
    except ValueError:
        raise RemoveOptionError, 'removing absurd rate value.'
    return '--limit ' + ret

def transf_iptables_state(v):
    if v == 'new':
        return '--state INVALID,NEW'
    elif v == 'related':
        return '--state ESTABLISHED,RELATED'
    return v

def transf_iptables_tcpflags(v):
    """Invert value/mask for iptables' tcp-flags."""
    v = v.upper()
    if v.find('/') == -1:
        v += '/SYN,ACK,FIN,RST,URG,PUSH'
    l = v.split('/')
    comp = l[0].split(',')
    mask = l[1].split(',')
    comp.sort()
    mask.sort()
    for i in comp + mask:
        if i not in 'SYN,ACK,FIN,RST,URG,PUSH'.split(','):
            raise CreateRulesError, 'invalid flag: "' + i + '"'
    try:
        comp[comp.index('PUSH')] = 'PSH'
    except ValueError:
        pass
    try:
        mask[mask.index('PUSH')] = 'PSH'
    except ValueError:
        pass
    return '--tcp-flags ' + ','.join(mask) + ' ' + ','.join(comp)

def transf_iptables_rejectwith(v):
    if v == '3/0':
        return '--reject-with icmp-net-unreachable'
    if v == '3/1':
        return '--reject-with icmp-host-unreachable'
    if v == '3/2':
        return '--reject-with icmp-proto-unreachable'
    if v == '3/3':
        return '--reject-with icmp-port-unreachable'
    if v == '3/9':
        return '--reject-with icmp-net-prohibited'
    if v == '3/10':
        return '--reject-with icmp-host-prohibited'
    return '--reject-with ' + v

def transf_iptables_nattype(v):
    if v == 'redirect':
        return '-j REDIRECT'
    if v == 'masq':
        return '-j MASQUERADE'
    if v == 'snat':
        return '-j SNAT'
    if v == 'dnat':
        return '-j DNAT'
    return v


# - Sets of options for the iptables/netfilter firewall

fw_commands = {
    'append':       '-A',
    'delete':       '-D',
    'replace':      '-R',
    'insert':       '-I',
    'flush':        '-F'
}

fw_rules_iptables = {
    'source-ip':        ('--source', VALUE),
    'destination-ip':   ('--destination', VALUE),
    'interface':        ('--in-interface', VALUE),
    'fragment-only':    ('--fragment', BOOLEAN),
    'direction':        (transf_iptables_chain, CALL)
}

fw_targets_iptables = {
    'target':       (transf_iptables_target, CALL),
    'reject-with':  (transf_iptables_rejectwith, CALL)
}

fw_protocols_iptables = {
    'protocol':         ('-p', VALUE),
    'source-port':      ('--source-port', VALUE),
    'destination-port': ('--destination-port', VALUE),
    'tcp-flags':        (transf_iptables_tcpflags, CALL),
    'icmp-type':        ('--icmp-type', VALUE),
    'syn-only':         ('--syn', BOOLEAN),
    'state':            (transf_iptables_state, CALL)
}

fw_log_iptables = {
    'priority':         ('--log-level', VALUE),
    'facility':         ('', REMOVE)
}

fw_limits_iptables = {
    'rate':      (transf_iptables_rate, CALL),
    'burst':     ('--limit-burst', VALUE)
}

fw_nat_iptables = {
    'nat':          (transf_iptables_nattype, CALL),
    'to-address':   ('', VALUE),
    'to-port':      ('', VALUE)
}

# The converter dictionary for iptables.
fw_iptables_converter = {
    'rule':         fw_rules_iptables,
    'target':       fw_targets_iptables, 
    'protocol':     fw_protocols_iptables,
    'log':          fw_log_iptables,
    'limit':        fw_limits_iptables,
    'nat':          fw_nat_iptables
}


class Rule(RuleBase):
    """Methods and variables used to create the command string for iptables."""
    converter = fw_iptables_converter
    first_transformation = {}
    section_transformation = {}
    withLog = 0

    def _getRuleCommand(self):
        """Return a string used to run the command for this rule."""
        cmd = 'iptables'

        rd = self.getModifiedRuleData()
        action = self.getAction()
        exe = fw_commands[action]
        cmd = cmd + ' ' + exe
        has_target = rd.hasNode('target')
        direction = rd.pop('rule', 'direction')
        has_proto = rd.hasNode('protocol')

        nat = rd.hasNode('nat')
        nat_type, to_port, to_address = rd.pop('nat', ('nat', 'to-port',
                                                        'to-address'))
        to_port = to_port.replace(':', '-')
        to_address = to_address.replace(':', '-')

        if nat_type == '-j REDIRECT':
            direction = 'OUTPUT'
        elif nat_type == '-j MASQUERADE':
            direction = 'POSTROUTING'
        elif nat_type == '-j DNAT':
            direction = 'OUTPUT'
        elif nat_type == '-j SNAT':
            direction = 'POSTROUTING'

        if direction:
            cmd = cmd + ' ' + direction

        rn = self.getRuleNumber()
        if rn and (action in ('replace', 'insert', 'delete')):
            cmd = cmd + ' ' + rn
        if has_proto:
            p = rd.pop('protocol', 'protocol')
            if p:
                cmd = cmd + ' ' + p
        elif to_port:
            cmd = cmd + ' -p 6'
        
        if nat:
            cmd = cmd + ' -t nat ' + nat_type
        if nat_type == '-j REDIRECT' or nat_type == '-j MASQUERADE':
            if to_port:
                cmd = cmd + ' --to-ports ' + to_port
        elif nat_type == '-j DNAT':
            if to_address:
                cmd = cmd + ' --to-destination ' + to_address
                if to_port:
                    cmd = cmd + ':' + to_port
        elif nat_type == '-j SNAT':
            if to_address:
                cmd = cmd + ' --to-source ' + to_address
            if to_port:
                cmd = cmd + ':' + to_port
        if direction in ('OUTPUT', 'POSTROUTING'):
            i = rd.pop('rule', 'interface')
            if i:
                rd.set('rule', 'interface', '--out-interface ' + i.split()[1])

        if rd.has('protocol', 'state'):
            cmd = cmd + ' -m state'

        has_limit = rd.hasNode('limit')
        if has_limit:
            cmd = cmd + ' -m limit'
            rate = rd.pop('limit', 'rate')
            if rate:
                cmd = cmd + ' ' + rate
        has_log = rd.hasNode('log')
        if has_log:
            cmd = cmd + ' -j LOG'
            if has_target:
                rd.pop('target', 'target')
        if has_target:
            tg = rd.pop('target', 'target')
            cmd = cmd + ' ' + tg

        return cmd + ' ' + rd.getDataFlat()



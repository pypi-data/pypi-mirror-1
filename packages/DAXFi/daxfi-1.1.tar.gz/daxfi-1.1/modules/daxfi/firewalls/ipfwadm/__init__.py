"""
ipfwadm package (daxfi.firewalls package).

Class used to manage ipfwadm rules.

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

module = import_C_module('ipfwadm')


def is_supported():
    return module.is_supported()

def list_rules(direction):
    if direction == 'nat':
        return module.list_rules('forward', 1) + module.list_rules('in', 1)
    return module.list_rules(direction)

def list_chains():
    return module.list_chains()

def get_policy(direction):
    return module.get_policy(direction)


def transf_ipfwadm_proto(v):
    """Ipfwadm wants a protocol name, instead of a protocol number."""
    if v == '0' or v == 'all':
        return '-P all'
    elif v == '1' or v == 'icmp':
        return '-P icmp'
    elif v == '6' or v == 'tcp':
        return '-P tcp'
    elif v == '17' or v == 'udp':
        return '-P udp'
    return '-P ' + v

def trasf_ipfwadm_icmptype(v):
    """Ipfwadm need an icmp type expressed in numeric format."""
    i = v.find('/')
    if i != -1:
        v = v[:i]
    return v

def transf_ipfwadm_target(v):
    if v == 'drop':
        return 'deny'
    return v

def trasf_ipfwadm_nat(v):
    if v == 'snat':
        return 'masq'
    if v == 'dnat':
        return 'redirect'
    return v


# Sections to be modified for ipfwadm.
fw_section_transform_ipfwadm = {
    'limit':            REMOVE
}

# - Sets of options for the ipfwadm firewall

fw_commands = {
    'append':           '-a',
    'delete':           '-d',
    'insert':           '-i',
    'flush':            '-f'
}

fw_rules_ipfwadm = {
    'source-ip':        ('-S', VALUE),
    'destination-ip':   ('-D', VALUE),
    'interface':        ('-W', VALUE),
    'direction':        ('', VALUE),
    'fragment-only':    ('', FATAL)
}

fw_target_ipfwadm = {
    'target':           (transf_ipfwadm_target, CALL),
    'reject-with':      ('', REMOVE)
}

fw_protocols_ipfwadm = {
    'protocol':         (transf_ipfwadm_proto, CALL),
    'source-port':      ('', VALUE),
    'destination-port': ('', VALUE),
    'icmp-type':        (trasf_ipfwadm_icmptype, CALL),
    'tcp-flags':        ('', FATAL),
    'syn-only':         ('-y', BOOLEAN),
    'state':            ('', FATAL)
}

fw_log_ipfwadm = {
    'priority':         ('', REMOVE),
    'facility':         ('', REMOVE)
}

fw_nat_ipfwadm = {
    'nat':          (trasf_ipfwadm_nat, CALL),
    'to-address':   ('', FATAL),
    'to-port':      ('-r', VALUE)
}

# The converter dictionary for ipfwadm.
fw_ipfwadm_converter = {
    'rule':         fw_rules_ipfwadm,
    'protocol':     fw_protocols_ipfwadm,
    'target':       fw_target_ipfwadm,
    'log':          fw_log_ipfwadm,
    'nat':          fw_nat_ipfwadm
}


class Rule(RuleBase):
    """Methods and variables used to create the command string for ipfwadm."""
    converter = fw_ipfwadm_converter
    first_transformation = {}
    section_transformation = fw_section_transform_ipfwadm
    defaults = {}
    withLog = 1

    def _getRuleCommand(self):
        """Return a string used to run the command for this rule."""
        cmd = 'ipfwadm'

        action = self.getAction()

        exe = fw_commands.get(action)
        if exe is None:
            sl_print_error('unsupported action for ipfwadm: ' + action)
            return ''
        cmd = cmd + ' ' + exe
        rd = self.getModifiedRuleData()

        rn = self.getRuleNumber()
        if action == 'delete' and rn:
            sl_print_error('cannot delete a rule via rule-number')
            return ''

        if action == 'insert' and rn:
            sl_print_warning('cannot insert a rule in a arbitrary ' + \
                                'position, inserting it at the top')

        has_nat = rd.hasNode('nat')
        nat_type, to_port = rd.pop('nat', ('nat', 'to-port'))

        has_target = rd.hasNode('target')
        if has_target and not has_nat:
            target = rd.pop('target', 'target')
            cmd = cmd + ' ' + target

        if nat_type == 'redirect':
            cmd = cmd + ' accept -I'
        elif nat_type == 'masq':
            cmd = cmd + ' masquerade -F'
        if to_port:
            cmd = cmd + ' ' + to_port

        chn = rd.pop('rule', 'direction')
        if chn and not has_nat:
            if chn == 'in':
                cmd = cmd + ' -I'
            elif chn == 'out':
                cmd = cmd + ' -O'

        if action == 'flush' and chn == 'nat':
            sl_print_error('cannot flush NAT tables for ipfwadm; instead ' + \
                            'flush in, forward and out directions separately')
            return ''

        has_proto = rd.hasNode('protocol')
        if has_proto:
            pt = rd.get('protocol', 'protocol')
            if pt == '-P all':
               rd.pop('protocol', 'protocol')

            sp = rd.pop('protocol', 'source-port')
            if not sp:
                sp = rd.pop('protocol', 'icmp-type')
            sa = rd.pop('rule', 'source-ip')
            if sp and not sa: sa = '-S 0.0.0.0/0.0.0.0'
            if sa:
                cmd = cmd + ' ' + sa + ' ' + sp

            dp = rd.pop('protocol', 'destination-port')
            if dp:
                da = rd.pop('rule', 'destination-ip')
                if not da: da = '-D 0.0.0.0/0.0.0.0'
                cmd = cmd + ' ' + da + ' ' + dp
            syn = rd.get('protocol', 'syn-only')
            if syn == '! -y':
                cmd = cmd + ' -k'
                rd.pop('protocol', 'syn-only')

        has_log = rd.popNode('log')
        if has_log != None:
            cmd = cmd + ' -o'
        cmd = cmd + ' ' + rd.getDataFlat()
        if cmd.find('!') != -1:
            sl_print_error('ipfwadm does not support parameter negation')
            return ''
        return cmd



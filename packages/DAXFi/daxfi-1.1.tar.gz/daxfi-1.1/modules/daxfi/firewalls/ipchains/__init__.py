"""
ipchains package (daxfi.firewalls package).

Class used to manage ipchains rules.

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

module = import_C_module('ipchains')


def is_supported():
    return module.is_supported()

def list_rules(direction):
    if direction == 'nat':
        return module.list_rules('in', 1) + module.list_rules('forward', 1)
    return module.list_rules(direction)

def list_chains():
    return module.list_chains()

def get_policy(direction):
    return module.get_policy(direction)


def transf_ipchains_target(v):
    if v == 'drop':
        return '-j DENY'
    elif v == 'reject':
        return '-j REJECT'
    elif v == 'accept':
        return '-j ACCEPT'
    return '-j ' + v

def trasf_ipchains_nat(v):
    if v == 'snat':
        return 'masq'
    if v == 'dnat':
        return 'redirect'
    return v

def transf_ipchains_direction(v):
    if v == 'in': return 'input'
    if v == 'out': return 'output'
    return v


# Sections to be modified for ipchains.
fw_section_transform_ipchains = {
    'limit':            REMOVE
}

# - Sets of options for the ipchains firewall

fw_commands = {
    'append':           '-A',
    'delete':           '-D',
    'replace':          '-R',
    'insert':           '-I',
    'flush':            '-F'
}

fw_rules_ipchains = {
    'direction':        (transf_ipchains_direction, CALL),
    'source-ip':        ('--source', VALUE),
    'destination-ip':   ('--destination', VALUE),
    'interface':        ('--interface', VALUE),
    'fragment-only':    ('--fragment', BOOLEAN)
}

fw_targets_ipchains = {
    'target':       (transf_ipchains_target, CALL),
    'reject-with':  ('', REMOVE)
}

fw_protocols_ipchains = {
    'protocol':         ('-p', VALUE),
    'source-port':      ('--source-port', VALUE),
    'destination-port': ('--destination-port', VALUE),
    'icmp-type':        ('', VALUE),
    'syn-only':         ('--syn', BOOLEAN),
    'tcp-flags':        ('', FATAL),
    'state':            ('', FATAL)
}

fw_log_ipchains = {
    'priority':         ('', REMOVE),
    'facility':         ('', REMOVE)
}

fw_nat_ipchains = {
    'nat':          (trasf_ipchains_nat, CALL),
    'to-address':   ('', FATAL),
    'to-port':      ('', VALUE)
}

# The converter dictionary for ipchains.
fw_ipchains_converter = {
    'rule':         fw_rules_ipchains,
    'target':       fw_targets_ipchains,
    'protocol':     fw_protocols_ipchains,
    'nat':          fw_nat_ipchains
}


class Rule(RuleBase):
    """Methods and variables used to create the command string for ipchains."""
    converter = fw_ipchains_converter
    first_transformation = {}
    section_transformation = fw_section_transform_ipchains
    defaults = {}
    withLog = 1
    commands = fw_commands

    def _getRuleCommand(self):
        """Return a string used to run the command for this rule."""
        cmd = 'ipchains'

        rd = self.getModifiedRuleData()

        action = self.getAction()
        exe = fw_commands[action]

        cmd = cmd + ' ' + exe

        has_nat = rd.hasNode('nat')
        nat_type, to_port = rd.pop('nat', ('nat', 'to-port'))

        has_target = rd.hasNode('target')
        target = ''
        if has_target and not has_nat:
            target = rd.pop('target', 'target')
        direction = rd.pop('rule', 'direction')
        if action == 'flush':
            if direction == 'nat': direction = ''
            return cmd + ' ' + direction

        if nat_type == 'redirect':
            cmd = cmd + ' input -j REDIRECT'
            if to_port:
                cmd = cmd + ' ' + to_port
        elif nat_type == 'masq':
            cmd = cmd + ' forward -j MASQ'
        if direction:
            cmd = cmd + ' ' + direction
        if self.getRuleNumber() and \
            (self.getAction() == 'replace' or
                self.getAction() == 'insert' or self.getAction() == 'delete'):
            cmd = cmd + ' ' + self.getRuleNumber()
        if has_target:
            cmd = cmd + ' ' + target

        has_proto = rd.hasNode('protocol')
        itype = ''
        if has_proto:
            itype = rd.pop('protocol', 'icmp-type')
        if itype:
            if itype.find('/') == -1:
                cmd = cmd + ' --icmp-type ' + itype
            else:
                sp = rd.pop('protocol', 'source-port')
                dp = rd.pop('protocol', 'destination-port')
                if not sp: sp = '--source 0.0.0.0/0.0.0.0'
                if not dp: dp = '--destination 0.0.0.0/0.0.0.0'
                tc = itype.split('/')
                cmd = cmd + ' ' + sp + ' ' + tc[0] + \
                            ' ' + dp + ' ' + tc[1]
        has_log = rd.hasNode('log')
        if has_log:
            cmd = cmd + ' -l'
            rd.popNode('log')
        return cmd + ' ' + rd.getDataFlat()



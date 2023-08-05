"""
ipfilter package (daxfi.firewalls package).

Class used to manage ipfilter rules.

  Copyright 2002 Davide Alberani <alberanid@libero.it>

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

module = import_C_module('ipfilter')


def is_supported():
    return module.is_supported()

def list_rules(direction):
    if direction == 'nat':
        try:
            return module.list_nat()
        except NameError:
            return []
    return module.list_rules(direction)

def list_chains():
    return module.list_chains()

def get_policy(direction):
    return module.get_policy(direction)


def transf_ipfilter_target(v):
    """Modify the target name."""
    i = v.lower()
    if i == 'drop':
        return 'block'
    if i == 'reject':
        return 'block return-icmp'
    if i == 'accept':
        return 'pass'
    return v

def transf_ipfilter_port(v):
    """Ipfilter use its own range syntax."""
    # XXX: quite messy!
    v = transf_port(v)
    if v.find(':') != -1:
        plist = v.split(':')
        a = plist[0]
        b = plist[1]
        return a + ' >< ' + b
    else:
        return '= ' + v

def transf_ipfilter_icmp(v):
    """Convert icmp names into icmp codes."""
    code = v.split('/')
    res = 'icmp-type ' + str(code[0])
    if len(code) > 1:
        res = res + ' code ' + str(code[1])
    return res

def transf_ipfilter_state(v):
    """Manage states for ipfilter."""
    if v == 'related':
        return 'keep state'
    raise CreateRulesError, 'unable to write a rule with this state'

def transf_ipfilter_syn(v):
    """ACK and SYN matches must be 'emulated' with 'flags'."""
    if v == 'yes':
        return 'flags S/SRA'
    elif v == 'no':
        return 'flags SA'
    return ''

def transf_ipfilter_logprio(v):
    """ipfilter uses the BSD names for logging priority."""
    if v == 'warning':
        v = 'warn'
    return v

def transf_ipfilter_tcpflags(v):
    """ipfilter uses it's own syntax for tcp flags."""
    out = ''
    if v.find(' ') != -1:
        vs = v.split(' ')
        v = vs[1] + '/' + vs[0]
    v = v.split('/')
    for e in v:
        x = e.split(',')
        for i in x:
            out = out + i[0]
        out = out + '/'
    return 'flags ' + out[:-1]


fw_section_transform_ipfilter = {
    'limit':            REMOVE
}

# - Sets of options for the ipfilter firewall

fw_commands = {
    'append':           '',
    'delete':           '',
    'insert':           '',
    'flush':            ''
}

fw_rules_ipfilter = {
    'source-ip':        ('from', VALUE),
    'destination-ip':   ('to', VALUE),
    'interface':        ('on', VALUE),
    'fragment-only':    ('with frag', BOOLEAN),
}

fw_targets_ipfilter = {
    'target':       (transf_ipfilter_target, CALL),
    'reject-with':  ('', VALUE)
}

fw_protocols_ipfilter = {
    'protocol':         ('proto', VALUE),
    'source-port':      (transf_ipfilter_port, CALL),
    'destination-port': (transf_ipfilter_port, CALL),
    'icmp-type':        (transf_ipfilter_icmp, CALL),
    'tcp-flags':        (transf_ipfilter_tcpflags, CALL),
    'syn-only':         (transf_ipfilter_syn, CALL),
    'state':            (transf_ipfilter_state, CALL)
}

fw_log_ipfilter = {
    'priority':         (transf_ipfilter_logprio, CALL),
    'facility':         ('', VALUE)
}

fw_nat_ipfilter = {
    'nat':          ('', VALUE),
    'to-address':   (transf_ip, CALL),
    'to-port':      ('', VALUE)
}

fw_ipfilter_converter = {
    'rule':         fw_rules_ipfilter,
    'target':       fw_targets_ipfilter,
    'protocol':     fw_protocols_ipfilter,
    'log':          fw_log_ipfilter,
    'nat':          fw_nat_ipfilter
}


class Rule(RuleBase):
    """Methods and variables used to create the command string for ipfilter."""
    converter = fw_ipfilter_converter
    first_transformation = {}
    section_transformation = fw_section_transform_ipfilter
    defaults = {}
    firewallName = 'ipfilter'
    withLog = 1

    def __str__(self):
        """Print this rule."""
        cmd = self._buildRule()
        if not cmd: return ''
        if cmd[0] == '&':
            return '# Execute the command: ' + cmd[1:]
        elif cmd[0] == '%':
            return '# Remove the rule: "' + cmd[1:] + '"'
        elif cmd[0] == '^':
            return '# Remove the NAT rule: "' + cmd[1:] + '"'
        if cmd[0] == '!':
            return cmd[1:]
        else:
            return cmd

    def _getRuleCommand(self):
        """Return a string that is the command to run ipfilter rules."""
        cmd = self._buildRule()
        if not cmd:
            return ''
        if cmd[0] == '&':
            return cmd[1:]
        elif cmd[0] == '!':
            return 'echo "' + cmd[1:] + '" | ipnat -f -'
        elif cmd[0] == '%':
            return 'echo "' + cmd[1:] + '" | ipf -rf -'
        elif cmd[0] == '^':
            return 'echo "' + cmd[1:] + '" | ipnat -rf -'
        else:
            return 'echo "' + cmd + '" | ipf -f -'

    def _buildRule(self):
        """Internal function that builds the command string for
        this rule.  Commands to be executed directly are prepended
        with a &; other lines are commands from a configuration file
        for ipfilter."""
        cmd = ''

        action = self.getAction()
        exe = fw_commands.get(action)

        if exe is None:
            sl_print_error('cannot get the action for this rule')
            return ''

        rd = self.getModifiedRuleData()
        if not rd:
            return '' 

        direction = rd.pop('rule', 'direction')
        has_nat = rd.hasNode('nat')
        nat_type, to_port, to_address = rd.pop('nat', ('nat', 'to-port',
                                                'to-address'))
        if to_port == '0': to_port = ''

        if action == 'flush':
            if direction == 'nat': return '&ipnat -C'
            return '&ipf -F' + direction[0]

        if has_nat:
            if nat_type in ('redirect', 'dnat'):
                cmd = 'rdr'
            elif nat_type in ('masq', 'snat'):
                cmd = 'map'

        target = rd.hasNode('target')
        tg = ''
        if target and not has_nat:
            tg = rd.pop('target', 'target')
            rw = rd.pop('target', 'reject-with')
            if rw:
                tg = 'block return-icmp'
                spl = rw.split('/')
                rw = spl[0]
                rc = ''
                if len(spl) > 1:
                    rc = spl[1]
                if rw == '3' and rc:
                    rw = rc
                tg = tg + '(' + rw + ')'

        if action == 'insert':
            nr = self.getRuleNumber()
            if nr:
                cmd = '@' + nr + ' '
        if exe:
            cmd = cmd + ' ' + exe
        if tg:
            cmd = cmd + tg

        st = ''
        state = rd.has('protocol', 'state')
        if state:
            st = rd.pop('protocol', 'state')
        if direction:
            if state:
                if st == 'keep state':
                    if direction == 'in':
                        direction = 'out'
                    elif direction == 'out':
                        direction = 'in'
            if not has_nat:
                cmd = cmd + ' ' + direction

        has_log = rd.hasNode('log')
        if has_log:
            cmd = cmd + ' log'
            fac = rd.pop('log', 'facility')
            lev = rd.pop('log', 'priority')
            if fac:
                if not lev:
                    lev = 'warn'
                lev = fac + '.' + lev
            if lev:
                cmd = cmd + ' level ' + lev
            rd.popNode('log')

        # Always use the quick option.
        if not has_nat:
            cmd = cmd + ' quick'

        iface = rd.pop('rule', 'interface')
        if iface:
            if has_nat: iface = iface[3:]
            cmd = cmd + ' ' + iface

        has_proto = rd.hasNode('protocol')
        proto = None
        if has_proto:
            proto = rd.pop('protocol', 'protocol')
        if proto:
            if not has_nat: cmd = cmd + ' ' + proto

        sip = rd.pop('rule', 'source-ip')
        if not sip:
            sip = 'from 0.0.0.0/0.0.0.0'
        #if nat_type in ('redirect', 'dnat'): sip = sip[5:]
        cmd = cmd + ' ' + sip
        if has_proto:
            sp = rd.pop('protocol', 'source-port')
            if sp:
                if len(sp) > 1 and sp[0] == '!':
                    if sp[2] == '=':
                        sp = '!= ' + sp[3:]
                    else:
                        sp = sp[2:]
                        sp = sp.replace('><', '<>')
                #if nat_type in ('redirect', 'dnat'): sp = sp.replace('=', '')
                cmd = cmd + ' port ' + sp
        dip = rd.pop('rule', 'destination-ip')
        if not dip:
            dip = 'to 0.0.0.0/0.0.0.0'
        #if nat_type not in ('redirect', 'dnat'):
        cmd = cmd + ' ' + dip
        if has_proto:
            dp = rd.pop('protocol', 'destination-port')
            if dp:
                if len(dp) > 1 and dp[0] == '!':
                    if dp[2] == '=':
                        dp = '!= ' + dp[3:]
                    else:
                        dp = dp[2:]
                        dp = dp.replace('><', '<>')
                #if nat_type in ('redirect', 'dnat'):
                #    dp = dp.replace(' =', '')
                cmd = cmd + ' port ' + dp
            tcpflags = rd.pop('protocol', 'tcp-flags')
            if tcpflags:
                if not has_nat: cmd = cmd + ' ' + tcpflags
            syn = rd.pop('protocol', 'syn-only')
            if syn:
                if not has_nat: cmd = cmd + ' ' + syn
        frag = rd.pop('rule', 'fragment-only')
        if frag:
            if not has_nat: cmd = cmd + ' ' + frag
        if has_proto:
            icmptype = rd.pop('protocol', 'icmp-type')
            if icmptype:
                if not has_nat: cmd = cmd + ' ' + icmptype

        if st and not has_nat:
            cmd = cmd + ' ' + st

        if has_nat:
            cmd = cmd + ' ->'
            if nat_type == 'masq':
                to_address = '0/32'
            elif nat_type == 'redirect':
                to_address = '127.0.0.1'
            if not to_address: to_address = '0.0.0.0/0.0.0.0'
            cmd = cmd + ' ' + to_address
            if proto: proto = proto[6:]
            if to_port:
                cmd = cmd + ' port'
                if nat_type in ('snat', 'masq'):
                    cmd = cmd + 'map' # the 'portmap' keyword
                    if proto == '17': cmd = cmd + ' udp'
                    else: cmd = cmd + ' tcp'
                    cmd = cmd + ' ' + to_port
                else:
                    cmd = cmd + ' ' + to_port
                    if proto == '17': cmd = cmd + ' udp'
                    elif proto == '6': cmd = cmd + ' tcp'

        if action == 'delete':
            if has_nat: return '^' + cmd
            rn = self.getRuleNumber()
            if rn:
                sl_print_error('cannot delete a rule via rule-number')
                return ''
            return '%' + cmd

        if has_nat:
            return '!' + cmd
        return cmd


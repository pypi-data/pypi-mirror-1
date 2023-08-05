"""
Rule class (daxfi package).

The representation of a firewall's rule.

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

import imp, os

from daxfi._rulesutils import *
from daxfi.RuleBuilder import RuleData


# --- Functions used to import C modules

def _get_C_module_name(n):
    """Return the expected name of the C module for the given firewall."""
    data = os.uname()
    opsys = data[0].lower()
    arch = data[4].lower()
    if len(arch) > 3 and arch[0] == 'i' and arch[2:4] == '86':
        arch = 'i386'
    return '_' + n + '_' + opsys + '_' + arch

def import_C_module(modname):
    """Import a C module; if the module doesn't exists, a fake
    module is returned."""
    modname = 'daxfi.firewalls.' + modname + '.' + _get_C_module_name(modname)
    try: 
        m = __import__(modname, globals(), locals(), [modname.split('.')[-1]])
    except ImportError:
        m = imp.new_module(modname)
    if not getattr(m, 'is_supported', None):
        def is_supported(*args, **kw): return 0
        setattr(m, 'is_supported', is_supported)
    if not getattr(m, 'list_rules', None):
        def list_rules(direction, *args, **kw): return []
        setattr(m, 'list_rules', list_rules)
    if not getattr(m, 'list_chains', None):
        def list_chains(*args, **kw): return []
        setattr(m, 'list_chains', list_chains)
    if not getattr(m, 'get_policy', None):
        def get_policy(*args, **kw): return ''
        setattr(m, 'get_policy', get_policy)
    return m


# --- Misc functions

def rule_to_bare_xml(rd):
    """Return the XML representation of a RuleData object."""
    x = '<rule '
    r = rd.popNode('rule')
    for a, v in r.items():
        x += a + '="' + v + '" '
    x += '>\n'
    for node in rd.listNodes():
        x += '  <' + node + ' '
        for attribute in rd.list(node):
            x += attribute + '="' + rd.get(node, attribute) + '" '
        x += '/>\n'
    x += '</rule>'
    return x

def rule_to_xml(rd, action, ruleNumber):
    """Given a RuleData object, an action and a ruleNumber,
    return a XML string."""
    x = '<?xml version="1.0"?>\n\n<' + action
    if ruleNumber:
        x += ' ' + str(ruleNumber)
    x += '>\n'
    for line in rule_to_bare_xml(rd).splitlines():
        x += '  ' + line + '\n'
    x += '</' + action + '>'
    return x


# --- The RuleBase class

class RuleBase:
    """Class that define a firewall rule.

    A firewall rule is described with a RuleData object, the action to be
    taken for this rule and an optional ruleNumber (only for certain actions).
    """
    converter = {}
    first_transformation = {}
    section_transformation = {}
    withLog = 1

    def __init__(self, rd=RuleData(), action='', ruleNumber=None):
        """Create a new rule.

        *rd* -- The RuleData object which describes the rule.

        *action* -- The action to be taken for this rule.

        *ruleNumber* -- The optional rule number
                        (useful for 'insert'-like rules).
        """
        self.reset()
        self.setAction(action)
        self.setRuleNumber(ruleNumber)
        self.setRuleData(rd)

    def __getattr__(self, name):
        """Called when an attribute lookup has not found the attribute."""
        if name == 'firewallName':
            mn = self.__module__
            return mn.split('.')[-1]
        elif name == 'action':
            return self.getAction()
        elif name == 'ruleNumber':
            return self.getRuleNumber()
        raise AttributeError, name

    def setRuleData(self, rd):
        """Set the RuleData object."""
        self.__command = None
        self.__rd = rd
        self.__modified_rd = None

    def getRuleData(self):
        """Return a copy of the RuleData object."""
        return self.__rd.copy()

    def reset(self):
        """Reset this Rule object."""
        self.__command = None
        self.setRuleData(RuleData())
        self.setAction('')
        self.setRuleNumber(None)

    def getFirewallName(self):
        """Return the firewall name."""
        return self.firewallName

    def setAction(self, action):
        """Set the action to be taken for  this rule."""
        self.__command = None
        self.__action = action

    def getAction(self):
        """Get the action for this rule.

        Return the action, one of the values in xml_actions.
        """
        return self.__action

    def getTarget(self):
        """Return the target for this rule."""
        return self.__rd.get('target', 'target')
        
    def getModifiedRuleData(self):
        """Get the RuleData object modified with
        the self.converter dictionary."""
        if not self.__modified_rd:
            if self.__rd:
                self.__modified_rd = self.__rd.copy()
                modifyRuleData(self.__modified_rd, self.converter)
            else:
                sl_print_error('this rule is uninitialized')
        return self.__modified_rd

    def getDirection(self):
        """Return the direction for this rule."""
        d = self.__rd.get('rule', 'direction')
        if d: return d
        elif self.__rd.hasNode('nat'):
            return 'nat'
        return ''

    def setRuleNumber(self, ruleNumber):
        """Set the rule number."""
        self.__command = None
        self.__rule_number = ruleNumber

    def getRuleNumber(self):
        """Get the rule number."""
        if self.__rule_number is not None:
            return str(self.__rule_number)
        return None

    def getXML(self):
        """Return a pretty XML string for this rule."""
        if not self.__rd:
            return ''
        return rule_to_xml(self.__rd.copy(), self.__action, self.__rule_number)

    def getBareXML(self):
        """Return the bare XML representation of the rule, without
        the action and the rule number."""
        if not self.__rd:
            return ''
        return rule_to_bare_xml(self.__rd.copy())

    def __str__(self):
        """Print this rule."""
        return self.getRuleCommand()

    def __repr__(self):
        """The representation string for Rule objects."""
        return '<%s firewall rule at %s>' % (self.firewallName, id(self))

    def __cmp__(self, other):
        """Compare two rules."""
        if self.__rd == other.__rd:
            return 0
        return 1

    def __xor__(self, other):
        """Merge two rules."""
        res = self.__class__(RuleData(), self.__action, self.__rule_number)
        res.setRuleData(self.__rd ^ other.__rd)
        return res

    def __nonzero__(self):
        """The rule is 'true' if it generates a command."""
        if self.getRuleCommand():
            return 1
        return 0

    def copy(self):
        """Return a copy of itself."""
        return self.__class__(self.__rd.copy(), self.__action,
                                self.__rule_number)

    def _getRuleCommand(self):
        """Return a string used to run the command for this rule.

        By default, just return the list of attributes of the
        RuleData object.
        This method must be override in the 'Rule' class that
        inherits from this class.
        """
        if not self.__modified_rd:
            return ''
        act = self.getAction()
        return act + ' ' + self.__modified_rd.getDataFlat()

    def getRuleCommand(self):
        """Return a string that is the command to run this rule."""
        act = self.getAction()
        if not act:
            sl_print_error('no action specified for this rule')
            self.__command = ''
        if not self.__rd or not self.getModifiedRuleData():
            sl_print_error('rule uninitialized')
            self.__command = ''
        if act not in xml_actions:
            sl_print_error('unknown action: "' + act + '"')
            self.__command = ''
        if self.__command is None:
            self.__command = self._getRuleCommand()
        return self.__command



"""
daxfi package.

This package is used to develop DAXFi-based applications.

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

import types, commands

from daxfi._exceptions import *
from daxfi._syslog import *
from daxfi.RuleBuilder import RuleBuilder
from _rulesutils import mergeRuleWithUDC

__all__ = ['Firewall', 'DetectFirewallError', 'SingletonFirewall',
            'listAvailableFirewalls', 'Rule', 'RuleBuilder', 'firewalls']

__version__ = '1.0'


# - Main class

class Firewall:
    """The main class.

    Through an instance of this class, you have complete control over
    your firewall.
    """
    def __init__(self, firewallBrand=None, substitutionDict={}):
        """Return an instance of the Firewall class.

        Initialize a Firewall object.

        *firewallBrand* -- a string or a list of strings amongst
                            which the firewall will be selected.

        *substitutionDict* -- the dictionary used to substitute some
                                predefined strings in XML files.
        """
        self.__ruleClass = None
        self.__ruleBuilder = None
        self.__fw_mod = None
        self.__fw_name = ''
        self.__fw_forced = 0
        self.setSubstitutionDict(substitutionDict)
        self._loadFirewall(brand=firewallBrand)

    def __repr__(self):
        """Return the representation for a Firewall object."""
        s = '<%s ' % self.getFirewallName()
        if self.__fw_forced:
            s += '(forced) '
        return s + 'firewall at %x>' % id(self)

    def _loadFirewall(self, brand=None):
        """Detect the firewall and import related modules."""
        from daxfi import firewalls
        if brand and type(brand) in (types.StringType, types.UnicodeType):
            brand = [brand]
        # If not specified, we'll try any known firewall.
        if not brand:
            brand = firewalls.firewallsList
        mod = None
        for fw in brand:
            try:
                mod = __import__('daxfi.firewalls.' + fw,
                                    None, None, fw)
            except ImportError, e:
                sl_print_error(e)
                continue
            funct = mod.__dict__.get('is_supported')
            if callable(funct):
                if funct():
                    # The firewall is supported.
                    self.__fw_mod = mod
                    self.__fw_forced = 0
                    break
                elif mod and len(brand) == 1:
                    # A single firewall was specified, and it's not
                    # supported, and so we're forced to use it.
                    self.__fw_mod = mod
                    self.__fw_forced = 1
                    break
        else:
            raise DetectFirewallError, 'unable to detect the firewall'
        del firewalls
        if not self.__fw_mod:
            raise DetectFirewallError, 'unable to detect the firewall'
        self.__ruleClass = self.__fw_mod.Rule
        self.__fw_name = self.__fw_mod.__name__.split('.')[-1]
        self.__ruleBuilder = RuleBuilder(self.__ruleClass, self.__fw_name)

    def _runCommand(self, cmd):
        """Execute a given command.  Return 0 for error."""
        if not cmd:
            return 0
        if type(cmd) not in (types.StringType, types.UnicodeType):
            sl_print_error('the command "' + str(cmd) + '" is not a string')
            return 0
        status, output = commands.getstatusoutput(cmd)
        if status:
            sl_print_error('got status error "' + str(status) +
                            '" executing "' + cmd + '"; the output was: "' +
                            output + '"')
            return 0
        return 1

    def forceFirewall(self, firewallBrand):
        """Force the use of the given firewall."""
        self._loadFirewall(brand=firewallBrand)

    def isForced(self):
        """Return true if the used firewall was forced."""
        return self.__fw_forced
 
    def setSubstitutionDict(self, substitutionDict):
        """Set the substitution dictionary."""
        if type(substitutionDict) is not types.DictType:
            raise ValueError, 'the substitutionDict must be a dictionary'
        for val in substitutionDict.keys() + substitutionDict.values():
            if type(val) not in (types.StringType, types.UnicodeType):
                raise ValueError, 'the key or value "' + str(val) + \
                                    '" is not a string'
        self.__subDict = substitutionDict

    def getSubstitutionDict(self):
        """Get the substitution dictionary."""
        return self.__subDict

    def getFirewallName(self):
        """Return the name of the running firewall."""
        return self.__fw_name

    def getRuleClass(self):
        """Return the class that represents a Rule for this firewall."""
        return self.__ruleClass

    def getRuleBuilder(self):
        """Return the RuleBuilder object used to create new rules."""
        return self.__ruleBuilder

    def _subDictSubstitution(self, s):
        """Substitute well known strings in the given XML string with
        user supplied data."""
        for k, v in self.__subDict.items():
            s = s.replace(k, v)
        return s

    def _parseXMLFile(self, fname):
        """Parse a XML file, return a list of Rule objects."""
        file_content = ''
        try:
            f = open(fname, 'r')
            file_content = f.read()
            f.close()
        except IOError, e:
            sl_print_error(e)
            return []
        return self._parseXMLString(file_content)

    def _parseXMLString(self, s):
        """Parse a XML string, with substitution of the user supplied
        substituition dictionary."""
        return self.__ruleBuilder.parseXMLString(self._subDictSubstitution(s))

    def newRulesFromXMLFile(self, fileName):
        """Parse XML file.

        Parse a XML file, and return a list of rules.

        *fileName* -- the name of the file to parse.
        """
        return self._parseXMLFile(fileName)

    def newRulesFromXMLString(self, xmlString):
        """New rules from XML strings.

        Parse a XML string and return a list of rules.
        """
        return self._parseXMLString(xmlString)

    def _create(self,
            action='append',
            pos=None,
            target='drop',
            direction='in',
            source='0.0.0.0/0.0.0.0',
            destination='0.0.0.0/0.0.0.0',
            interface='',
            proto='',
            sport='',
            dport='',
            log=0):
        """Create a set of rules with the given parameters.
        By default the direction is 'in' and the target is 'drop'.
        """
        p = ''
        if proto:
            p = ' protocol="%s" ' % proto
        if sport:
            p = p + ' source-port="%s"' % sport
        if dport:
            p = p + ' destination-port="%s"' % dport
        if p:
            p = '<protocol %s />' % p
        if log:
            p = p + '<log />'
        p = p + '<target target="%s" />' % target

        x = '<?xml version="1.0"?><%s' % action
        if pos:
            x += ' rule-number="%s"' % str(pos)
        x += '>'
        x += '<rule direction="%s" source-ip="%s" ' \
                'destination-ip="%s" ' % (direction, source, destination)
        if interface:
            x += ' interface="%s" ' % interface
        x += '>'
        p = '%s%s</rule></%s>' % (x, p, action)
        return self.newRulesFromXMLString(p)

    def createNewRules(self, *args, **kw):
        """Create new rules with the given parameters."""
        return apply(self._create, args, kw)

    def _runRule(self, r):
        """Execute a given rule."""
        if not isinstance(r, self.__ruleClass):
            sl_print_error('this is not a Rule object')
            return 0
        return self._runCommand(r.getRuleCommand())

    def runRules(self, rules):
        """Execute a given rule or list of rules."""
        if type(rules) not in (types.ListType, types.TupleType):
            return self._runRule(rules)
        r = 1
        for i in rules:
            if not self._runRule(i):
                r = 0
        return r

    def runXMLFile(self, fileName):
        """Parse an XML file and run the resulting set of rules."""
        return self.runRules(self.newRulesFromXMLFile(fileName))

    def runXMLString(self, xmlString):
        """Parse an XML string and run the resulting set of rules."""
        return self.runRules(self.newRulesFromXMLString(xmlString))

    def runNewRules(self, *args, **kw):
        """Create and run new rules with the given parameters."""
        return self.runRules(apply(self.createNewRules, args, kw))

    def getRuleCommands(self, rules):
        """Return a list of commands for the given rule or list of rules."""
        rlist = []
        if type(rules) not in (types.ListType, types.TupleType):
            rlist.append(str(rules))
        else:
            rlist += [str(x) for x in rules]
        return rlist

    def getXMLRules(self, rules):
        """Return a list of XML strings for the given rule or list of rules."""
        rlist = []
        if type(rules) not in (types.ListType, types.TupleType):
            rlist.append(rules.getXML())
        else:
            rlist += [x.getXML() for x in rules]
        return rlist

    def listRules(self, direction):
        """Return the list of rules in the given direction."""
        res = []
        for i in self.listXMLRules(direction):
            res += self.__ruleBuilder.parseXMLString(i)
        return res

    def listCommandRules(self, direction):
        """Return a list of commands for the given direction."""
        return [x.getRuleCommand() for x in self.listRules(direction)]

    def listXMLRules(self, direction):
        """Return a list of XML strings; one for every running rule."""
        try:
            return self.__fw_mod.list_rules(direction)
        except OSError, e:
            if self.__fw_forced:
                return []
            else:
                raise OSError, e

    def listChains(self):
        """Return the list of defined chains."""
        try:
            return self.__fw_mod.list_chains()
        except OSError, e:
            if self.__fw_forced:
                return []
            else:
                raise OSError, e

    def getPolicy(self, direction):
        """Return a Rule object representing the policy for the given chain."""
        try:
            policy = self.__fw_mod.get_policy(direction)
        except OSError, e:
            if self.__fw_forced:
                return []
            else:
                raise OSError, e
        if policy:
            return self.createNewRules(target=policy, direction=direction)
        else:
            return []

    def dumpRulesUDC(self, direction):
        """Dump rules in the given chain, merging rules in
        user-defined chains; return a list of Rule objects.
        
        This method should be called only when you've user-defined
        chains in your running set of rules.  The policy of the chain
        is considered."""
        chains = {}
        result = []
        for chain in self.listChains():
            chains[chain] = self.listRules(chain)
        for rule in chains.get(direction, []):
            result += filter(None, mergeRuleWithUDC(rule, chains))
        policy = self.getPolicy(direction)
        if policy:
            result += policy
        return result

    def checkRule(self, rule):
        """If a rule is actually running, return the rule index,
        -1 otherwise."""
        direction = ''
        direction = rule.getDirection()
        if not direction:
            return -1
        rlist = self.listRules(direction)
        try:
            return rlist.index(rule)
        except ValueError:
            return -1


class _SingletonFactory:
    """Create a singleton of a given class."""
    __baseClass = None
    __object = None
    def __init__(self, base_class):
        self.__baseClass = base_class
    def __call__(self, *args, **kw):
        if self.__object is None:
            self.__object = apply(self.__baseClass, args, kw)
        return self.__object


# A 'singletonized' version of the Firewall class.
SingletonFirewall = _SingletonFactory(Firewall)


# - Functions

def listAvailableFirewalls():
    """Return a list of available and supported firewalls."""
    flist = []
    from daxfi import firewalls
    for fw in firewalls.firewallsList:
        try:
            mod = __import__('daxfi.firewalls.' + fw, None, None, fw)
        except ImportError, e:
            sl_print_error(e)
            continue
        funct = mod.__dict__.get('is_supported')
        if callable(funct) and funct():
            flist.append(mod.__name__.split('.')[-1])
    return flist



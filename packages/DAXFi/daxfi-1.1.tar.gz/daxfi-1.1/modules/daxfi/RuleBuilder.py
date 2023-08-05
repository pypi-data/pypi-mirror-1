"""
RuleBuilder class (daxfi package).

The RuleBuilder class, used to generate Rule objects.

  Copyright 2001-2006 Davide Alberani <alberanid@libero.it>

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

import types, copy
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from xml.sax import make_parser, handler, SAXException
from xml.sax.xmlreader import InputSource

from daxfi._rulesutils import *


class RuleData:
    """Manage data representing a firewall rule."""
    def __init__(self):
        """Initialize the RuleData object."""
        self.reset()

    def reset(self):
        """Reset a RuleData object."""
        self.__data = {}

    def getData(self):
        """Return a copy of the data dictionary."""
        return copy.deepcopy(self.__data)

    def setData(self, data):
        """Set the data dictionary."""
        self.__data = data

    def setNode(self, node, data):
        """Set a given node."""
        self.__data[str(node)] = data

    def set(self, node, attribute, value):
        """Set a given attribute."""
        node = str(node)
        if node not in self.__data.keys():
            self.__data[node] = {}
        self.__data[node][str(attribute)] = str(value)

    def hasNode(self, node):
        """Return true if the object has the given node."""
        return node in self.__data.keys()

    def has(self, node, attribute):
        """Return true if the object has the given attribute."""
        return node in self.__data.keys() \
                and attribute in self.__data[node].keys()

    def listNodes(self):
        """List available nodes."""
        return self.__data.keys()

    def list(self, node):
        """List available attributes in the given node."""
        n = self.__data.get(node)
        if not n:
            return []
        return n.keys()

    def popNode(self, node):
        """Return a given node, and delete it from the data set."""
        n = self.__data.get(node)
        if n is not None:
            del self.__data[node]
        return n

    def _getAttributes(self, node, attributes, default, delete):
        """Get/pop an attribute."""
        n = self.__data.get(node)
        if not n:
            if delete and n == {}:
                del self.__data[node]
            if type(attributes) in (types.StringType, types.UnicodeType):
                return default
            else:
                return [default] * len(attributes)
        l = []
        if type(attributes) in (types.StringType, types.UnicodeType):
            attributes = [attributes]
        for item in attributes:
            v = n.get(item)
            if v is None:
                v = default
            elif delete:
                del n[item]
            l.append(v)
        if delete and n == {}:
            del self.__data[node]
        if len(l) == 1:
            return l[0]
        return l

    def pop(self, node, attributes, default=''):
        """Return the given attribute(s) or 'default' if not present in the
        data set, and remove it."""
        return self._getAttributes(node, attributes, default, delete=1)

    def getNode(self, node):
        """Return the given node."""
        return self.__data.get(node)

    def get(self, node, attributes, default=''):
        """Return the given attribute(s) or 'default' if not present."""
        return self._getAttributes(node, attributes, default, delete=0)

    def copy(self):
        """Return a copy of this object."""
        x = RuleData()
        x.setData(copy.deepcopy(self.__data))
        return x

    def __len__(self):
        """Return how many nodes are in the data set."""
        return len(self.__data)

    def __cmp__(self, other):
        """Compare two RuleData objects."""
        if self.__data == other.__data:
            return 0
        return 1

    def __xor__(self, other):
        """Merge two RuleData objects."""
        res = RuleData()
        for node, attribute in [(x, y) for x in self.intersection(other.__data)
                                for y in self.intersection(other.__data, x)]:
            if self.__data[node][attribute] != other.__data[node][attribute]:
                if node == attribute == 'target': continue
                res.setData({})
                return res
        data = other.getData()
        for node in filter(data.has_key, self.__data.keys()):
            data[node].update(self.__data[node])
        for node in filter(lambda x, data=data: not data.has_key(x),
                            self.__data.keys()):
            data[node] = copy.deepcopy(self.__data[node])
        target = other.get('target', 'target')
        if target:
            if data.get('target') is None:
                data['target'] = {}
            data['target']['target'] = target
        elif data.get('target') is not None:
            del data['target']
        res.setData(data)
        return res

    def intersection(self, dictionary, node=None):
        """Return a list that is the intersection between this object's data
        and a dictionary."""
        if node is None:
            data = self.__data
            dkeys = dictionary.keys()
        else:
            data = self.__data.get(node)
            dkeys = dictionary.get(node)
        if not data or not dkeys:
            return []
        if type(dkeys) is types.DictType:
            dkeys = dkeys.keys()
        return filter(data.has_key, dkeys)

    def getDataFlat(self):
        """Return a string with every 'attribute-name value' couple."""
        l = []
        for node, attribute in [(x, y) for x in self.listNodes()
                                        for y in self.list(x)]:
            value = self.get(node, attribute)
            l.append(value)
        return ' '.join(l)


class DAXFiXMLHandler(handler.ContentHandler):
    """Handler for DAXFi XMLs."""
    special_tags = xml_targets + xml_protocols + xml_nat

    def __init__(self, firewallName=None):
        """Initizialize the handler."""
        handler.ContentHandler.__init__(self)
        self.setFirewallName(firewallName)
        self.reset()

    def reset(self):
        """Reset the handler."""
        self.__rdl = []
        self.__rn = None
        self.__action = None
        self.__rd = RuleData()

    def setFirewallName(self, firewallName):
        """Set the name of the running firewall."""
        self.__firewallName = firewallName

    def getRulesList(self):
        """Return the list of parsed rules."""
        return self.__rdl

    def processingInstruction(self, target, data):
        """Manage processing instructions."""
        if target == 'daxfi-process':
            sd = data.find("'")
            if sd == -1: sd = data.find('"')
            e = data.rfind("'")
            if e == -1: e = data.rfind('"')
            ldata = [x.strip() for x in data[sd+1:e].split(',')]
            # Search 'only-for'.
            if data.find('only-for') != -1:
                if self.__firewallName not in ldata:
                    raise DaxfiStopProcessing
            # Search 'not-for'.
            elif data.find('not-for') != -1:
                if self.__firewallName in ldata:
                    raise DaxfiStopProcessing
            else:
                sl_print_warning('unknown value for processing' + \
                                    ' instruction: "' + data + '"')
        else:
            sl_print_warning('unknown processing instruction: "' + \
                                target + '"')

    def startElement(self, name, attrs):
        """Manage a new open tag."""
        if name == 'ruleset': return
        elif name in xml_actions:
            self.__action = name
            if 'rule-number' in attrs.getNames():
                self.__rn = attrs.getValue('rule-number')
            else:
                self.__rn = None
            return
        elif name in self.special_tags:
            oname = name
            if name in xml_targets:
                name = 'target'
            elif name in xml_protocols:
                name = 'protocol'
            elif name in xml_nat:
                name = 'nat'
            self.__rd.set(name, name, oname)
        else:
            self.__rd.setNode(name, {})
        for attr in attrs.getNames():
            self.__rd.set(name, attr, attrs.getValue(attr))

    def endElement(self, name):
        """Manage a new closing tag."""
        if name == 'rule':
            self.__rdl.append((self.__rd, self.__action, self.__rn))
            self.__rd = RuleData()

# --- The RuleBuilder class, used to generate Rule objects

class RuleBuilder:
    """Class used to build a set of Rule objects.

    The parseXMLString() method return a list of Rule objects
    for the given XML string.
    """
    first_transformation = {
                            'rule': {
                                'source-ip':        (transf_ip, CALL),
                                'destination-ip':   (transf_ip, CALL)
                            },
                            'protocol': {
                                'protocol':         (transf_proto, CALL),
                                'source-port':      (transf_port, CALL),
                                'destination-port': (transf_port, CALL),
                                'tcp-flags':        (transf_sort, CALL),
                                'icmp-type':        (transf_icmp, CALL)
                            },
                            'target': {
                                'reject-with':      (transf_icmp, CALL)
                            },
                            'nat': {
                                'to-address':       (transf_ip_nomask, CALL),
                                'to-port':          (transf_port, CALL)
                            }
                        }

    section_transformation = {}

    default_remove = {
                        'rule': {
                            'source-ip':    (transf_ip_remove_default, CALL),
                            'destination-ip': (transf_ip_remove_default, 
                                                    CALL)
                        },
                        'protocol': {
                            'source-port':  (transf_port_remove_default, CALL),
                            'destination-port': (transf_port_remove_default,
                                                    CALL)
                        }
                    }

    def __init__(self, ruleClass, firewallName):
        """Initialize a RuleBuilder object.

        *ruleClass* -- the class used to create Rule objects.
        
        *firewallName* -- the name of the firewall."""
        self.setRuleClass(ruleClass)
        self.setFirewallName(firewallName)
        self.__dh = DAXFiXMLHandler(self.__firewallName)
        self.__inpsrc = InputSource()
        self.__parser = make_parser()
        self.__parser.setContentHandler(self.__dh)
        self.__parser.setFeature('http://xml.org/sax/features/external-general-entities', 0)
        ##self.__parser.setFeature('http://xml.org/sax/features/external-parameter-entities', 0)
        ##self.__parser.setFeature('http://xml.org/sax/features/validation', 0)
        self.reset()

    def parseXMLString(self, xmlString):
        """Parse a given XML string; return a list of Rule objects."""
        self.reset()
        try:
            self.__inpsrc.setByteStream(StringIO(xmlString))
            self.__parser.parse(self.__inpsrc)
        except DaxfiStopProcessing:
            pass
        except SAXException, e:
            sl_print_error('XML parser error: ' + str(e))
        rlist = []
        for i in self.__dh.getRulesList():
            rdata = i[0]
            modifyRuleData(rdata, forEveryAttribute=transf_normalize,
                            convSections=self.section_transformation,
                            convAttributes=self.first_transformation)
            modifyRuleData(rdata,
                        convAttributes=self.__ruleClass.first_transformation,
                        convSections=self.__ruleClass.section_transformation)
            modifyRuleData(rdata, convAttributes=self.default_remove)
            rlist += self.getRules(rdata, i[1], i[2])
        return rlist

    def reset(self):
        """Reset the builder."""
        self.__dh.reset()

    def setRuleClass(self, ruleClass):
        """An hack."""
        self.__ruleClass = ruleClass

    def setFirewallName(self, firewallName):
        """Another hack."""
        self.__firewallName = firewallName

    def getRulesWithoutLog(self, rd, action, rn):
        """Return the rules for firewalls without a log option
        (they need a separated logging rule, like iptables)."""
        rlist = []
        has_log = rd.hasNode('log')
        has_target = rd.hasNode('target')
        if has_log:
            if has_target:
                rd0 = rd.copy()
                rd.popNode('target')
                rd0.popNode('log')
                rd0.popNode('limit')
                rlist = [self.__ruleClass(rd, action, rn),
                            self.__ruleClass(rd0, action, rn)]
            else:
                rlist = [self.__ruleClass(rd, action, rn)]
        else:
            rlist = [self.__ruleClass(rd, action, rn)]
        return rlist

    def getRulesWithLog(self, rd, action, rn):
        """Return the rules for this XML.

        Elaborate the current XML and return a set of Rule object.
        For firewalls that can log and set rules with a single command.
        """
        return [self.__ruleClass(rd, action, rn)]

    def getRules(self, rd, action, rn):
        """Return the rules for the given XML."""
        if self.__ruleClass.withLog:
            return self.getRulesWithLog(rd, action, rn)
        else:
            return self.getRulesWithoutLog(rd, action, rn)



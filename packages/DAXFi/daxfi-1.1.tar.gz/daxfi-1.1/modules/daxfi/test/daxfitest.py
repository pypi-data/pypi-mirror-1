#!/usr/bin/env python
#
# Test suite for daxfi.
#
# It's OK if error messages are printed on the logs; only the printed
# lines are relevant.
#


import unittest, sys
from daxfi import Firewall
from daxfi import sl_print_error


# The firewall object.
firewall = Firewall()


# - Some XML strings.

xml1 = """<?xml version="1.0"?>

<append>
  <rule source-ip="0/0" destination-ip="1.2.3.4" direction="in">
    <tcp />
    <reject />
  </rule>
  <rule source-ip="0/0" destination-ip="1.2.3.4" direction="in">
    <icmp />
    <accept />
  </rule>
  <rule source-ip="0/0" destination-ip="1.2.3.4" direction="in">
    <udp />
    <drop />
  </rule>
</append>
"""

xml2 = """<?xml version="1.0"?>

<!DOCTYPE insert SYSTEM "daxfifw_0.5.dtd">

<insert rule-number="2">
  <rule source-ip="1.2.3.4/8" direction="out">
    <udp destination-port="1024:65535" />
    <accept />
  </rule>
</insert>
"""

xml3 = """<?xml version="1.0"?>

<ruleset>
  <flush>
    <rule direction="in" />
    <rule direction="out" />
  </flush>
</ruleset>
"""

xml4 = """<?xml version="1.0"?>

<append>
  <rule direction="in">
    <accept />
    <tcp state="related" />
  </rule>
</append>
"""

xml5 = """<?xml version="1.0"?>
<append>
  <rule direction="in">
    <accept />
    <log />
  </rule>
</append>
"""

xml6 = """<?xml version="1.0"?>
<append>
  <rule direction="in">
    <accept />
    <log>
      <limit rate="1/s" burst="10" />
    </log>
  </rule>
</append>
"""

xml7 = """<?xml version="1.0"?>
<append>
  <rule direction="in">
    <tcp destination-port="1024:65535" state="new" />
    <accept />
  </rule>
</append>
"""

#xml8 = """<?xml version="1.0"?>
#
#<ruleset>
#  <set-policy direction="out">
#    <accept />
#  </set-policy>
#</ruleset>
#"""

xml9 = """<?xml version="1.0"?>

<delete>
  <rule direction="out">
    <udp source-port="123" />
    <drop />
  </rule>
</delete>
"""

xml10 = """<?xml version="1.0"?>

<append>
  <rule direction="in">
    <tcp source-port="! 123" />
    <accept />
  </rule>
</append>
"""

xml11 = """<?xml version="1.0"?>

<append>
  <rule direction="in">
    <tcp syn-only="yes" />
    <accept />
  </rule>
</append>
"""

xml12 = """<?xml version="1.0"?>
<append>
  <rule direction="in">
    <tcp syn-only="no" />
    <accept />
  </rule>
</append>
"""

xml13 = """<?xml version="1.0"?>

<append>
  <rule direction='in' source-ip='192.168.3.0/24' interface='le1'>
    <snat to-address='5.6.7.8' to-port='1:1024' />
  </rule>
</append>
"""

xml14  = """<?xml version="1.0"?>

<append>
  <rule source-ip='192.16.1.0/24' interface='ppp0'>
    <masq />
  </rule>
</append>
"""

xml15 = """<?xml version='1.0'?>

<append>
  <rule source-ip='1.2.3.0/24' interface='le2'>
    <tcp source-port='80' />
    <redirect to-port='8080' />
  </rule>
</append>
"""


xmlw1 = """<?xml version="1.0"?>

<just a="badTag" />
"""

xmlw2 = """<?xml version="1.0"?>

<a wrong="xml (with no closing tag)">
"""

# - Associate XML strings to results for various firewalls.

data = {
    xml1:   (
            (   'iptables -A INPUT -p 6 --destination 1.2.3.4/255.255.255.255 -j REJECT',
               'iptables -A INPUT -p 1 --destination 1.2.3.4/255.255.255.255 -j ACCEPT',
                'iptables -A INPUT -p 17 --destination 1.2.3.4/255.255.255.255 -j DROP'),
            ('ipchains -A input -j REJECT --destination 1.2.3.4/255.255.255.255 -p 6',
                'ipchains -A input -p 1 -j ACCEPT --destination 1.2.3.4/255.255.255.255',
                'ipchains -A input -p 17 -j DENY --destination 1.2.3.4/255.255.255.255'),
            ('ipfwadm -a reject -I  -D 1.2.3.4/255.255.255.255 -P tcp',
                'ipfwadm -a accept -I  -D 1.2.3.4/255.255.255.255 -P icmp',
                'ipfwadm -a deny -I  -D 1.2.3.4/255.255.255.255 -P udp'),
                ('block return-icmp in quick proto 6 from 0.0.0.0/0.0.0.0 to 1.2.3.4/255.255.255.255', 'pass in quick proto 1 from 0.0.0.0/0.0.0.0 to 1.2.3.4/255.255.255.255', 'block in quick proto 17 from 0.0.0.0/0.0.0.0 to 1.2.3.4/255.255.255.255')),

    xml2:   (
            ('iptables -I OUTPUT 2 -p 17 -j ACCEPT --source 1.0.0.0/255.0.0.0 --destination-port 1024:65535',),
            ('ipchains -I output 2 -p 17 -j ACCEPT --source 1.0.0.0/255.0.0.0 --destination-port 1024:65535',),
            ('ipfwadm -i accept -O -D 0.0.0.0/0.0.0.0 1024:65535  -S 1.0.0.0/255.0.0.0 -P udp',),
            ('@2 pass out quick proto 17 from 1.0.0.0/255.0.0.0 to 0.0.0.0/0.0.0.0 port 1024 >< 65535',)),

    xml3:   (
            (   'iptables -F INPUT',
                'iptables -F OUTPUT'),
            ('ipchains -F input',
                'ipchains -F output'),
            ('ipfwadm -f -I', 'ipfwadm -f -O'),
            ('# Execute the command: ipf -Fi', '# Execute the command: ipf -Fo')),

    xml4:   (
            ('iptables -A INPUT -p 6 -m state --state ESTABLISHED,RELATED -j ACCEPT',),
            ('',),
            ('',),
            ('pass out quick proto 6 from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0 keep state',)),

    xml5:   (
            (   'iptables -A INPUT -j LOG',
                'iptables -A INPUT -j ACCEPT'),
            ('ipchains -A input -j ACCEPT -l',),
            ('ipfwadm -a accept -I -o',),
            ('pass in log quick from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0',)),

    xml6:   (
            (   'iptables -A INPUT -m limit -j LOG --limit-burst 10 --limit 1/s',
                'iptables -A INPUT -j ACCEPT'),
            ('ipchains -A input -j ACCEPT -l',),
            ('ipfwadm -a accept -I -o',),
            ('pass in log quick from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0',)),

    xml7:   (
            ('iptables -A INPUT -p 6 -m state -j ACCEPT --state INVALID,NEW --destination-port 1024:65535',),
            ('',),
            ('',),
            ('',)),

    #xml8:   (
    #        ('iptables -P OUTPUT ACCEPT',),
    #        ('ipchains -P output ACCEPT',),
    #        ('ipfwadm -p accept -O',),
    #        ('pass out all',)),

    xml9:   (
            ('iptables -D OUTPUT -p 17 -j DROP --source-port 123',),
            ('ipchains -D output -p 17 -j DENY --source-port 123',),
            ('ipfwadm -d deny -O -S 0.0.0.0/0.0.0.0 123  -P udp',),
            ('# Remove the rule: "block out quick proto 17 from 0.0.0.0/0.0.0.0 port = 123 to 0.0.0.0/0.0.0.0"',)),

    xml10:  (
            ('iptables -A INPUT -p 6 --source-port ! 123 -j ACCEPT',),
            ('ipchains -A input -p 6 --source-port ! 123 -j ACCEPT',),
            ('',),
            ('pass in quick proto 6 from 0.0.0.0/0.0.0.0 port !=  123 to 0.0.0.0/0.0.0.0',)),

    xml11:  (
            ('iptables -A INPUT -p 6 --syn -j ACCEPT',),
            ('ipchains -A input -j ACCEPT -p 6 --syn',),
            ('ipfwadm -a accept -I -y -P tcp',),
            ('pass in quick proto 6 from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0 flags S/SRA',)),

    xml12:  (
            ('iptables -A INPUT -p 6 ! --syn -j ACCEPT',),
            ('ipchains -A input -p 6 ! --syn -j ACCEPT',),
            ('ipfwadm -a accept -I -k -P tcp',),
            ('pass in quick proto 6 from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0 flags SA',)),

    xml13:  (
            ('iptables -A POSTROUTING -p 6 -t nat -j SNAT --to-source 5.6.7.8:1-1024 --out-interface le1 --source 192.168.3.0/255.255.255.0',),
            ('',),
            ('',),
            ('map le1 from 192.168.3.0/255.255.255.0 to 0.0.0.0/0.0.0.0 -> 5.6.7.8/255.255.255.255 portmap tcp 1:1024',)),

    xml14:  (
            ('iptables -A POSTROUTING -t nat -j MASQUERADE --out-interface ppp0 --source 192.16.1.0/255.255.255.0',),
            ('ipchains -A forward -j MASQ --interface ppp0 --source 192.16.1.0/255.255.255.0',),
            ('ipfwadm -a masquerade -F -W ppp0 -S 192.16.1.0/255.255.255.0',),
            ('map ppp0 from 192.16.1.0/255.255.255.0 to 0.0.0.0/0.0.0.0 -> 0/32',)),

    xml15:  (
            ('iptables -A OUTPUT -p 6 -t nat -j REDIRECT --to-ports 8080 --out-interface le2 --source 1.2.3.0/255.255.255.0 --source-port 80',),
            ('ipchains -A input -j REDIRECT 8080 --interface le2 --source 1.2.3.0/255.255.255.0 --source-port 80 -p 6',),
            ('ipfwadm -a accept -I -r 8080 -S 1.2.3.0/255.255.255.0 80 -W le2 -P tcp',),
            ('rdr le2 from 1.2.3.0/255.255.255.0 port = 80 to 0.0.0.0/0.0.0.0 -> 127.0.0.1 port 8080 tcp',)),

    xmlw1:   ((), (), (), ()),
    xmlw2:   ((), (), (), ())
}


def split_string(thestring):
    """Split strings in (-switch value) 'atoms' so that they can be compared."""
    sp = thestring.split()
    index = 0
    while index < len(sp):
        c = sp[index]
        if c and c[0] == '-':
            try:
                s = sp[index+1]
            except IndexError:
                break
            if s and s[0] != '-':
                if s[0] == '!':
                    p = ''
                    try:
                        p = sp[index+2]
                        if p and p[0] != '-':
                            sp[index] = c + ' ' + s + ' ' + p
                            del sp[index+1]
                            del sp[index+1]
                    except IndexError:
                        pass
                    if p and p[0] != '-':
                        continue
                sp[index] = c + ' ' + s
                del sp[index+1]
        index = index + 1
    sp.sort()
    return sp


def perror_len(a, b):
    la = len(a)
    lb = len(b)
    ra = [str(r) for r in a]
    rb = b
    s = 'got ' + str(la) + ' results (' + str(lb) + ' expected)\n\n' + \
        'Results: ' + str(ra) + '\n\nExpected: ' + (rb)
    return s


def perror_dif(a, b):
    s = 'these rules are different!\n\nRule A (got): ' + str(a) + \
            '\n\nRule B (expected): ' + str(b)
    return s


class XMLParserTestCase(unittest.TestCase):
    """Check the parser."""
    xml = ''
    res = ()

    def setFirewall(self, fw):
        self.firewall = fw

    def compareRule(self, rule, result):
        r = split_string(str(rule))
        result = split_string(result)
        if r == result:
            return 1
        return 0
        
    def checkParser(self):
        rl = self.firewall.newRulesFromXMLString(self.xml)
        assert len(rl) == len(self.res), perror_len(rl, self.res)
        i = 0
        for r1, r2 in map(None, rl, self.res):
            assert self.compareRule(r1, r2), perror_dif(rl[i], self.res[i])
            i = i + 1


def make_test_OLD():
    s = unittest.TestSuite()
    for k, v in data.items():
        tc = XMLParserTestCase('checkParser')
        tc.xml = k
        tc.res = v[FWI]
        s.addTest(tc)
    return s

def make_test():
    s = unittest.TestSuite()
    from daxfi.firewalls import __all__
    for fw in __all__:
        if fw == 'iptables':
            fwi = 0
        elif fw == 'ipchains':
            fwi = 1
        elif fw == 'ipfwadm':
            fwi = 2
        elif fw == 'ipfilter':
            fwi = 3
        else:
            raise ValueError, 'unknown firewall: ' + fw + \
                        '; update this test suite!'
            sys.exit(1)
        for k, v in data.items():
            tc = XMLParserTestCase('checkParser')
            tc.setFirewall(Firewall(firewallBrand=fw))
            tc.xml = k
            tc.res = v[fwi]
            s.addTest(tc)
    return s



class DumpRule(unittest.TestCase):
    """Check the dump of rules from a running firewall."""
    flush = """<?xml version="1.0"?><flush><rule direction="in"/></flush>"""
    rule = """<?xml version="1.0"?>
              <append>
                <rule direction="in" source-ip="5.6.7.8/24"
                        destination-ip="1.2.3.4/8">
                    <tcp source-port="123" destination-port="100:200" />
                    <log />
                    <accept />
                </rule>
              </append>"""

    def setUp(self):
        firewall.runXMLString(self.flush)
    def tearDown(self):
        firewall.runXMLString(self.flush)

    def checkListRules(self):
        original_rules = firewall.newRulesFromXMLString(self.rule)
        firewall.runRules(original_rules)
        lr = firewall.listRules('in')
        assert len(original_rules) == len(lr), perror_len(original_rules, lr)
        for r1, r2 in map(None, original_rules, lr):
            assert split_string(str(r1)) == split_string(str(r2)), \
                        perror_dif(r1, r2)

    def checkCreate(self):
        original_rules = firewall.createNewRules(source='5.6.7.8/24',
                                    destination='1.2.3.4/8',
                                    direction='in',
                                    proto='tcp',
                                    dport='100:200',
                                    sport='123',
                                    log=1,
                                    target='accept',
                                    action='append')
        rules = firewall.newRulesFromXMLString(self.rule)
        assert len(original_rules) == len(rules), perror_len(original_rules,
                                                                rules)
        i = 0
        for r1, r2 in map(None, original_rules, rules):
            assert split_string(str(r1)) == \
                    split_string(str(r2)), \
                        perror_dif(str(original_rules[i]),
                                    str(rules[i]))
            i = i + 1


parser_suite = make_test()
dump_suite = unittest.makeSuite(DumpRule, 'check')

allsuites = unittest.TestSuite((parser_suite, dump_suite))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(allsuites)



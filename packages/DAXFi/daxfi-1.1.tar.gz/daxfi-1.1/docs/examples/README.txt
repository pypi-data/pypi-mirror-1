
To see the resulting command for these XML files, use the
'daxfixmlfile' script.

You can use the '-f' option to specify a given firewall,
otherwise your installed firewall is used.

E.g.:

# daxfixmlfile -f ipchains test01.xml
ipchains -A input -j ACCEPT --destination-port 80 -p 6 --source 192.196.1.0/255.255.255.0

# daxfixmlfile -f ipfilter test13.xml
block in log level local2.warn quick on ppp0 from 0.0.0.0/0.0.0.0 to 127.0.0.0/255.0.0.0

# daxfixmlfile -f iptables test13.xml
iptables -A INPUT -j LOG --log-level warn --in-interface ppp0 --destination 127.0.0.0/255.0.0.0
iptables -A INPUT -j DROP --in-interface ppp0 --destination 127.0.0.0/255.0.0.0



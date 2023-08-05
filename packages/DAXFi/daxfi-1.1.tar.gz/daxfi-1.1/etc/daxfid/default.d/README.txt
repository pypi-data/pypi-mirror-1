
  default runlevel

A useful default for a single dial-up machine.

With iptables the output will be:
# Flush chains.
iptables -F INPUT
iptables -F OUTPUT

# Accept everything on the local interface.
iptables -A INPUT -j ACCEPT --in-interface lo
iptables -A OUTPUT -j ACCEPT --out-interface lo

# Reject and log auth connections.
iptables -A INPUT -p 6 -m limit --limit 1/s -j LOG --destination-port 113 --limit-burst 10 --source 5.6.7.8/255.255.255.255 --destination 1.2.3.4/255.255.255.255
iptables -A INPUT -p 6 -j REJECT --destination-port 113 --source 5.6.7.8/255.255.255.255 --destination 1.2.3.4/255.255.255.255

# Block and log some martians.
iptables -A INPUT -m limit --limit 1/s -j LOG --limit-burst 10 --in-interface le1 --source 127.0.0.0/255.0.0.0
iptables -A INPUT -j DROP --in-interface le1 --source 127.0.0.0/255.0.0.0
iptables -A INPUT -m limit --limit 1/s -j LOG --limit-burst 10 --in-interface le1 --source 1.2.3.4/255.255.255.255
iptables -A INPUT -j DROP --in-interface le1 --source 1.2.3.4/255.255.255.255 

# Block and log connection attempts and invalid connections from the outside.
iptables -A INPUT -p 6 -m state -m limit --limit 1/s -j LOG --state INVALID,NEW --limit-burst 10 --source 5.6.7.8/255.255.255.255 --destination 1.2.3.4/255.255.255.255
iptables -A INPUT -p 6 -m state -j DROP --state INVALID,NEW --source 5.6.7.8/255.255.255.255 --destination 1.2.3.4/255.255.255.255

# Accept tcp and udp connections opened from the inside.
iptables -A INPUT -p 6 -m state -j ACCEPT --destination-port 1024:65535 --state ESTABLISHED,RELATED --destination 1.2.3.4/255.255.255.255
iptables -A INPUT -p 17 -m state -j ACCEPT --destination-port 1024:65535 --state ESTABLISHED,RELATED --destination 1.2.3.4/255.255.255.255

# Block some icmp types.
iptables -A INPUT -p 1 -m state -j DROP --icmp-type 0 --state INVALID,NEW
iptables -A INPUT -p 1 -m state -j DROP --icmp-type 8 --state INVALID,NEW
iptables -A INPUT -p 1 -j DROP --icmp-type 5
iptables -A INPUT -p 1 -j DROP --icmp-type 9
iptables -A INPUT -p 1 -j DROP --icmp-type 10 

# Accept other icmp types.
iptables -A INPUT -p 1 -j ACCEPT
iptables -A OUTPUT -p 1 -j ACCEPT

# Set policy
iptables -A OUTPUT -j ACCEPT 
iptables -A INPUT -j DROP 


With ipchains:
ipchains -F input
ipchains -F output
ipchains -A input -j ACCEPT --interface lo
ipchains -A output -j ACCEPT --interface lo
ipchains -A input -j REJECT -l --destination-port 113 -p 6 --source 5.6.7.8/255.255.255.255 --destination 1.2.3.4/255.255.255.255
ipchains -A input -j DENY -l --interface le1 --source 127.0.0.0/255.0.0.0
ipchains -A input -j DENY -l --interface le1 --source 1.2.3.4/255.255.255.255
ipchains -A input -j ACCEPT --destination-port 1024:65535 -p 6 ! --syn --source 5.6.7.8/255.255.255.255 --destination 1.2.3.4/255.255.255.255
ipchains -A input -j ACCEPT --destination-port 1024:65535 -p 17 --source 5.6.7.8/255.255.255.255 --destination 1.2.3.4/255.255.255.255
ipchains -A input -j DENY --icmp-type 5 -p 1
ipchains -A input -j DENY --icmp-type 9 -p 1
ipchains -A input -j DENY --icmp-type 10 -p 1
ipchains -A input -j ACCEPT -p 1
ipchains -A output -j ACCEPT -p 1
ipchains -A output -j ACCEPT 
ipchains -A input -j DENY 


With ipfwadm:
ipfwadm -f -I 
ipfwadm -f -O 
ipfwadm -a accept -I -W lo
ipfwadm -a accept -O -W lo
ipfwadm -a reject -I -D 1.2.3.4/255.255.255.255 113 -o -P tcp -S 5.6.7.8/255.255.255.255
ipfwadm -a deny -I -o -W le1 -S 127.0.0.0/255.0.0.0
ipfwadm -a deny -I -o -W le1 -S 1.2.3.4/255.255.255.255
ipfwadm -a accept -I -D 1.2.3.4/255.255.255.255 1024:65535 -k -P tcp -S 5.6.7.8/255.255.255.255
ipfwadm -a accept -I -D 1.2.3.4/255.255.255.255 1024:65535 -P udp -S 5.6.7.8/255.255.255.255
ipfwadm -a deny -I -S 0.0.0.0/0.0.0.0 5 -P icmp
ipfwadm -a deny -I -S 0.0.0.0/0.0.0.0 9 -P icmp
ipfwadm -a deny -I -S 0.0.0.0/0.0.0.0 10 -P icmp
ipfwadm -a accept -I -P icmp
ipfwadm -a accept -O -P icmp
ipfwadm -a accept -O 
ipfwadm -a deny -I 

With ipfilter:
# Execute the command: ipf -Fi
# Execute the command: ipf -Fo
pass in quick on lo from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0
pass out quick on lo from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0
block return-icmp in log quick proto 6 from 5.6.7.8/255.255.255.255 to 1.2.3.4/255.255.255.255 port = 113
block in log quick on le1 from 127.0.0.0/255.0.0.0 to 0.0.0.0/0.0.0.0
block in log quick on le1 from 1.2.3.4/255.255.255.255 to 0.0.0.0/0.0.0.0
pass out quick proto 6 from 0.0.0.0/0.0.0.0 to 1.2.3.4/255.255.255.255 port 1024 >< 65535 keep state
pass out quick proto 17 from 0.0.0.0/0.0.0.0 to 1.2.3.4/255.255.255.255 port 1024 >< 65535 keep state
block in quick proto 1 from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0 icmp-type 5
block in quick proto 1 from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0 icmp-type 9
block in quick proto 1 from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0 icmp-type 10
pass in quick proto 1 from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0
pass out quick proto 1 from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0
pass out quick from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0
block in quick from 0.0.0.0/0.0.0.0 to 0.0.0.0/0.0.0.0



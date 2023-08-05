
  flush runlevel

Flush any rules in the default chains and reset the policies
to ACCEPT.

With iptables:
iptables -F INPUT
iptables -F OUTPUT



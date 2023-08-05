  DAXFi - The Dynamic XML Firewall

DAXFi is a Python package that helps configure several different
kinds of firewalls in a consistent way.
The rules can be described with XML files, XML strings,
or generated directly by the code.
It comes with a Python package, useful to build other
applications aimed to manipulate different firewalls in a
homogeneous way (some useful example programs are included).

DAXFi is many things: it's a Python package to develop new
firewall-independent applications and it's a set of scripts
useful for users, developers and network/system administrators.

If you are a developer:
- maybe you need to control a firewall, but you want to stay
  independent from the syntax of a specific tool (like ipfilter,
  iptables, ipchains, and so on): you can import the daxfi Python
  package from your program, instantiate the Firewall class and then
  use the object to create new rules (from XML files or XML strings or
  directly in the code).
  Then you can run these rules, you can see what rules are already
  running in your system, compare two rules and so on.
  For more info on the daxfi package, please read "README.daxfiPackage"

If you are a user or a network/system administrator:
- with the 'daxfictl' script you can add and remove firewall rules
  from the command line: you can grant or deny access to defined
  addresses; the script is smart enough to refuse to run a rule that already
  exists.
  See "README.daxfictl"

- with 'daxfixmlfile' you can write your rules in XML files, and
  then use this script to generate/run the commands for your firewall.
  See "README.daxfixmlfile"

- if you have a set of rules already running, you can use the
  'daxfidump' script to obtain an equivalent set of XML files.
  See "README.daxfidump"

- you can use the 'daxfid' script: it's a program that helps configure
  a firewall for a dial-up system, and can run as a daemon to adapt its
  behavior to external conditions.
  See "./daxfid/README.daxfid"
  NOTE: the 'daxfid' program is quite big and complex: it's not the
  ideal starting point, if you're using DAXFi for the very first time.
  Try playing with other scripts, like 'daxfixmlfile' and 'daxfictl', first.


No matter what you use it for, DAXFi uses XML to describe firewall's rules;
you can find a short how-to about how to write XML files for DAXFi in
the "xmlrules.html" file, and some examples in the "./examples" directory.



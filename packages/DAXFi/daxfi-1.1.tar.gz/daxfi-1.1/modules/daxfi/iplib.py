"""
iplib module.

The representations of IPv4 addresses and netmasks.
You can use this module to convert amongst many different notations
and to manage couples of address/netmask in the CIDR notation.

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

import string, types

__version__ = '0.6'


# Notation types.
IP_UNKNOWN = NM_UNKNOWN = 0
IP_DOT = NM_DOT = 1 # 192.168.0.42
IP_HEX = NM_HEX = 2 # 0xC0A8002A
IP_BIN = NM_BIN = 3 # 030052000052
IP_OCT = NM_OCT = 4 # 11000000101010000000000000101010
IP_DEC = NM_DEC = 5 # 3232235562
NM_BITS = 6 # 26
NM_WILDCARD = 7 # 0.0.0.63

# Map notation with one or more strings.
NOTATION_MAP = {
    IP_DOT:         ('dotted decimal', 'dotted', 'quad', 'dot', 'dotted quad'),
    IP_HEX:         ('hexadecimal', 'hex'),
    IP_BIN:         ('binary', 'bin'),
    IP_OCT:         ('octal', 'oct'),
    IP_DEC:         ('decimal', 'dec'),
    NM_BITS:        ('bits', 'bit', 'cidr'),
    NM_WILDCARD:    ('wildcard bits', 'wildcard'),
    IP_UNKNOWN:     ('unknown', 'unk')
}

_NK = NOTATION_MAP.keys()
_NI = NOTATION_MAP.items()

def _get_notation(notation):
    """Return one value in IP_DOT, IP_HEX, IP_BIN, etc."""
    if notation in _NK:
        return notation
    for key, item in _NI:
        if notation in item:
            return key
    return None

# Note: /31 (4294967294L) is not a valid netmask.
VALID_NETMASKS = {0: 0L, 1: 2147483648L, 2: 3221225472L, 3: 3758096384L,
                    4: 4026531840L, 5: 4160749568L, 6: 4227858432L,
                    7: 4261412864L, 8: 4278190080L, 9: 4286578688L,
                    10: 4290772992L, 11: 4292870144L, 12: 4293918720L,
                    13: 4294443008L, 14: 4294705152L, 15: 4294836224L,
                    16: 4294901760L, 17: 4294934528L, 18: 4294950912L,
                    19: 4294959104L, 20: 4294963200L, 21: 4294965248L,
                    22: 4294966272L, 23: 4294966784L, 24: 4294967040L,
                    25: 4294967168L, 26: 4294967232L, 27: 4294967264L,
                    28: 4294967280L, 29: 4294967288L, 30: 4294967292L,
                    32: 4294967295L}


# - Functions used to check if an address or a netmask is in a given notation.

def is_dot(ip):
    """Return true if the IP address is in dotted decimal notation."""
    octets = string.split(str(ip), '.')
    if len(octets) != 4:
        return 0
    for i in octets:
        try:
            val = int(i)
        except (ValueError, OverflowError):
            return 0
        if val < 0 or val > 255:
            return 0
    return 1

def is_hex(ip):
    """Return true if the IP address is in hexadecimal notation."""
    try:
        dec = long(str(ip), 16)
    except (TypeError, ValueError):
        return 0
    if dec < 0 or dec > 0xFFFFFFFFL:
        return 0
    return 1

def is_bin(ip):
    """Return true if the IP address is in binary notation."""
    try:
        ip = str(ip)
        if len(ip) != 32:
            return 0
        dec = long(ip, 2)
    except (TypeError, ValueError):
        return 0
    if dec < 0 or dec > 4294967295L:
        return 0
    return 1

def is_oct(ip):
    """Return true if the IP address is in octal notation."""
    try:
        dec = long(str(ip), 8)
    except (TypeError, ValueError):
        return 0
    if dec < 0 or dec > 037777777777L:
        return 0
    return 1

def is_dec(ip):
    """Return true if the IP address is in decimal notation."""
    try:
        dec = long(str(ip))
    except ValueError:
        return 0
    if dec < 0 or dec > 4294967295L:
        return 0
    return 1

def _check_nm(nm, kind):
    NM_CHECK_FUNCT = {
        NM_DOT: _dot_to_dec,
        NM_HEX: _hex_to_dec,
        NM_BIN: _bin_to_dec,
        NM_OCT: _oct_to_dec,
        NM_DEC: _dec_to_dec_long}
    # Convert to decimal, and check if it's in the list of valid netmasks.
    try:
        dec = NM_CHECK_FUNCT[kind](nm, check=1)
    except ValueError:
        return 0
    if dec in VALID_NETMASKS.values():
        return 1
    return 0

def is_dot_nm(nm):
    """Return true if the netmask is in dotted decimal notatation."""
    return _check_nm(nm, NM_DOT)

def is_hex_nm(nm):
    """Return true if the netmask is in hexadecimal notatation."""
    return _check_nm(nm, NM_HEX)
            
def is_bin_nm(nm):
    """Return true if the netmask is in binary notatation."""
    return _check_nm(nm, NM_BIN)

def is_oct_nm(nm):
    """Return true if the netmask is in octal notatation."""
    return _check_nm(nm, NM_OCT)

def is_dec_nm(nm):
    """Return true if the netmask is in decimal notatation."""
    return _check_nm(nm, NM_DEC)

def is_bits_nm(nm):
    """Return true if the netmask is in bits notatation."""
    try:
        bits = int(str(nm))
    except (ValueError, OverflowError):
        return 0
    if bits < 0 or bits > 32 or bits == 31:
        return 0
    return 1

def is_wildcard_nm(nm):
    """Return true if the netmask is in wildcard bits notatation."""
    try:
        dec = 0xFFFFFFFFL - _dot_to_dec(nm, check=1)
    except ValueError:
        return 0
    if dec in VALID_NETMASKS.values():
        return 1
    return 0


# - Functions used to detect the notation of an IP address or netmask.

CHECK_FUNCT = {
    IP_DOT: (is_dot, is_dot_nm),
    IP_HEX: (is_hex, is_hex_nm),
    IP_BIN: (is_bin, is_bin_nm),
    IP_OCT: (is_oct, is_oct_nm),
    IP_DEC: (is_dec, is_dec_nm),
    NM_BITS: (lambda: 0, is_bits_nm),
    NM_WILDCARD:    (lambda: 0, is_wildcard_nm)
}

def _detect(ip, isnm):
    ip = str(ip)
    chkhex = 1
    chkoct = 1
    if len(ip) > 1:
        if ip[0:2] == '0x':
            if CHECK_FUNCT[IP_HEX][isnm](ip):
                return IP_HEX
            chkhex = 0
        elif ip[0] == '0':
            if CHECK_FUNCT[IP_OCT][isnm](ip):
                return IP_OCT
            chkoct = 0
    if CHECK_FUNCT[IP_DOT][isnm](ip):
        return IP_DOT
    elif isnm == 1 and CHECK_FUNCT[NM_BITS][isnm](ip):
        return NM_BITS
    elif isnm == 1 and CHECK_FUNCT[NM_WILDCARD][isnm](ip):
        return NM_WILDCARD
    elif CHECK_FUNCT[IP_BIN][isnm](ip):
        return IP_BIN
    elif chkhex and CHECK_FUNCT[IP_HEX][isnm](ip):
        return IP_HEX
    elif chkoct and CHECK_FUNCT[IP_OCT][isnm](ip):
        return IP_OCT
    elif CHECK_FUNCT[IP_DEC][isnm](ip):
        return IP_DEC
    return IP_UNKNOWN

def detect(ip):
    """Detect the notation of an IP address.

    @param ip: the IP address.
    @type ip: integers, strings or object with an appropriate __str()__ method.
    @return: one of the IP_* constants; IP_UNKNOWN if undetected.
    """
    return _detect(ip, isnm=0)

def detect_nm(nm):
    """Detect the notation of a netmask."""
    return _detect(nm, isnm=1)

def p_detect(ip):
    """Return the notation of a IP address (string)."""
    return NOTATION_MAP[detect(ip)][0]

def p_detect_nm(nm):
    """Return the notation of the netmask (string)."""
    return NOTATION_MAP[detect_nm(nm)][0]


def _is_notation(ip, notation, isnm):
    notation_orig = notation
    notation = _get_notation(notation)
    if notation not in CHECK_FUNCT.keys():
        raise ValueError, '_is_notation: unkown notation: "' + \
                            str(notation_orig) + '"'
    return CHECK_FUNCT[notation][isnm](ip)

def is_notation(ip, notation):
    """Return true if the given address is in the given notation."""
    return _is_notation(ip, notation, isnm=0)

def is_notation_nm(nm, notation):
    """Return true if the given netmask is in the given notation."""
    return _is_notation(nm, notation, isnm=1)


# - Functions used to convert various notation to/from decimal notation.

def _dot_to_dec(ip, check=1):
    """Dotted decimal notation to decimal conversion."""
    if check and not is_dot(ip):
        raise ValueError, '_dot_to_dec: invalid IP: "' + str(ip) + '"'
    octets = string.split(str(ip), '.')
    dec = 0L
    dec = dec | (long(octets[0]) << 24)
    dec = dec | (long(octets[1]) << 16)
    dec = dec | (long(octets[2]) << 8)
    dec = dec | long(octets[3])
    return dec

def _dec_to_dot(ip):
    """Decimal to dotted decimal notation conversion."""
    first = int((ip >> 24) & 255)
    second = int((ip >> 16) & 255)
    third = int((ip >> 8) & 255)
    fourth = int(ip & 255)
    return str(first) + '.' + str(second) + '.' + \
            str(third) + '.' + str(fourth)


def _hex_to_dec(ip, check=1):
    """Hexadecimal to decimal conversion."""
    if check and not is_hex(ip):
        raise ValueError, '_hex_to_dec: invalid IP: "' + str(ip) + '"'
    if type(ip) in (types.IntType, types.LongType):
        ip = hex(ip)
    return long(str(ip), 16)

def _dec_to_hex(ip):
    """Decimal to hexadecimal conversion."""
    return hex(ip)[:-1]


def _oct_to_dec(ip, check=1):
    """Octal to decimal conversion."""
    if check and not is_oct(ip):
        raise ValueError, '_oct_to_dec: invalid IP: "' + str(ip) + '"'
    if type(ip) in (types.IntType, types.LongType):
        ip = oct(ip)
    return long(str(ip), 8)

def _dec_to_oct(ip):
    """Decimal to octal conversion."""
    return oct(ip)[:-1]


def _bin_to_dec(ip, check=1):
    """Binary to decimal conversion."""
    if check and not is_bin(ip):
        raise ValueError, '_bin_to_dec: invalid IP: "' + str(ip) + '"'
    if type(ip) in (types.IntType, types.LongType):
        ip = str(ip)
    return long(str(ip), 2)

def _dec_to_bin(ip):
    """Decimal to binary conversion."""
    bin = ''
    for i in range(0, 32):
        if ip & 1:
            bin = '1' + bin
        else:
            bin = '0' + bin
        ip = ip >> 1
    return bin


def _dec_to_dec_long(ip, check=1):
    """Decimal to decimal (long) conversion."""
    if check and not is_dec(ip):
        raise ValueError, '_dec_to_dec: invalid IP: "' + str(ip) + '"'
    return long(str(ip))

def _dec_to_dec_str(ip):
    """Decimal to decimal (string) conversion."""
    return str(ip)


def _bits_to_dec(nm, check=1):
    """Bits to decimal conversion."""
    if check and not is_bits_nm(nm):
        raise ValueError, '_bits_to_dec: invalid IP: "' + str(nm) + '"'
    index = long(str(nm))
    return VALID_NETMASKS[index]

def _dec_to_bits(nm):
    """Decimal to bits conversion."""
    for key, value in VALID_NETMASKS.items():
        if value == nm:
            return str(key)


def _wildcard_to_dec(nm, check=0):
    """Wildcard bits to decimal conversion."""
    if check and not is_wildcard_nm(nm):
        raise ValueError, '_wildcard_to_dec: invalid IP: "' + str(nm) + '"'
    return 0xFFFFFFFFL - _dot_to_dec(nm, check=0)

def _dec_to_wildcard(nm):
    """Decimal to wildcard bits conversion."""
    return _dec_to_dot(0xFFFFFFFFL - nm)


def _convert(ip, notation, iformat, check, isnm):
    iformat_orig = iformat
    notation_orig = notation
    iformat = _get_notation(iformat)
    notation = _get_notation(notation)
    if iformat is None:
        raise ValueError, 'convert: unknown input format: "' + \
                            str(iformat_orig) + '"'
    if notation is None:
        raise ValueError, 'convert: unknown notation: "' + \
                            str(notation_orig) + '"'
    if type(ip) in (types.IntType, types.LongType) and iformat == IP_UNKNOWN:
        raise ValueError, 'convert: when the IP is given in a numeric' + \
                        ' format, you must specify it with the "iformat"' + \
                        ' parameter'
    docheck = 1
    if check != 0 and iformat == IP_UNKNOWN:
        iformat = _detect(ip, isnm)
        docheck = 0
    if check == 0:
        docheck = 0
    elif check == 1:
        docheck = 1
    dec = 0L
    if iformat == IP_DOT:
        dec = _dot_to_dec(ip, docheck)
    elif iformat == IP_HEX:
        dec = _hex_to_dec(ip, docheck)
    elif iformat == IP_BIN:
        dec = _bin_to_dec(ip, docheck)
    elif iformat == IP_OCT:
        dec = _oct_to_dec(ip, docheck)
    elif iformat == IP_DEC:
        dec = _dec_to_dec_long(ip, docheck)
    elif isnm and iformat == NM_BITS:
        dec = _bits_to_dec(ip, docheck)
    elif isnm and iformat == NM_WILDCARD:
        dec = _wildcard_to_dec(ip, docheck)
    else:
        raise ValueError, 'convert: unknown IP format: "' + \
                            str(iformat_orig) + '"'
    if isnm and dec not in VALID_NETMASKS.values():
        raise ValueError, 'convert: invalid netmask: "' + str(ip) + '"'
    if notation == IP_DOT:
        return _dec_to_dot(dec)
    elif notation == IP_HEX:
        return _dec_to_hex(dec)
    elif notation == IP_BIN:
        return _dec_to_bin(dec)
    elif notation == IP_OCT:
        return _dec_to_oct(dec)
    elif notation == IP_DEC:
        return _dec_to_dec_str(dec)
    elif isnm and notation == NM_BITS:
        return _dec_to_bits(dec)
    elif isnm and notation == NM_WILDCARD:
        return _dec_to_wildcard(dec)
    else:
        raise ValueError, 'convert: unknown notation: "' + \
                            str(notation_orig) + '"'

def convert(ip, notation=IP_DOT, iformat=IP_UNKNOWN, check=None):
    """Convert among IP address notations.

    Given an IP address, this function returns the address
    in another notation.

    @param ip: the IP address.
    @type ip: integers, strings or object with an appropriate __str()__ method.

    @param notation: the notation of the output (default: IP_DOT).
    @type notation: one of the IP_* constants, or the equivalent strings.

    @param iformat: force the input to be considered in the given notation
                    (default the notation of the input is autodetected).
    @type iformat: one of the IP_* constants, or the equivalent strings.

    @param check: force the notation check on the input (internally used).

    @return: a string representing the IP in the selected notation.

    @raise ValueError: raised when the input is in unknown notation.
    """
    return _convert(ip, notation, iformat, check, isnm=0)

def convert_nm(nm, notation=IP_DOT, iformat=IP_UNKNOWN, check=None):
    """Convert a netmask to another notation."""
    return _convert(nm, notation, iformat, check, isnm=1)


# - Classes used to manage IP addresses, netmasks and the CIDR notation.

class _IPv4Base:
    """Base class for IP addresses and netmasks."""
    _isnm = 0

    def __init__(self, ip, notation=IP_UNKNOWN):
        self.set(ip, notation)

    def set(self, ip, notation=IP_UNKNOWN):
        """Set the IP address/netmask."""
        self._ip_dec = long(_convert(ip, notation=IP_DEC, iformat=notation,
                            check=None, isnm=self._isnm))
        self._ip = _convert(self._ip_dec, notation=IP_DOT, iformat=IP_DEC,
                            check=0, isnm=self._isnm)
    def get(self):
        """Return the address/netmask."""
        return self.get_dot()
    def get_dot(self):
        """Return the dotted decimal notation of the address/netmask."""
        return self._ip
    def get_hex(self):
        """Return the hexadecimal notation of the address/netmask."""
        return _convert(self._ip_dec, notation=IP_HEX,
                        iformat=IP_DEC, check=0, isnm=self._isnm)
    def get_bin(self):
        """Return the binary notation of the address/netmask."""
        return _convert(self._ip_dec, notation=IP_BIN,
                        iformat=IP_DEC, check=0, isnm=self._isnm)
    def get_dec(self):
        """Return the decimal notation of the address/netmask."""
        return str(self._ip_dec)
    def get_oct(self):
        """Return the octal notation of the address/netmask."""
        return _convert(self._ip_dec, notation=IP_OCT,
                        iformat=IP_DEC, check=0, isnm=self._isnm)

    def __str__(self):
        """Print this address/netmask."""
        return self.get()
    def __cmp__(self, other):
        """Compare two addresses/netmasks."""
        if self._ip_dec < other._ip_dec:
            return -1
        elif self._ip_dec > other._ip_dec:
            return 1
        return 0
    def __int__(self):
        """Return the decimal representation of the address/netmask."""
        return self._ip_dec
    def __long__(self):
        """Return the decimal representation of the address/netmask (long)."""
        return long(self._ip_dec)
    def __hex__(self):
        """Return the hexadecimal representation of the address/netmask."""
        return self.get_hex()
    def __oct__(self):
        """Return the octal representation of the address/netmask."""
        return self.get_oct()


class IPv4Address(_IPv4Base):
    """An IPv4 Internet address.

    This class represents an IPv4 Internet address.
    """
    def __repr__(self):
        """The representation string for this address."""
        return '<IPv4 address %s>' % self.get()
    def __add__(self, other):
        """Sum two IP addresses."""
        if type(other) in (types.IntType, types.LongType):
            sum = self._ip_dec + other
        else:
            sum = self._ip_dec + other._ip_dec
        return IPv4Address(sum, notation=IP_DEC)
    def __sub__(self, other):
        """Subtract two IP addresses."""
        if type(other) in (types.IntType, types.LongType):
            sub = self._ip_dec - other
        else:
            sub = self._ip_dec + other._ip_dec
        return IPv4Address(sub, notation=IP_DEC)
    def __getattr__(self, name):
        """Called when an attribute lookup has not found the attribute."""
        if name in ('ip', 'address'):
            return self.get()
        raise AttributeError, name


class IPv4NetMask(_IPv4Base):
    """An IPv4 Internet netmask.

    This class represents an IPv4 Internet netmask.
    """
    _isnm = 1

    def get_bits(self):
        """Return the bits notation of the netmask."""
        return _convert(self._ip, notation=NM_BITS,
                        iformat=IP_DOT, check=0, isnm=self._isnm)
    def get_wildcard(self):
        """Return the wildcard bits notation of the netmask."""
        return _convert(self._ip, notation=NM_WILDCARD,
                        iformat=IP_DOT, check=0, isnm=self._isnm)
    def __repr__(self):
        """The representation string for this netmask."""
        return '<IPv4 netmask %s>' % self.get()
    def __getattr__(self, name):
        """Called when an attribute lookup has not found the attribute."""
        if name in ('nm', 'netmask'):
            return self.get()
        raise AttributeError, name


class CIDR:
    """A CIDR address.

    The representation of a Classless Inter-Domain Routing (CIDR) address.
    """
    def __init__(self, ip, netmask=None):
        self.set(ip, netmask)

    def set(self, ip, netmask=None):
        """Set the IP address and the netmask."""
        self._ips = []
        if netmask is None:
            ipnm = string.split(ip, '/')
            if len(ipnm) != 2:
                raise ValueError, 'set: invalid CIDR: "' + str(ip) + '"'
            ip = ipnm[0]
            netmask = ipnm[1]
        if isinstance(ip, IPv4Address):
            self._ip = ip
        else:
            self._ip = IPv4Address(ip)
        if isinstance(ip, IPv4NetMask):
            self._nm = netmask
        else:
            self._nm = IPv4NetMask(netmask)
        ipl = long(self._ip)
        nml = long(self._nm)
        base_add = ipl & nml
        self._ip_num = 0xFFFFFFFFL - 1 - nml
        if self._ip_num == -1:
            self._ip_num = 1
            self._net_ip = None
            self._bc_ip = None
            self._fist_ip_dec = base_add
            self._first_ip = IPv4Address(self._fist_ip_dec, IP_DEC)
            self._last_ip = self._first_ip
            return None
        self._net_ip = IPv4Address(base_add, IP_DEC)
        self._bc_ip = IPv4Address(base_add + self._ip_num + 1, IP_DEC)
        self._fist_ip_dec = base_add + 1
        self._first_ip = IPv4Address(self._fist_ip_dec, IP_DEC)
        self._last_ip = IPv4Address(base_add + self._ip_num, IP_DEC)

    def get_ip(self):
        """Return the given address."""
        return self._ip
    def get_netmask(self):
        """Return the netmask."""
        return self._nm
    def get_first_ip(self):
        """Return the first usable IP address."""
        return self._first_ip
    def get_last_ip(self):
        """Return the last usable IP address."""
        return self._last_ip
    def get_network_ip(self):
        """Return the network address."""
        return self._net_ip
    def get_broadcast_ip(self):
        """Return the broadcast address."""
        return self._bc_ip
    def get_ip_number(self):
        """Return the number of usable IP addresses."""
        return self._ip_num
    def get_all_valid_ip(self):
        """Return a list of IPv4Address objects, one for every usable IP.

        WARNING: it's slow and can take a huge amount of memory for
        subnets with a large number of addresses.
        """
        if not self._ips:
            for i in xrange(0, self._ip_num):
                self._ips.append(IPv4Address(self._fist_ip_dec + self._ip_num,
                                    IP_DEC))
        return self._ips

    def is_valid_ip(self, ip):
        """Return true if the given address in amongst the usable addresses."""
        if not isinstance(ip, IPv4Address):
            try:
                ip = IPv4Address(ip)
            except ValueError:
                return 0
        if ip < self._first_ip or ip > self._last_ip:
            return 0
        return 1

    def __str__(self):
        """Print this CIDR address."""
        return str(self._ip) + '/' + str(self._nm)
    def __repr__(self):
        """The representation string for this netmask."""
        return '<%s/%s CIDR>' % (str(self.get_ip()), str(self.get_netmask()))
    def __len__(self):
        """Return the number of usable IP address."""
        return self.get_ip_number()
    def __contains__(self, item):
        """Return true if the given address in amongst the usable addresses."""
        return self.is_valid_ip(item)
    def __getattr__(self, name):
        """Called when an attribute lookup has not found the attribute."""
        if name in ('ip', 'address'):
            return self.get_ip()
        if name in ('nm', 'netmask'):
            return self.get_netmask()
        raise AttributeError, name



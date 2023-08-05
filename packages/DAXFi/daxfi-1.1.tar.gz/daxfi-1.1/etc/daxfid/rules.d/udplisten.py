#
# Run in background every 5 seconds and block any open udp port.
#

PERSISTENT = 5

def run_this():

    EXCLUDED_PORTS = []

    DEBUG = 1

    import string

    try:
        udp_f = open('/proc/net/udp', 'r')
        content = udp_f.readlines()
        udp_f.close()
    except IOError:
        sl_print_error('udplisten: unable to open /proc/net/udp')
        return 0

    blocked_ports = loadData('blocked_ports')
    if not blocked_ports:
        blocked_ports = []

    actual_ports = []
    for i in range(1, len(content)):
        this_line = string.split(content[i])
        status = string.atoi(this_line[3], 16)
        if status == 7:
            adr = this_line[1]
            ip_address = string.split(adr, ':')[0]
            udp_port = string.atoi(string.split(adr, ':')[1], 16)
            # Now we got a list of open ports.
            actual_ports.append(udp_port)

    for udp_port in actual_ports:
        if udp_port in blocked_ports:
            continue
        if udp_port in EXCLUDED_PORTS:
            continue
        act = 'append'
        position = '-1'
        if is_daemon():
            act = 'insert'
            position = '1'
        rules = createNewRules(action=act,
                                    pos=position,
                                    source=REMOTE_IP,
                                    destination=LOCAL_IP,
                                    interface=INTERFACE,
                                    dport=`udp_port`,
                                    proto='udp',
                                    log=1)
        if is_daemon():
            rules.reverse()
        for rule in rules:
            ret = checkRule(rule)
            if ret == -1:
                if processRules(rule):
                    if udp_port not in blocked_ports:
                        if DEBUG:
                            sl_print_info('blocked udp port ' + `udp_port`)
                        blocked_ports.append(udp_port)

    for p in blocked_ports:
        if p not in actual_ports:
            rules = createNewRules(action='delete',
                                        source=REMOTE_IP,
                                        destination=LOCAL_IP,
                                        interface=INTERFACE,
                                        dport=`p`,
                                        proto='udp',
                                        log=1)
            for rule in rules:
                if checkRule(rule) != -1:
                    if processRules(rule):
                        if p in blocked_ports:
                            if DEBUG:
                                sl_print_info('unblocked udp port ' + `p`)
                            blocked_ports.remove(p)

    storeData('blocked_ports', blocked_ports)


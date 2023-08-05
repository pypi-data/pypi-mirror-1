#
# A somewhat complex rule:
#
# In the first run block any TCP ports reported to be in LISTEN status
# by /proc/net/tcp.
# After that, it run in daemon mode every five seconds; if one or more new
# open ports are found, they're marked and blocked in the *next* run.
# Beware that when this code is running in daemon mode, new rules used to
# block ports are put as first rules in the INPUT chain.
#
# The user can customize the EXCLUDED_PORTS list of ports not to block,
# and of course the PERSISTENT variable that represent the time in seconds
# to wait between successive executions.
#
# If ONLY_NOT_PRIVILEGED is != 0 any port below 1024 is leaved untouched.
#
# Obviously it's possible to modify the code obtaining more complex
# behaviors.  E.g.: to increment the waiting time between a new rule
# is detected and the effective execution of iptables you can store
# in wait_queue a timestamp for every port number.
#


# Run this rule every 5 seconds.
PERSISTENT = 5

def run_this():
    # List of port not to block.
    # Maybe you want to use something like [25, 80, 113]
    EXCLUDED_PORTS = [113]

    # Don't look at any port under 1024 (they're leaved open; in the sample1
    # level it's not a problem since the default policy will drop any
    # connection, but in sample2 maybe you want to set this variable
    # to 0 and modify EXCLUDED_PORTS above as you like.
    # 
    ONLY_NOT_PRIVILEGED = 1

    # Be verbose in logs.
    DEBUG = 1

    # --- End of user configurable things

    import string

    # Tcp valid states.
    TCP_ESTABLISHED = 1
    TCP_SYN_SENT    = 2
    TCP_SYN_RECV    = 3
    TCP_FIN_WAIT1   = 4
    TCP_FIN_WAIT2   = 5
    TCP_TIME_WAIT   = 6
    TCP_CLOSE       = 7
    TCP_CLOSE_WAIT  = 8
    TCP_LAST_ACK    = 9
    TCP_LISTEN      = 10
    TCP_CLOSING     = 11

    # Read infos from /proc/net/tcp
    content = ''
    try:
        tcp_f = open('/proc/net/tcp', 'r')
        content = tcp_f.readlines()
        tcp_f.close()
    except IOError:
        sl_print_error('tcplisten: unable to open /proc/net/tcp')
        return 0

    # Load data previously stored.
    blocked_ports = loadData('blocked_ports')
    if not blocked_ports:
        blocked_ports = []

    wait_queue = loadData('wait_queue')
    if not wait_queue:
        wait_queue = []

    # Ports in listen status.
    actual_ports = []
    for i in range(1, len(content)):
        this_line = string.split(content[i])
        status = string.atoi(this_line[3], 16)
        if status == TCP_LISTEN:
            adr = this_line[1]
            ip_address = string.split(adr, ':')[0]
            tcp_port = string.atoi(string.split(adr, ':')[1], 16)
            actual_ports.append(tcp_port)

    for tcp_port in actual_ports:
        if ONLY_NOT_PRIVILEGED and tcp_port < 1024:
            continue
        if tcp_port in blocked_ports:
            continue
        if tcp_port in EXCLUDED_PORTS:
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
                                    dport=`tcp_port`,
                                    proto='tcp',
                                    log=1)
        # If we're in daemon mode, we are INSERTing rules, and
        # we need to reverse the rules list so that the LOG
        # rule will appear as the first in the chain.
        if is_daemon():
            rules.reverse()

        lis = []
        for rule in rules:
            if checkRule(rule) == -1:
                lis.append(rule)
        if not lis:
            continue
        if not is_daemon():
            if processRules(lis):
                if DEBUG:
                    sl_print_info('tcp blocked port ' + `tcp_port`)
                if tcp_port not in blocked_ports:
                    blocked_ports.append(tcp_port)
        else:
            # Run the rule.
            if tcp_port in wait_queue:
                if processRules(lis):
                    if tcp_port not in blocked_ports:
                        if DEBUG:
                            sl_print_info('blocked tcp port ' +
                                            `tcp_port`)
                        blocked_ports.append(tcp_port)
                    if tcp_port in wait_queue:
                        wait_queue.remove(tcp_port)
            # Store the port in wait_queue.
            elif tcp_port not in blocked_ports:
                if tcp_port not in wait_queue:
                    wait_queue.append(tcp_port)
                    break

    # Checks if previously blocked ports are now closed.
    for p in blocked_ports:
        if p not in actual_ports:
            rules = createNewRules(action='delete',
                                        source=REMOTE_IP,
                                        destination=LOCAL_IP,
                                        interface=INTERFACE,
                                        dport=`p`,
                                        proto='tcp',
                                        log=1)
            for rule in rules:
                if processRules(rule):
                    if p in blocked_ports:
                        if DEBUG:
                            sl_print_info('unblocked tcp port ' + `p`)
                        blocked_ports.remove(p)

    # Store the data.
    storeData('blocked_ports', blocked_ports)
    storeData('wait_queue', wait_queue)



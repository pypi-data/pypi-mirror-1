"Reads syslog(2) messages from a file."

import re
import socket

sshd_message_re = re.compile(r'sshd\[(?P<pid>\d+)\]: (?P<msg>.+)')

sshd_messages = {
    # Note on the <user> parts: Only allowing non-whitespace because otherwise that's probably
    # an attack against this type of failure-leads-to-ban application; it's been seen before.
    # Instead, we just don't match those lines.

    'invalid_user': re.compile(r'^Invalid user (?P<user>\S+) from (?P<source>.+)$'),
    # Side note: "invalid user" lines generate these too, with "invalid user" 
    # prepended to the username. We avoid matching these intentfully.
    'password_failure': re.compile(r'^Failed password for (?P<user>\S+) from (?P<source>[^ ]+) port \d+ ssh\d$'),
}

def parse_line(line):
    mo = sshd_message_re.search(line)
    if mo is not None:
        sshd_pid, message = mo.groups()
        for sshd_message in sshd_messages:
            mo = sshd_messages[sshd_message].search(message)
            if mo is not None:
                mo = mo.groupdict()
                mo['source'] = validate_source(mo['source'])
                return sshd_pid, sshd_message, mo
    raise ValueError("unparsable line %r" % (line,))

def validate_source(source):
    # gethostbyname returns an IP address if one was passed in.
    try:
        ip_address = socket.gethostbyname(source)
        # alternatively:
        #ip_address = socket.inet_ntoa(socket.inet_aton(source))
    except (socket.gaierror, socket.error):
        return None
    return ip_address

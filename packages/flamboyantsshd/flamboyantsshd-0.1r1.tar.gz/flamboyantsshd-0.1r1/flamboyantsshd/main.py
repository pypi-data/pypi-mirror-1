#!/usr/bin/env python

import sys

from flamboyantsshd import logs, config, tail_file

handler = config.handler(config.Penalties, config.Tolerance)
fp = file(sys.argv[1], "rU")
fp.seek(0, 2)  # 0 bytes from end.

for cmd in sys.argv[2:]:
    if cmd == "process-all":
        fp.seek(0, 0)  # 0 bytes from start.
    elif cmd == "process-new":
        fp.seek(0, 2)  # 0 bytes from end.

for line in tail_file(fp):
    try:
        sshd_pid, message_type, kwargs = logs.parse_line(line)
        getattr(handler, message_type)(**kwargs)
    except ValueError:
        pass

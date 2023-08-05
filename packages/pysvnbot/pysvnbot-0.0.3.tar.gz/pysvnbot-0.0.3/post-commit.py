#!/usr/bin/env python

import sys
import subprocess
import socket

# {{{ Utilities
def run(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    if p.wait() != 0:
        sys.exit(1)
    return p.stdout.read()

class Writer(object):
    def __init__(self, remote_address):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(remote_address)

    def __call__(self, data):
        self.socket.send(data + "\n")
# }}}

# {{{ Get pysvnbot settings.
from pysvnbot import conf
write = Writer(conf.ipc_socket)
# }}}

# {{{ Get SVN info
repos, rev = sys.argv[1:]
author = run(("/usr/bin/svnlook", "author", "--revision", rev, repos)).split("\n", 1)[0]
log = run(("/usr/bin/svnlook", "log", "--revision", rev, repos)).rstrip()
changed = run(("/usr/bin/svnlook", "changed", "--revision", rev, repos)).rstrip().split("\n")
changed_dirs = run(("/usr/bin/svnlook", "dirs-changed", "--revision", rev, repos)).rstrip().split("\n")
# }}}

# {{{ Write out stuff
# Yeah, ugly, so sue me.
write("%s: %s commits r%s. %d file%s in %d dir%s changed." % (repos, author, rev, len(changed), "s"[len(changed) == 1:], len(changed_dirs), "s"[len(changed_dirs) == 1:]))

if len(changed) <= 5:
    for change in changed:
        write("  * %s" % change)

log = log.split("\n")
while log:
    line = log.pop(0)
    while line:
        write(line[:80])
        line = line[80:]
# }}}

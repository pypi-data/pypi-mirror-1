#!/usr/bin/env python

# I recommend that you don't put this as your post-commit hook, rather you
# write a short shell script to call it, which has set PYTHONPATH as it
# should, so that you don't have to edit parts of a package and have it
# overwritten all the time.

from os import path
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
repos_name = path.basename(repos)
author = run(("/usr/bin/svnlook", "author", "--revision", rev, repos)).split("\n", 1)[0]
log = run(("/usr/bin/svnlook", "log", "--revision", rev, repos)).rstrip()
changed = run(("/usr/bin/svnlook", "changed", "--revision", rev, repos)).rstrip().split("\n")
changed_dirs = run(("/usr/bin/svnlook", "dirs-changed", "--revision", rev, repos)).rstrip().split("\n")
# }}}

# {{{ Write out stuff
write("%s: %s commits r%s. %d file%s in %d dir%s changed." % (repos_name,
    author, rev, len(changed), "s"[len(changed) == 1:], len(changed_dirs),
    "s"[len(changed_dirs) == 1:]))

if len(changed) <= 5:
    for change in changed:
        write("  * %s" % change)

while log:
    write(log[:80])
    log = log[80:]
# }}}

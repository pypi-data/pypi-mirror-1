#!/usr/bin/env python
"""Main bot module, run it to get the bot to start. Uses extreme amounts
of threads."""

import sys
from pysvnbot import ipc, conf, start_thread

try:
    import pysimpirc
except ImportError, e:
    print >>sys.stderr, ("Failed importing pysimpirc. It is a required "
        "dependency, and can be installed by running `easy_install pysimpirc`"
        "as root or equivalent.")
    print >>sys.stderr, "Error was:", e
    sys.exit(1)

class AutoJoiner(pysimpirc.CommonIRCConnection):
    """Normal IRC bot that tries to autojoin all channels in sequence given
    in __init__.
    """

    def __init__(self, autojoin=(), **kw):
        super(AutoJoiner, self).__init__(**kw)
        self.autojoin_channels = autojoin
        self.autojoined = False

    def autojoin(self):
        if not self.autojoined:
            self.join(self.autojoin_channels)
            self.autojoined = True

    def irc_001(self, prefix, args):
        self.autojoin()

    def irc_005(self, prefix, args):
        self.autojoin()

    def irc_376(self, prefix, args):
        self.autojoin()

    def irc_422(self, prefix, args):
        self.autojoin()

def start_irc_thread(*a, **kw):
    i = AutoJoiner(*a, **kw)
    i.register()  # Register to the IRCd.
    t = start_thread(i.process_forever, start=False)
    t.connection = i  # Hacky? Yeah.
    t.start()
    return t

def main():
    # Start the IPC server first in case the address is taken. (I am aware of
    # the fact that this is a very crappy line, I find it so crappy it's
    # funny.)
    ipc_svr = ipc.IPCServer(lambda m: [[[t.connection.privmsg(c, l) for l in m.replace("\r", "\n").split("\n")] for c in t.connection.autojoin_channels] for t in threads], conf.ipc_socket)
    # Start the IRC bot threads, nothing odd.
    threads = [start_irc_thread(remote_address=remote_address, **conf.ircs[remote_address]) for remote_address in conf.ircs]
    # "Threadize" the main loop of the IPC server as well.
    threads.append(start_thread(ipc_svr.serve_forever, daemon=True))
    # Wait for the boats to drift ashore.
    [thread.join() for thread in threads]

if __name__ == "__main__":
    main()

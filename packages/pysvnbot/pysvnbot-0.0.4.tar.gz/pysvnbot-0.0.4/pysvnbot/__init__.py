"""Python SVN Bot

The name is sort of a misnomer because it doesn't really need to be SVN, it in
fact doesn't even have to involve any VCS at all, because what the bot does is
open a UNIX socket which you decide where it should be, and then it just
echoes out whatever is received on that socket.
"""

import threading

def start_thread(f, daemon=False, start=True, *a, **kw):
    t = threading.Thread(target=f)
    t.setDaemon(daemon)
    if start:
        t.start()
    return t

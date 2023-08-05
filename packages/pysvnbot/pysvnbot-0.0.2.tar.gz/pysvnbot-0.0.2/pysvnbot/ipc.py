"""Inter-process communication interface module."""

import SocketServer

# I think this is obvious enough to not require any documentation, but I might
# be wrong.
class IPCServer(SocketServer.ThreadingUnixStreamServer):
    def __init__(self, callback, server_address):
        self.callback = callback
        SocketServer.ThreadingUnixStreamServer.__init__(self, server_address,
            IPCRequestHandler)

class IPCRequestHandler(SocketServer.StreamRequestHandler):
    """Simple request handler which just reads in rfile and passes the data
    on to the parent servers' callback function.
    """

    def handle(self):
        self.wfile.close()
        self.server.callback(self.rfile.read())
        self.rfile.close()

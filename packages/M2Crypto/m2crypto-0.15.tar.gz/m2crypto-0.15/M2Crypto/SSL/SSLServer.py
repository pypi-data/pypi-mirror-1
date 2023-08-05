"""Copyright (c) 1999-2002 Ng Pheng Siong. All rights reserved."""

RCS_id='$Id: SSLServer.py 299 2005-06-09 17:32:28Z heikki $'

# Python
import socket, SocketServer

# M2Crypto
from Connection import Connection
from M2Crypto.SSL import SSLError
from M2Crypto import m2


class SSLServer(SocketServer.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, ssl_context):
        """ 
        Superclass says: Constructor. May be extended, do not override.
        This class says: Ho-hum.
        """
        self.server_address=server_address
        self.RequestHandlerClass=RequestHandlerClass
        self.ssl_ctx=ssl_context
        self.socket=Connection(self.ssl_ctx)
        self.server_bind()
        self.server_activate()

    def handle_request(self):
        try:
            request, client_address = self.get_request()
            if self.verify_request(request, client_address):
                self.process_request(request, client_address)
        except SSLError:
            self.handle_error()

    def handle_error(self):
        print '-'*40
        import traceback
        traceback.print_exc()
        print '-'*40


class ForkingSSLServer(SocketServer.ForkingMixIn, SSLServer):
    pass


class ThreadingSSLServer(SocketServer.ThreadingMixIn, SSLServer):
    pass



#!/usr/bin/env python

"""
BaseHTTPRequestHandler adapter.
"""

import WebStack.BaseHTTPRequestHandler
import BaseHTTPServer
from WebStack.Generic import EndOfResponse

class HandlerFactory:

    "A factory class creating WebStack dispatcher objects."

    def __init__(self, resource, authenticator=None, handle_errors=1):

        """
        Initialise the root application-specific 'resource' and optional
        'authenticator'. The optional 'handle_errors' parameter (if true) causes
        handlers to deal with uncaught exceptions cleanly.
        """

        self.webstack_resource = resource
        self.webstack_authenticator = authenticator
        self.handle_errors = handle_errors

    def __call__(self, request, client_address, server):

        "Act as a factory for the server objects."

        handler = Handler(request, client_address, server, self.webstack_resource,
            self.webstack_authenticator, self.handle_errors)
        return handler

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    "A class dispatching requests to WebStack resources."

    def __init__(self, request, client_address, server, resource, authenticator, handle_errors):

        """
        Initialise the root application-specific 'resource' and 'authenticator'.
        Where 'handle_errors' is true, uncaught exceptions are dealt with by the
        handler.
        """

        self.webstack_resource = resource
        self.webstack_authenticator = authenticator
        self.handle_errors = handle_errors
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def handle(self):

        "Dispatch the request to the root application-specific resource."

        # NOTE: Overriding and trimming back the method's functionality.

        self.raw_requestline = self.rfile.readline()
        if not self.parse_request(): # An error code has been sent, just exit
            return

        trans = WebStack.BaseHTTPRequestHandler.Transaction(self)
        if self.webstack_authenticator is None or self.webstack_authenticator.authenticate(trans):
            try:
                self.webstack_resource.respond(trans)
            except EndOfResponse:
                pass
            except:
                if self.handle_errors:
                    trans.set_response_code(500) # Internal error
                else:
                    raise
        else:
            trans.set_response_code(401) # Unauthorized
            trans.set_header_value("WWW-Authenticate", '%s realm="%s"' % (
                self.webstack_authenticator.get_auth_type(), self.webstack_authenticator.get_realm()))

        trans.commit()

default_address = ("", 8080)

def deploy(resource, authenticator=None, address=None, handle_errors=1):

    """
    Deploy the given 'resource', with the given optional 'authenticator', at the
    given optional 'address', where 'address' is a 2-tuple of the form
    (host_string, port_integer).

    The optional 'handle_errors' flag (true by default) specifies whether error
    conditions are handled gracefully.
    """

    handler = HandlerFactory(resource, authenticator, handle_errors)
    server = BaseHTTPServer.HTTPServer(address or default_address, handler)
    server.serve_forever()

# vim: tabstop=4 expandtab shiftwidth=4

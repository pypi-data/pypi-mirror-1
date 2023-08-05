#!/usr/bin/env python

"""
BaseHTTPRequestHandler adapter.

Copyright (C) 2004, 2005, 2006 Paul Boddie <paul@boddie.org.uk>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import WebStack.BaseHTTPRequestHandler
import BaseHTTPServer
from WebStack.Generic import EndOfResponse
from WebStack.Adapters.Helpers.Error import ErrorResource

class HandlerFactory:

    "A factory class creating WebStack dispatcher objects."

    def __init__(self, resource, authenticator=None, handle_errors=1, error_resource=None):

        """
        Initialise the root application-specific 'resource' and optional
        'authenticator'. The optional 'handle_errors' parameter (if true) causes
        handlers to deal with uncaught exceptions cleanly, and the optional
        'error_resource' specifies an alternative error message generation
        resource.
        """

        self.webstack_resource = resource
        self.webstack_authenticator = authenticator
        self.handle_errors = handle_errors
        self.error_resource = error_resource or ErrorResource()

    def __call__(self, request, client_address, server):

        "Act as a factory for the server objects."

        handler = Handler(request, client_address, server, self.webstack_resource,
            self.webstack_authenticator, self.handle_errors, self.error_resource)
        return handler

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    "A class dispatching requests to WebStack resources."

    def __init__(self, request, client_address, server, resource, authenticator, handle_errors, error_resource):

        """
        Initialise the root application-specific 'resource' and 'authenticator'.
        Where 'handle_errors' is true, uncaught exceptions are dealt with by the
        handler and reported using the 'error_resource' provided.
        """

        self.webstack_resource = resource
        self.webstack_authenticator = authenticator
        self.handle_errors = handle_errors
        self.error_resource = error_resource
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def handle(self):

        "Dispatch the request to the root application-specific resource."

        # NOTE: Overriding and trimming back the method's functionality.

        self.raw_requestline = self.rfile.readline()
        if not self.parse_request(): # An error code has been sent, just exit
            return

        trans = WebStack.BaseHTTPRequestHandler.Transaction(self)
        try:
            if self.webstack_authenticator is None or self.webstack_authenticator.authenticate(trans):
                try:
                    self.webstack_resource.respond(trans)
                except EndOfResponse:
                    pass
                except:
                    if self.handle_errors:
                        trans.rollback()
                        trans.set_response_code(500) # Internal error
                        self.error_resource.respond(trans)
                    else:
                        raise
            else:
                trans.set_response_code(401) # Unauthorized
                trans.set_header_value("WWW-Authenticate", '%s realm="%s"' % (
                    self.webstack_authenticator.get_auth_type(), self.webstack_authenticator.get_realm()))

        finally:
            trans.commit()

default_address = ("", 8080)

def deploy(resource, authenticator=None, address=None, handle_errors=1, error_resource=None):

    """
    Deploy the given 'resource', with the given optional 'authenticator', at the
    given optional 'address', where 'address' is a 2-tuple of the form
    (host_string, port_integer).

    The optional 'handle_errors' flag (true by default) specifies whether error
    conditions are handled gracefully, and the optional 'error_resource'
    specifies an alternative error message generation resource, if desired.
    """

    handler = HandlerFactory(resource, authenticator, handle_errors, error_resource)
    server = BaseHTTPServer.HTTPServer(address or default_address, handler)
    server.serve_forever()

# vim: tabstop=4 expandtab shiftwidth=4

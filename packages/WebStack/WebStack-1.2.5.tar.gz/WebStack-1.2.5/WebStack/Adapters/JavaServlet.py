#!/usr/bin/env python

"""
Java Servlet adapter.

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

import WebStack.JavaServlet
from WebStack.Generic import EndOfResponse
from javax.servlet.http import HttpServlet

def deploy(resource, authenticator=None, address=None, handle_errors=1):

    """
    Deploy the given 'resource' and optional 'authenticator'.
    The optional 'handle_errors' flag, if set to false, causes tracebacks to be
    displayed in the browser.

    The optional 'address' parameter is deliberately ignored.
    """

    # NOTE: Since jython 2.1 does not support the nested scope mechanisms
    # NOTE: required to just drop the above parameters into methods even as
    # NOTE: default parameters, we employ class attributes.

    class _Deploy(HttpServlet):
        def __init__(self):
            HttpServlet.__init__(self)
            self.dispatcher = Dispatcher(self.resource, self.authenticator, self.handle_errors)

        def service(self, request, response):
            self.dispatcher.service(request, response)

    _Deploy.resource = resource
    _Deploy.authenticator = authenticator
    _Deploy.handle_errors = handle_errors

    return _Deploy

class Dispatcher:

    "A servlet helper class dispatching requests to WebStack resources."

    def __init__(self, resource, authenticator=None, handle_errors=1):

        """
        Initialise the root application-specific 'resource' and optional
        'authenticator'. The optional 'handle_errors' parameter (if true)
        causes handlers to deal with uncaught exceptions cleanly.
        """

        self.webstack_resource = resource
        self.webstack_authenticator = authenticator
        self.handle_errors = handle_errors

    def service(self, request, response):

        """
        Handle the 'request' and 'response' presented by the servlet.
        """

        trans = WebStack.JavaServlet.Transaction(request, response)
        try:
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
                #trans.set_header_value("WWW-Authenticate", '%s realm="%s"' % (
                #    self.webstack_authenticator.get_auth_type(), self.webstack_authenticator.get_realm()))

        finally:
            trans.commit()

# vim: tabstop=4 expandtab shiftwidth=4

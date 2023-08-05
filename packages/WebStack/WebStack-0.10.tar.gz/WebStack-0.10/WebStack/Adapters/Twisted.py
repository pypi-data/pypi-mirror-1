#!/usr/bin/env python

"""
Twisted adapter.

Copyright (C) 2004, 2005 Paul Boddie <paul@boddie.org.uk>

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
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
"""

import WebStack.Twisted
from WebStack.Generic import EndOfResponse
import twisted.web.resource
import twisted.web.server
import twisted.internet.reactor

class Dispatcher(twisted.web.resource.Resource):

    "A class dispatching requests to WebStack resources."

    isLeaf = 1

    def __init__(self, resource, authenticator=None, handle_errors=1):

        """
        Initialise the root application-specific 'resource' and optional
        'authenticator'. The optional 'handle_errors' parameter (if true) causes
        handlers to deal with uncaught exceptions cleanly.
        """

        twisted.web.resource.Resource.__init__(self)
        self.webstack_resource = resource
        self.webstack_authenticator = authenticator
        self.handle_errors = handle_errors

    def getChild(self, path, request):
        raise NotImplementedError, "getChild"

    def render(self, request):

        "Dispatch the given 'request' to the root application-specific resource."

        trans = WebStack.Twisted.Transaction(request)
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
        request.finish()
        return twisted.web.server.NOT_DONE_YET

default_address = ("", 8080)

def deploy(resource, authenticator=None, address=None, handle_errors=1):

    """
    Deploy the given 'resource', with the given optional 'authenticator', at the
    given optional 'address', where 'address' is a 2-tuple of the form
    (host_string, port_integer).

    NOTE: Twisted only makes use of the port number provided in the 'address'.

    The optional 'handle_errors' flag (true by default) specifies whether error
    conditions are handled gracefully.
    """

    address = address or default_address

    top_level = Dispatcher(resource, authenticator, handle_errors)
    site = twisted.web.server.Site(top_level)
    twisted.internet.reactor.listenTCP(address[1], site)
    twisted.internet.reactor.run()

# vim: tabstop=4 expandtab shiftwidth=4

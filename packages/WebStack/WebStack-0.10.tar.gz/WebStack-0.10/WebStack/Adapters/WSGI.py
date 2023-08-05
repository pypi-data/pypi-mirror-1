#!/usr/bin/env python

"""
WSGI adapter.

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

import WebStack.WSGI
from WebStack.Generic import EndOfResponse
from Helpers.wsgi_cgi import run_with_cgi

class WSGIAdapter:

    "A WSGI adapter class."

    def __init__(self, resource, authenticator=None, handle_errors=1):

        """
        Initialise the adapter with the given WebStack 'resource' and the
        optional 'authenticator'. The optional 'handle_errors' parameter (if
        true) causes handlers to deal with uncaught exceptions cleanly.
        """

        self.resource = resource
        self.authenticator = authenticator
        self.handle_errors = handle_errors

    def __call__(self, environ, start_response):

        """
        Dispatch to the root application-specific 'resource'. Return a list of
        strings comprising the response body text.
        """

        # NOTE: It would be best to give start_response to the transaction so
        # NOTE: that the underlying response's write method can be used by the
        # NOTE: transaction directly. Unfortunately, WebStack doesn't provide
        # NOTE: any means of declaring when the headers have been set and when
        # NOTE: response body output is the only thing to be subsequently
        # NOTE: produced.

        trans = WebStack.WSGI.Transaction(environ)

        try:
            if self.authenticator is None or self.authenticator.authenticate(trans):
                try:
                    self.resource.respond(trans)
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
                    self.authenticator.get_auth_type(), self.authenticator.get_realm()))
        finally:
            trans.commit()

        # NOTE: Provide sensible messages.
        # NOTE: Ignoring the write method returned by start_response.

        start_response(
            "%s WebStack status" % trans.get_response_code(),
            trans.get_wsgi_headers()
            )
        return [trans.get_wsgi_content()]

def deploy(resource, authenticator=None, address=None, handle_errors=1):

    """
    Deploy the given 'resource', with the given optional 'authenticator', at the
    given optional 'address', where 'address' is a 2-tuple of the form
    (host_string, port_integer).

    NOTE: The 'address' is ignored with the current WSGI implementation.

    The optional 'handle_errors' flag (true by default) specifies whether error
    conditions are handled gracefully.
    """

    handler = WSGIAdapter(resource, authenticator, handle_errors)
    run_with_cgi(handler)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"""
Java Servlet adapter.
"""

import WebStack.JavaServlet
from WebStack.Generic import EndOfResponse

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

        trans.commit()

# vim: tabstop=4 expandtab shiftwidth=4

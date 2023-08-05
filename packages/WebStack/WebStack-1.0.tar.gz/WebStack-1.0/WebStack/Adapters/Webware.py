#!/usr/bin/env python

"""
Webware adapter.

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
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import WebStack.Webware
from WebStack.Generic import EndOfResponse

# For Webware releases later than 0.8.1, employ special URLParsers in contexts
# for each application in the application server; such parsers create servlets
# instead of having servlet factories do that work.

try:
    from WebKit.URLParser import URLParser

except ImportError:

    # NOTE: Using Webware 0.8.1 or earlier. Assume that this really is the case.

    pass

else:
    class WebStackURLParser(URLParser):

        """
        A custom URL parser which provides access to application-specific resources.
        Override the 'parse' method for more precise control of servlet
        instantiation.
        """

        def __init__(self, resource, authenticator=None, handle_errors=1):

            """
            Initialise the parser object with the given root application-specific
            'resource' and optional 'authenticator'. The optional 'handle_errors'
            parameter (if true) causes handlers to deal with uncaught exceptions
            cleanly.
            """

            self.webstack_resource = resource
            self.webstack_authenticator = authenticator
            self.handle_errors = handle_errors

        def parse(self, trans, requestPath):

            """
            For the given Webware transaction, 'trans', override the usual servlet
            factory mechanism and return a servlet which will provide access to the
            application-specific resources.
            The 'trans' object - a Webware transaction - is not given to the servlet
            since such information is available when the 'respond' method is invoked
            on the servlet.
            The provided 'requestPath' object is not used, since this information
            should be available elsewhere.
            """

            return WebStackServlet(self.webstack_resource, self.webstack_authenticator,
                self.handle_errors)

# For Webware 0.8.1 and earlier, employ servlet factories and servlets.

from WebKit.ServletFactory import ServletFactory
from WebKit.Servlet import Servlet

class WebStackServletFactory(ServletFactory):

    """
    A servlet factory object producing servlets which provide access to
    application-specific resources.
    """

    def __init__(self, application, resource, file_extensions, authenticator=None, handle_errors=1):

        """
        Initialise the servlet factory with the Webware 'application' and the
        WebStack root application-specific 'resource'. The 'file_extensions'
        specified indicate for which files this factory is invoked. An optional
        'authenticator' is used to control access to the resource. The optional
        'handle_errors' parameter (if true) causes handlers to deal with
        uncaught exceptions cleanly.
        """

        ServletFactory.__init__(self, application)
        self.webstack_resource = resource
        self.file_extensions = file_extensions
        self.webstack_authenticator = authenticator
        self.handle_errors = handle_errors

    def uniqueness(self):

        """
        Return "file" uniqueness - probably the most appropriate response.
        """

        return "file"

    def extensions(self):

        """
        Return the file extensions supported by this factory.
        """

        return self.file_extensions

    def servletForTransaction(self, trans):

        """
        Return a servlet which will provide access to the application-specific
        resources. The 'trans' object - a Webware transaction - is not given to
        the servlet since such information is available when the 'respond'
        method is invoked on the servlet.
        """

        return WebStackServlet(self.webstack_resource, self.webstack_authenticator,
            self.handle_errors)

# Servlets are common to both solutions.

class WebStackServlet(Servlet):

    "A servlet which dispatches transactions to application-specific resources."

    def __init__(self, resource, authenticator, handle_errors):

        """
        Initialise the servlet with an application-specific 'resource' and
        'authenticator'. Where 'handle_errors' is true, uncaught exceptions are
        dealt with by the handler.
        """

        Servlet.__init__(self)
        self.webstack_resource = resource
        self.webstack_authenticator = authenticator
        self.handle_errors = handle_errors

    def respond(self, trans):

        """
        Respond to the incoming transaction, 'trans', by dispatching to the
        application-specific resource.
        """

        new_trans = WebStack.Webware.Transaction(trans)
        if self.webstack_authenticator is None or self.webstack_authenticator.authenticate(new_trans):
            try:
                self.webstack_resource.respond(new_trans)
            except EndOfResponse:
                pass
            except:
                if self.handle_errors:
                    new_trans.set_response_code(500) # Internal error
                else:
                    raise
        else:
            new_trans.set_response_code(401) # Unauthorized
            new_trans.set_header_value("WWW-Authenticate", '%s realm="%s"' % (
                self.webstack_authenticator.get_auth_type(), self.webstack_authenticator.get_realm()))

        new_trans.commit()

# vim: tabstop=4 expandtab shiftwidth=4

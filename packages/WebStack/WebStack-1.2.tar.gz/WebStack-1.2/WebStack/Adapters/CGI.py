#!/usr/bin/env python

"""
CGI adapter.

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

import WebStack.CGI
from WebStack.Generic import EndOfResponse
import sys, os
from WebStack.Adapters.Helpers.Error import ErrorResource

def deploy(resource, authenticator=None, input=None, output=None, env=None,
    address=None, handle_errors=1, error_resource=None):

    """
    Dispatch to the root application-specific 'resource'. Employ the optional
    'authenticator' to control access to the resource. If the optional 'input'
    stream, 'output' stream or environment 'env' are specified, use them instead
    of the defaults: standard input, standard output and the operating system
    environment respectively. Note that 'env' must evaluate to true for it to
    replace the default. The optional 'handle_errors' parameter (if true) causes
    handlers to deal with uncaught exceptions cleanly, and the optional
    'error_resource' specifies an alternative error message generation resource,
    if desired.

    The optional 'address' parameter is deliberately ignored.
    """

    error_resource = error_resource or ErrorResource()

    trans = WebStack.CGI.Transaction(input or sys.stdin, output or sys.stdout,
        env or os.environ)

    try:
        if authenticator is None or authenticator.authenticate(trans):
            try:
                resource.respond(trans)
            except EndOfResponse:
                pass
            except:
                if handle_errors:
                    trans.rollback()
                    trans.set_response_code(500) # Internal error
                    error_resource.respond(trans)
                else:
                    raise
        else:
            trans.set_response_code(401) # Unauthorized
            trans.set_header_value("WWW-Authenticate", '%s realm="%s"' % (
                authenticator.get_auth_type(), authenticator.get_realm()))
    finally:
        trans.commit()

# vim: tabstop=4 expandtab shiftwidth=4

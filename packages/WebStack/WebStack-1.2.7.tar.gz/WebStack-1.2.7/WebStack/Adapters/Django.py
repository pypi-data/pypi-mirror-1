#!/usr/bin/env python

"""
Django adapter.

Copyright (C) 2006 Paul Boddie <paul@boddie.org.uk>

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

import WebStack.Django
from WebStack.Generic import EndOfResponse
from WebStack.Adapters.Helpers.Error import ErrorResource

def deploy(resource, authenticator=None, address=None, handle_errors=1, error_resource=None):

    """
    Deploy the given 'resource', employing the optional 'authenticator' to
    protect it. The optional 'handle_errors' parameter (if true) causes handlers
    to deal with uncaught exceptions cleanly, and the optional 'error_resource'
    specifies an alternative error message generation resource, if desired.

    The optional 'address' parameter is deliberately ignored.
    """

    def _deploy(request, *args, **kw):
        return respond(request, resource, authenticator=authenticator,
            virtual_path_info=kw.get("vp"), handle_errors=handle_errors,
            error_resource=error_resource)
    return _deploy

def respond(request, resource, authenticator=None, virtual_path_info=None, handle_errors=1,
    error_resource=None):

    """
    Dispatch to the root application-specific 'resource'. Employ the optional
    'authenticator' to control access to the resource. Define the optional
    'virtual_path_info' as the path information considered to belong to the
    given 'resource'.

    The optional 'handle_errors' parameter (if true) causes handlers to deal
    with uncaught exceptions cleanly, and the optional 'error_resource'
    specifies an alternative error message generation resource.
    """

    error_resource = error_resource or ErrorResource()

    trans = WebStack.Django.Transaction(request)
    if virtual_path_info:
        trans.set_virtual_path_info(virtual_path_info)

    try:
        if authenticator is None or authenticator.authenticate(trans):
            try:
                resource.respond(trans)
            except EndOfResponse:
                pass
            except Exception, exc:
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
        return trans.response

# vim: tabstop=4 expandtab shiftwidth=4

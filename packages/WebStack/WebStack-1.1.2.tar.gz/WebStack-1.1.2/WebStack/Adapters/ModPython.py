#!/usr/bin/env python

"""
mod_python adapter.

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

import WebStack.ModPython
from WebStack.Generic import EndOfResponse
from mod_python import apache

def respond(request, resource, handle_errors=1):

    """
    Dispatch the given 'request' to the root application-specific 'resource'.
    The optional 'handle_errors' flag, if set to false, causes tracebacks to be
    displayed in the browser.
    """

    trans = WebStack.ModPython.Transaction(request)

    # NOTE: Resource pooling may be appropriate.

    try:
        try:
            try:
                resource.respond(trans)
            except EndOfResponse:
                pass
            return trans.get_response_code()

        except:

            # NOTE: Error conditions should be investigated further, along with
            # NOTE: other response states.

            if handle_errors:
                return apache.HTTP_INTERNAL_SERVER_ERROR
            else:
                raise

    finally:
        trans.commit()

def authenticate(request, authenticator, handle_errors=1):

    """
    Dispatch the given 'request' to the application-specific 'authenticator'.
    The optional 'handle_errors' flag, if set to false, causes tracebacks to be
    displayed in the browser.
    """

    trans = WebStack.ModPython.Transaction(request)

    # NOTE: Resource pooling may be appropriate.
    # NOTE: Forbidden access is not yet considered here.

    try:
        if authenticator.authenticate(trans):
            return apache.OK
        else:
            return apache.HTTP_UNAUTHORIZED
    except:

        # NOTE: Error conditions should be investigated further, along with
        # NOTE: other response states.

        if handle_errors:
            return apache.HTTP_INTERNAL_SERVER_ERROR
        else:
            raise

# vim: tabstop=4 expandtab shiftwidth=4

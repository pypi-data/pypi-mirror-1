#!/usr/bin/env python

"""
mod_python adapter.
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
            resource.respond(trans)
        except EndOfResponse:
            pass
        trans.commit()
        return trans.get_response_code()
    except:

        # NOTE: Error conditions should be investigated further, along with
        # NOTE: other response states.

        if handle_errors:
            return apache.HTTP_INTERNAL_SERVER_ERROR
        else:
            raise

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

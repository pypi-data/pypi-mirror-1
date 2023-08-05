#!/usr/bin/env python

"""
Zope adapter.
"""

import WebStack.Zope
from WebStack.Generic import EndOfResponse

from Globals import Persistent
from OFS.SimpleItem import Item
from AccessControl import ClassSecurityInfo
import Acquisition
#from ZPublisher.HTTPResponse import status_reasons

class WebStackAdapterProduct(Persistent, Acquisition.Implicit, Item):

    "A WebStack adapter product superclass."

    security = ClassSecurityInfo()
    security.declareObjectProtected("View")
    security.declareProtected("View", "index_html")

    def __init__(self, id, resource, authenticator=None, handle_errors=1):

        """
        Initialise with an 'id', a WebStack 'resource', and an optional
        'authenticator'. The optional 'handle_errors' parameter (if true) causes
        handlers to deal with uncaught exceptions cleanly.
        """

        self.id = id
        self.webstack_resource = resource
        self.webstack_authenticator = authenticator
        self.handle_errors = handle_errors

    def __bobo_traverse__(self, request, entry_name):
        if entry_name == "index_html":
            return getattr(self, "index_html")
        return self

    def index_html(self, REQUEST=None):

        """
        Dispatch the given 'REQUEST' to the root application-specific WebStack
        resource.
        """

        # Provide the adapter so that "path info" can be determined correctly.

        if REQUEST is not None:
            trans = WebStack.Zope.Transaction(REQUEST, self)
        else:
            raise "Internal Error"

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
            #trans.set_header_value("WWW-Authenticate", '%s realm="%s"' % (
            #    self.webstack_authenticator.get_auth_type(), self.webstack_authenticator.get_realm()))
            raise "Unauthorized"

        trans.commit()
        #raise status_reasons[trans.get_response_code()]

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"""
Webware context for the Auth application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import WebStackURLParser
from Auth import AuthResource, AuthAuthenticator

# NOTE: Initialising a shared resource.

resource = AuthResource()
authenticator = AuthAuthenticator()
urlParser = WebStackURLParser(resource, authenticator)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
from Auth import AuthResource, AuthAuthenticator

print "Serving..."
deploy(AuthResource(), AuthAuthenticator(), handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

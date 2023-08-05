#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
from Auth import AuthResource, AuthAuthenticator

print "Serving..."
deploy(AuthResource(), AuthAuthenticator())

# vim: tabstop=4 expandtab shiftwidth=4

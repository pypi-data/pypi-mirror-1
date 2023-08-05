#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
from Cookies import CookiesResource

print "Serving..."
deploy(CookiesResource(), handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

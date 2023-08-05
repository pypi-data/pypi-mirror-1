#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
from Cookies import CookiesResource

print "Serving..."
deploy(CookiesResource())

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
from Simple import SimpleResource

# Special magic incantation.

print "Serving..."
deploy(SimpleResource())

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
from VerySimple import VerySimpleResource

# Special magic incantation.

print "Serving..."
deploy(VerySimpleResource(), handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

from WebStack.Adapters.Twisted import deploy
from Sessions import SessionsResource

print "Serving..."
deploy(SessionsResource())

# vim: tabstop=4 expandtab shiftwidth=4

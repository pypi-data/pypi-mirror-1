#!/usr/bin/env python

from WebStack.Adapters.Twisted import deploy
from Unicode import UnicodeResource

print "Serving..."
deploy(UnicodeResource(), handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

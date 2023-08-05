#!/usr/bin/env python

from WebStack.Adapters.Twisted import deploy
from Simple import SimpleResource

print "Serving..."
deploy(SimpleResource(), handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

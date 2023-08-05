#!/usr/bin/env python

from WebStack.Adapters.Twisted import deploy
from VerySimple import VerySimpleResource

print "Serving..."
deploy(VerySimpleResource(), handle_errors=1)

# vim: tabstop=4 expandtab shiftwidth=4

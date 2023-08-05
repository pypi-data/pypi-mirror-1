#!/usr/bin/env python

from WebStack.Adapters.Twisted import deploy
from Form import FormResource

print "Serving..."
deploy(FormResource(), handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

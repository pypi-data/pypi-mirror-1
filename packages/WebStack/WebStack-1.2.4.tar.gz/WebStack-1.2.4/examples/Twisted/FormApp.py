#!/usr/bin/env python

from WebStack.Adapters.Twisted import deploy
from Form import FormResource

print "Serving..."
deploy(FormResource())

# vim: tabstop=4 expandtab shiftwidth=4

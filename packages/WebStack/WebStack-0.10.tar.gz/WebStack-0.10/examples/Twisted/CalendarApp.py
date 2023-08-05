#!/usr/bin/env python

from WebStack.Adapters.Twisted import deploy
from Calendar import DirectoryResource

print "Serving..."
deploy(DirectoryResource())

# vim: tabstop=4 expandtab shiftwidth=4

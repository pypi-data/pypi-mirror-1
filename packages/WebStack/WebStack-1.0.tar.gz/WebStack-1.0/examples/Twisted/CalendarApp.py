#!/usr/bin/env python

from WebStack.Adapters.Twisted import deploy
from Calendar import CalendarResource

print "Serving..."
deploy(CalendarResource())

# vim: tabstop=4 expandtab shiftwidth=4

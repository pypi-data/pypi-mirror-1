#!/usr/bin/env python

from WebStack.Adapters.Twisted import deploy
from Calendar import CalendarResource

print "Serving..."

# Choose or customise one of the following if the example fails.

deploy(CalendarResource())
#deploy(CalendarResource("iso-8859-1"))

# vim: tabstop=4 expandtab shiftwidth=4

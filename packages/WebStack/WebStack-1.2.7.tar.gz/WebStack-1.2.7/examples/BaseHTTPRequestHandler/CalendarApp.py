#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
from Calendar import CalendarResource

print "Serving..."

# Choose or customise one of the following if the example fails.

deploy(CalendarResource(), handle_errors=0)
#deploy(CalendarResource("iso-8859-1"), handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

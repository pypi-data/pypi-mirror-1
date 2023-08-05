#!/usr/bin/env python

"""
Webware context for the Calendar application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import WebStackURLParser
from Calendar import CalendarResource

# NOTE: Initialising a shared resource.

resource = CalendarResource()
urlParser = WebStackURLParser(resource)

# vim: tabstop=4 expandtab shiftwidth=4

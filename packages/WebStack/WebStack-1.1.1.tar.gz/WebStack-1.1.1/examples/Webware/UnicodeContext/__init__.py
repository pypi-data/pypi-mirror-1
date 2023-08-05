#!/usr/bin/env python

"""
Webware context for the Unicode application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import WebStackURLParser
from Unicode import UnicodeResource

# NOTE: Initialising a shared resource.

resource = UnicodeResource()
urlParser = WebStackURLParser(resource)

# vim: tabstop=4 expandtab shiftwidth=4

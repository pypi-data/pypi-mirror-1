#!/usr/bin/env python

"""
Webware context for the VerySimple application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import WebStackURLParser
from VerySimple import VerySimpleResource

# NOTE: Initialising a shared resource.

resource = VerySimpleResource()
urlParser = WebStackURLParser(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"""
Webware context for the Unicode application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import deploy
from Unicode import UnicodeResource

# NOTE: Initialising a shared resource.

resource = UnicodeResource()
urlParser = deploy(resource, handle_errors=1)

# vim: tabstop=4 expandtab shiftwidth=4

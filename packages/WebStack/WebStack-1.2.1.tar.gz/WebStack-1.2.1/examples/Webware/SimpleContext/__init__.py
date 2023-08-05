#!/usr/bin/env python

"""
Webware context for the Simple application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import deploy
from Simple import SimpleResource

# NOTE: Initialising a shared resource.

resource = SimpleResource()
urlParser = deploy(resource, handle_errors=1)

# vim: tabstop=4 expandtab shiftwidth=4

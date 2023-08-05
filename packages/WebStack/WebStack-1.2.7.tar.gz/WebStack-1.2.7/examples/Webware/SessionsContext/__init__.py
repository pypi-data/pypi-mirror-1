#!/usr/bin/env python

"""
Webware context for the Sessions application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import deploy
from Sessions import SessionsResource

# NOTE: Initialising a shared resource.

resource = SessionsResource()
urlParser = deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

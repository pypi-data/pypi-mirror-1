#!/usr/bin/env python

"""
Webware context for the Cookies application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import deploy
from Cookies import CookiesResource

# NOTE: Initialising a shared resource.

resource = CookiesResource()
urlParser = deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

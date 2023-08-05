#!/usr/bin/env python

"""
Webware context for the Cookies application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import WebStackURLParser
from Cookies import CookiesResource

# NOTE: Initialising a shared resource.

resource = CookiesResource()
urlParser = WebStackURLParser(resource)

# vim: tabstop=4 expandtab shiftwidth=4

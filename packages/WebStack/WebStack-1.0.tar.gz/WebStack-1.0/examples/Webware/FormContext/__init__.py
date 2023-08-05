#!/usr/bin/env python

"""
Webware context for the Form application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import WebStackURLParser
from Form import FormResource

# NOTE: Initialising a shared resource.

resource = FormResource()
urlParser = WebStackURLParser(resource)

# vim: tabstop=4 expandtab shiftwidth=4

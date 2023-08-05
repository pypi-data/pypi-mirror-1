#!/usr/bin/env python

"""
Webware context for the Form application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import deploy
from Form import FormResource

# NOTE: Initialising a shared resource.

resource = FormResource()
urlParser = deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

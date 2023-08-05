#!/usr/bin/env python

"""
Webware plug-in code.
"""

__version__ = "0.1"

from WebStack.Adapters.Webware import WebStackServletFactory
from Calendar import CalendarResource

# NOTE: Initialising a shared resource.

resource = CalendarResource()

def InstallInWebKit(appServer):
    global resource
    app = appServer.application()
    app.addServletFactory(WebStackServletFactory(app, resource, [".cal"]))

# vim: tabstop=4 expandtab shiftwidth=4

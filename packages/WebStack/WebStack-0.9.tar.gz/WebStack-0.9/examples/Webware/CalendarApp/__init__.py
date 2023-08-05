#!/usr/bin/env python

"""
Webware plug-in code.
"""

__version__ = "0.1"

from WebStack.Adapters.Webware import WebStackServletFactory
from Calendar import DirectoryResource

# NOTE: Initialising a shared resource.

resource = DirectoryResource()

def InstallInWebKit(appServer):
    global resource
    app = appServer.application()
    app.addServletFactory(WebStackServletFactory(app, resource, [".ics"]))

# vim: tabstop=4 expandtab shiftwidth=4

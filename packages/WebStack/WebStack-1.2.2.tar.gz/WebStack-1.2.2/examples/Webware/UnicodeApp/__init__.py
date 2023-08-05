#!/usr/bin/env python

"""
Webware plug-in code.
"""

__version__ = "0.1"

from WebStack.Adapters.Webware import WebStackServletFactory
from Unicode import UnicodeResource

# NOTE: Initialising a shared resource.

resource = UnicodeResource()

def InstallInWebKit(appServer):
    global resource, authenticator
    app = appServer.application()

    # NOTE: Allow .unicode files only. Really, we'd like any kind of file, but
    # NOTE: that would severely undermine the servlet factory concept.

    app.addServletFactory(WebStackServletFactory(app, resource, [".unicode"]))

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"""
Webware plug-in code.
"""

__version__ = "0.1"

from WebStack.Adapters.Webware import WebStackServletFactory
from Auth import AuthResource, AuthAuthenticator

# NOTE: Initialising a shared resource.

resource = AuthResource()
authenticator = AuthAuthenticator()

def InstallInWebKit(appServer):
    global resource, authenticator
    app = appServer.application()

    # NOTE: Allow .auth files only. Really, we'd like any kind of file, but
    # NOTE: that would severely undermine the servlet factory concept.

    app.addServletFactory(WebStackServletFactory(app, resource, [".auth"], authenticator))

# vim: tabstop=4 expandtab shiftwidth=4

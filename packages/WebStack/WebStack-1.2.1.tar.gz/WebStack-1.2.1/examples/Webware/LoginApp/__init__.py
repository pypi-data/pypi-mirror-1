#!/usr/bin/env python

"""
Webware plug-in code.
"""

__version__ = "0.1"

from WebStack.Adapters.Webware import WebStackServletFactory
from WebStack.Resources.Login import LoginResource, LoginAuthenticator

# NOTE: Initialising a shared resource.

resource = LoginResource(
    LoginAuthenticator(
        secret_key="horses",
        credentials=(
            ("badger", "abc"),
            ("vole", "xyz"),
        )
    )
)

def InstallInWebKit(appServer):
    global resource
    app = appServer.application()

    # NOTE: Allow .login files only. Really, we'd like any kind of file, but
    # NOTE: that would severely undermine the servlet factory concept.

    app.addServletFactory(WebStackServletFactory(app, resource, [".login"]))

# vim: tabstop=4 expandtab shiftwidth=4

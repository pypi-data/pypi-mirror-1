#!/usr/bin/env python

"""
Webware plug-in code.
"""

__version__ = "0.1"

from WebStack.Adapters.Webware import WebStackServletFactory
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from Simple import SimpleResource

# NOTE: Initialising a shared resource.

resource = LoginRedirectResource(
    login_url="http://localhost/webkit/app.login",
    app_url="http://localhost",
    resource=SimpleResource(),
    authenticator=LoginRedirectAuthenticator(secret_key="horses"),
    anonymous_parameter_name="anonymous",
    logout_parameter_name="logout"
)

def InstallInWebKit(appServer):
    global resource
    app = appServer.application()

    # NOTE: Allow .simplewithlogin files only. Really, we'd like any kind of
    # NOTE: file, but that would severely undermine the servlet factory concept.

    app.addServletFactory(WebStackServletFactory(app, resource, [".simplewithlogin"]))

# vim: tabstop=4 expandtab shiftwidth=4

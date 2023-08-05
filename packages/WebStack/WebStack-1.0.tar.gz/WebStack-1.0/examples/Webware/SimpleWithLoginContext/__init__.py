#!/usr/bin/env python

"""
Webware context for the Simple application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import WebStackURLParser
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from Simple import SimpleResource

# NOTE: Initialising a shared resource.

resource = LoginRedirectResource(
    login_url="http://localhost/webkitcvs/login",
    app_url="http://localhost",
    resource=SimpleResource(),
    authenticator=LoginRedirectAuthenticator(secret_key="horses"),
    anonymous_parameter_name="anonymous",
    logout_parameter_name="logout"
)
urlParser = WebStackURLParser(resource)

# vim: tabstop=4 expandtab shiftwidth=4

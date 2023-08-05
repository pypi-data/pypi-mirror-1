#!/usr/bin/env python

from WebStack.Adapters.JavaServlet import deploy
from Simple import SimpleResource
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator

# NOTE: Not sure if the resource should be maintained in a resource pool.

resource = LoginRedirectResource(
    login_url="http://localhost:8080/LoginApp/",
    app_url="http://localhost:8080",
    resource=SimpleResource(),
    authenticator=LoginRedirectAuthenticator(secret_key="horses"),
    anonymous_parameter_name="anonymous",
    logout_parameter_name="logout"
    )

SimpleWithLoginApp = deploy(resource)

# vim: tabstop=4 expandtab shiftwidth=4

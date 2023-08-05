#!/usr/bin/env python

from WebStack.Adapters.Twisted import deploy
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from Simple import SimpleResource

print "Serving..."
deploy(
    LoginRedirectResource(
        login_url="http://localhost:8081",
        app_url="http://localhost:8080",
        resource=SimpleResource(),
        authenticator=LoginRedirectAuthenticator(secret_key="horses"),
        anonymous_parameter_name="anonymous",
        logout_parameter_name="logout"
    )
)

# vim: tabstop=4 expandtab shiftwidth=4

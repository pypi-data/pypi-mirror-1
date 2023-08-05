#!/usr/bin/env python

from WebStack.Adapters.Django import deploy
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from Simple import SimpleResource

resource = LoginRedirectResource(
    login_url="http://localhost:8080/django/webstack/login",
    app_url="http://localhost:8080",
    resource=SimpleResource(),
    authenticator=LoginRedirectAuthenticator(secret_key="horses"),
    anonymous_parameter_name="anonymous",
    logout_parameter_name="logout",
    use_logout_redirect=0
)

simplewithlogin = deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

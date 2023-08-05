#!/usr/bin/env python

"""
Webware context for the Simple application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import deploy
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from WebStack.Resources.Login import LoginResource, LoginAuthenticator
from WebStack.Resources.ResourceMap import MapResource
from Simple import SimpleResource

# NOTE: Initialising a shared resource.

resource = MapResource({
    "simple" :
        LoginRedirectResource(
            login_url="http://localhost:9080/simplewithlogin/login",
            app_url="http://localhost:9080",
            resource=SimpleResource(),
            authenticator=LoginRedirectAuthenticator(secret_key="horses"),
            anonymous_parameter_name="anonymous",
            logout_parameter_name="logout"
        ),
    "login" :
        LoginResource(
            LoginAuthenticator(
                secret_key="horses",
                credentials=(
                    ("badger", "abc"),
                    ("vole", "xyz"),
                )
            )
        )
    })

urlParser = deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

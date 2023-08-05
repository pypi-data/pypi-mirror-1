#!/usr/bin/env python

from WebStack.Adapters.Twisted import deploy
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from WebStack.Resources.Login import LoginResource, LoginAuthenticator
from WebStack.Resources.ResourceMap import MapResource
from Simple import SimpleResource

print "Serving..."
deploy(
    MapResource({
        "simple" :
            LoginRedirectResource(
                login_url="http://localhost:8080/login",
                app_url="http://localhost:8080",
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
        }),
    handle_errors=1
)

# vim: tabstop=4 expandtab shiftwidth=4

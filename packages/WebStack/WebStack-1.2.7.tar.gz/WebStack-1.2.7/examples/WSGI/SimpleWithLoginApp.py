#!/usr/bin/env python

# Uncomment and adjust the paths below if WebStack is not installed somewhere
# on the PYTHONPATH.

#import sys
#sys.path.append("/home/paulb/Software/Python/WebStack")
#sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters.WSGI import deploy_with_wsgiref as deploy
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from WebStack.Resources.Login import LoginResource, LoginAuthenticator
from WebStack.Resources.ResourceMap import MapResource
from Simple import SimpleResource

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
    handle_errors=0
)

# vim: tabstop=4 expandtab shiftwidth=4

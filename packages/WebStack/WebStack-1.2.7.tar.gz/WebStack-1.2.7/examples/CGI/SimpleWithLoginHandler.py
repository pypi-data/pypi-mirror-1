#!/usr/bin/env python

# Uncomment and adjust the paths below if WebStack is not installed somewhere
# on the PYTHONPATH.

#import sys
#sys.path.append("/home/paulb/Software/Python/WebStack")
#sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters.CGI import deploy
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from WebStack.Resources.Login import LoginResource, LoginAuthenticator
from WebStack.Resources.ResourceMap import MapResource
from Simple import SimpleResource

deploy(
    MapResource({
        "simple" :
            LoginRedirectResource(
                login_url="http://localhost/cgi/login", # Change this to be the exact URL on your server.
                                                        # eg. http://localhost:8000/cgi/LoginHandler.py
                app_url="http://localhost",             # Change this to be the URL base for your server.
                                                        # eg. http://localhost:8000
                                                        # Note that the login application can be placed on
                                                        # a different server if desirable.
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

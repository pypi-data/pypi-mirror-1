#!/usr/bin/env python

# NOTE: Path manipulation requires manual customisation.

import sys
sys.path.append("/home/paulb/Software/Python/WebStack")
sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters.CGI import deploy
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from Simple import SimpleResource

deploy(
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
    handle_errors=1
)

# vim: tabstop=4 expandtab shiftwidth=4

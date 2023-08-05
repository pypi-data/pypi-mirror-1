#!/usr/bin/env python

# NOTE: Path manipulation requires manual customisation.

import sys
sys.path.append("/home/paulb/Software/Python/WebStack")
sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters.WSGI import deploy
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from Simple import SimpleResource

deploy(
    LoginRedirectResource(
        login_url="http://localhost/wsgi/login",
        app_url="http://localhost",
        resource=SimpleResource(),
        authenticator=LoginRedirectAuthenticator(secret_key="horses"),
        anonymous_parameter_name="anonymous",
        logout_parameter_name="logout"
    )
)

# vim: tabstop=4 expandtab shiftwidth=4

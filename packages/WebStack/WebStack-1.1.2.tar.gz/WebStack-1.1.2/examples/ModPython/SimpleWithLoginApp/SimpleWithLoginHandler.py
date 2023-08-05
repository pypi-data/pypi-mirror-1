#!/usr/bin/env python

# NOTE: Path manipulation requires manual customisation.

import sys
sys.path.append("/home/paulb/Software/Python/WebStack")
sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters import ModPython
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from Simple import SimpleResource

# NOTE: Not sure if the resource should be maintained in a resource pool.

resource = LoginRedirectResource(
    login_url="http://localhost/login/app.login",
    app_url="http://localhost",
    resource=SimpleResource(),
    authenticator=LoginRedirectAuthenticator(secret_key="horses"),
    anonymous_parameter_name="anonymous",
    logout_parameter_name="logout",
    use_logout_redirect=0
)

def handler(req):
    global resource
    return ModPython.respond(req, resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

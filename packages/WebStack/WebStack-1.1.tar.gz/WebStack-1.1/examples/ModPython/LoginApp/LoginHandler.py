#!/usr/bin/env python

# NOTE: Path manipulation requires manual customisation.

import sys
sys.path.append("/home/paulb/Software/Python/WebStack")
sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters import ModPython
from WebStack.Resources.Login import LoginResource, LoginAuthenticator

# NOTE: Not sure if the resource should be maintained in a resource pool.

resource = LoginResource(
    LoginAuthenticator(
        secret_key="horses",
        credentials=(
            ("badger", "abc"),
            ("vole", "xyz"),
        )
    ),
    use_redirect=0
)

def handler(req):
    global resource
    return ModPython.respond(req, resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

# NOTE: Path manipulation requires manual customisation.

import sys
sys.path.append("/home/paulb/Software/Python/WebStack")
sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters import ModPython
from Auth import AuthResource, AuthAuthenticator

# NOTE: Not sure if the resource should be maintained in a resource pool.

resource = AuthResource()
authenticator = AuthAuthenticator()

def handler(req):
    global resource
    return ModPython.respond(req, resource, handle_errors=0)

def authenhandler(req):
    global authenticator
    return ModPython.authenticate(req, authenticator, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

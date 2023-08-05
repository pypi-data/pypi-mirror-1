#!/usr/bin/env python

# NOTE: Path manipulation may require manual customisation.

import sys, os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../../Common")))

from WebStack.Adapters.ModPython import deploy
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

handler, _no_authentication = deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

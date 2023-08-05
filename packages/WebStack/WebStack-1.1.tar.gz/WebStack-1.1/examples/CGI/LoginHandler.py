#!/usr/bin/env python

# NOTE: Path manipulation requires manual customisation.

import sys
sys.path.append("/home/paulb/Software/Python/WebStack")
sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters.CGI import deploy
from WebStack.Resources.Login import LoginResource, LoginAuthenticator

deploy(
    LoginResource(
        LoginAuthenticator(
            secret_key="horses",
            credentials=(
                ("badger", "abc"),
                ("vole", "xyz"),
            )
        )
    ),
    handle_errors=1
)

# vim: tabstop=4 expandtab shiftwidth=4

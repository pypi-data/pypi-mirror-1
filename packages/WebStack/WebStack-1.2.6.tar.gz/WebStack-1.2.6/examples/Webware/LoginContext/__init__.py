#!/usr/bin/env python

"""
Webware context for the Login application (post Webware 0.8.1).
"""

from WebStack.Adapters.Webware import deploy
from WebStack.Resources.Login import LoginResource, LoginAuthenticator

# NOTE: Initialising a shared resource.

resource = LoginResource(
    LoginAuthenticator(
        secret_key="horses",
        credentials=(
            ("badger", "abc"),
            ("vole", "xyz"),
        )
    )
)

urlParser = deploy(resource, handle_errors=1)

# vim: tabstop=4 expandtab shiftwidth=4

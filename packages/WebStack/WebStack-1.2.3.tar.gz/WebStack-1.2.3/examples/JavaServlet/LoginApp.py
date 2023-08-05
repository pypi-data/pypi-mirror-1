#!/usr/bin/env python

from WebStack.Adapters.JavaServlet import deploy
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

LoginApp = deploy(resource)

# vim: tabstop=4 expandtab shiftwidth=4

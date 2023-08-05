#!/usr/bin/env python

from WebStack.Adapters.Django import deploy
from WebStack.Resources.Login import LoginResource, LoginAuthenticator

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

login = deploy(resource, handle_errors=1)

# vim: tabstop=4 expandtab shiftwidth=4

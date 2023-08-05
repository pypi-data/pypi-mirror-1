#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
from WebStack.Resources.Login import LoginResource, LoginAuthenticator

print "Serving..."
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
    address=("", 8081),
    handle_errors=1
)

# vim: tabstop=4 expandtab shiftwidth=4

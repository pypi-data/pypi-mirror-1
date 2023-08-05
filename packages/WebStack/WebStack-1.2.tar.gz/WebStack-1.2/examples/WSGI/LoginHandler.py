#!/usr/bin/env python

# Uncomment and adjust the paths below if WebStack is not installed somewhere
# on the PYTHONPATH.

#import sys
#sys.path.append("/home/paulb/Software/Python/WebStack")
#sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters.WSGI import deploy
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
    )
)

# vim: tabstop=4 expandtab shiftwidth=4

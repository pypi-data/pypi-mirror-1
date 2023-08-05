#!/usr/bin/env python

from WebStack.Adapters.Django import deploy
from Auth import AuthResource, AuthAuthenticator

resource = AuthResource()
authenticator = AuthAuthenticator()

auth = deploy(resource, authenticator=authenticator, handle_errors=1)

# vim: tabstop=4 expandtab shiftwidth=4

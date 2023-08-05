#!/usr/bin/env python

from WebStack.Adapters.JavaServlet import deploy
from Auth import AuthResource, AuthAuthenticator

AuthApp = deploy(AuthResource(), AuthAuthenticator())

# vim: tabstop=4 expandtab shiftwidth=4

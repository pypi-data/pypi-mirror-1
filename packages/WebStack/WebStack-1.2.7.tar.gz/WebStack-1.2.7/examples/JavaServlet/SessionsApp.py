#!/usr/bin/env python

from WebStack.Adapters.JavaServlet import deploy
from Sessions import SessionsResource

SessionsApp = deploy(SessionsResource(), handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

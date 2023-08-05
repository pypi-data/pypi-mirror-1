#!/usr/bin/env python

from WebStack.Adapters.JavaServlet import deploy
from Simple import SimpleResource

SimpleApp = deploy(SimpleResource(), handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

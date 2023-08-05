#!/usr/bin/env python

from WebStack.Adapters.JavaServlet import deploy
from JSPTest import JSPTestResource

JSPTestApp = deploy(JSPTestResource(), handle_errors=0)
print "Deployed."

# vim: tabstop=4 expandtab shiftwidth=4

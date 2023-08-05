#!/usr/bin/env python

from WebStack.Adapters.JavaServlet import deploy
from Unicode import UnicodeResource

UnicodeApp = deploy(UnicodeResource())

# vim: tabstop=4 expandtab shiftwidth=4

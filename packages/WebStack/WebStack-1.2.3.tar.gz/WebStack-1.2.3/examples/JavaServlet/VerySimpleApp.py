#!/usr/bin/env python

from WebStack.Adapters.JavaServlet import deploy
from VerySimple import VerySimpleResource

VerySimpleApp = deploy(VerySimpleResource())

# vim: tabstop=4 expandtab shiftwidth=4

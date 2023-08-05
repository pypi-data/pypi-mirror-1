#!/usr/bin/env python

from WebStack.Adapters.JavaServlet import deploy
from Form import FormResource

FormApp = deploy(FormResource())

# vim: tabstop=4 expandtab shiftwidth=4

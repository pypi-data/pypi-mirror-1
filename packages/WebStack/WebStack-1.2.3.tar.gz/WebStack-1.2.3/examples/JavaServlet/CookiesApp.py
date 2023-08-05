#!/usr/bin/env python

from WebStack.Adapters.JavaServlet import deploy
from Cookies import CookiesResource

CookiesApp = deploy(CookiesResource())

# vim: tabstop=4 expandtab shiftwidth=4

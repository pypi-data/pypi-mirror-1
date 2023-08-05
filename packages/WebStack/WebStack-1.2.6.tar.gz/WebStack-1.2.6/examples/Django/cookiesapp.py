#!/usr/bin/env python

from WebStack.Adapters.Django import deploy
from Cookies import CookiesResource

resource = CookiesResource()

cookies = deploy(resource, handle_errors=1)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

from WebStack.Adapters.Django import deploy
from Form import FormResource

resource = FormResource()

form = deploy(resource, handle_errors=1)

# vim: tabstop=4 expandtab shiftwidth=4

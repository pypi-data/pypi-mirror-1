#!/usr/bin/env python

from WebStack.Adapters.Django import deploy
from VerySimple import VerySimpleResource

resource = VerySimpleResource()

verysimple = deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

from WebStack.Adapters.Django import deploy
from Simple import SimpleResource

resource = SimpleResource()

simple = deploy(resource)

# vim: tabstop=4 expandtab shiftwidth=4

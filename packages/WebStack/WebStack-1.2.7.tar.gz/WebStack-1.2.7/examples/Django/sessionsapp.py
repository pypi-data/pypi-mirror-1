#!/usr/bin/env python

from WebStack.Adapters.Django import deploy
from Sessions import SessionsResource

resource = SessionsResource()

sessions = deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

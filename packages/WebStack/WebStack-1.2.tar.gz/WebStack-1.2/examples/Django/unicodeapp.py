#!/usr/bin/env python

from WebStack.Adapters.Django import deploy
from Unicode import UnicodeResource

unicode = deploy(UnicodeResource(), handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

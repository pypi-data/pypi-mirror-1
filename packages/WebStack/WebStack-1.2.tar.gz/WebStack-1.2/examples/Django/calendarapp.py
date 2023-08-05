#!/usr/bin/env python

from WebStack.Adapters.Django import deploy
from Calendar import CalendarResource

# Choose or customise one of the following if the example fails.

resource = CalendarResource()
#resource = CalendarResource("iso-8859-1")

calendar = deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

from WebStack.Adapters.JavaServlet import deploy
from Calendar import CalendarResource

CalendarApp = deploy(CalendarResource(), handle_errors=0)
#CalendarApp = deploy(CalendarResource("iso-8859-1"), handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

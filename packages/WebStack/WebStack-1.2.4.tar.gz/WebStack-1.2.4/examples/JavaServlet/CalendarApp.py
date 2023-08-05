#!/usr/bin/env python

from WebStack.Adapters.JavaServlet import deploy
from Calendar import CalendarResource

CalendarApp = deploy(CalendarResource())
#CalendarApp = deploy(CalendarResource("iso-8859-1"))

# vim: tabstop=4 expandtab shiftwidth=4

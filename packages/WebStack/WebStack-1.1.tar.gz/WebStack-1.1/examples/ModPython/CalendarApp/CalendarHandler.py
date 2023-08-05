#!/usr/bin/env python

# NOTE: Path manipulation requires manual customisation.

import sys
sys.path.append("/home/paulb/Software/Python/WebStack")
sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters import ModPython
from Calendar import CalendarResource

# NOTE: Not sure if the resource should be maintained in a resource pool.
# Choose or customise one of the following if the example fails.

resource = CalendarResource()
#resource = CalendarResource("iso-8859-1")

def handler(req):
    global resource
    return ModPython.respond(req, resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

# Uncomment and adjust the paths below if WebStack is not installed somewhere
# on the PYTHONPATH.

#import sys
#sys.path.append("/home/paulb/Software/Python/WebStack")
#sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters.WSGI import deploy_as_cgi
from Calendar import CalendarResource

# Choose or customise one of the following if the example fails.

deploy_as_cgi(CalendarResource(), handle_errors=0)
#deploy_as_cgi(CalendarResource("iso-8859-1"), handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

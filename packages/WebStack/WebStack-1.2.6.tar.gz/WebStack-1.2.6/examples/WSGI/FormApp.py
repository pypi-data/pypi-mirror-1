#!/usr/bin/env python

# Uncomment and adjust the paths below if WebStack is not installed somewhere
# on the PYTHONPATH.

#import sys
#sys.path.append("/home/paulb/Software/Python/WebStack")
#sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters.WSGI import deploy_with_wsgiref as deploy
from Form import FormResource

deploy(FormResource())

# vim: tabstop=4 expandtab shiftwidth=4

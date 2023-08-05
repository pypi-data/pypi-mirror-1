#!/usr/bin/env python

# Uncomment and adjust the paths below if WebStack is not installed somewhere
# on the PYTHONPATH.

#import sys
#sys.path.append("/home/paulb/Software/Python/WebStack")
#sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters.CGI import deploy
from Cookies import CookiesResource

deploy(CookiesResource())

# vim: tabstop=4 expandtab shiftwidth=4

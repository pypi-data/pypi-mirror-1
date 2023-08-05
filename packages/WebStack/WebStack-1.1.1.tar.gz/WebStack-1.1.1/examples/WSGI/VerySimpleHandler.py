#!/usr/bin/env python

# NOTE: Path manipulation requires manual customisation.

import sys
sys.path.append("/home/paulb/Software/Python/WebStack")
sys.path.append("/home/paulb/Software/Python/WebStack/examples/Common")

from WebStack.Adapters.WSGI import deploy
from VerySimple import VerySimpleResource

deploy(VerySimpleResource())

# vim: tabstop=4 expandtab shiftwidth=4

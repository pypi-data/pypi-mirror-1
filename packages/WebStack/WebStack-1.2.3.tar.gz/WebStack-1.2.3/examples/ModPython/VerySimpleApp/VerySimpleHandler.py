#!/usr/bin/env python

# NOTE: Path manipulation may require manual customisation.

import sys, os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../../Common")))

from WebStack.Adapters.ModPython import deploy
from VerySimple import VerySimpleResource

# NOTE: Not sure if the resource should be maintained in a resource pool.

resource = VerySimpleResource()

handler, _no_authentication = deploy(resource, handle_errors=1)

# vim: tabstop=4 expandtab shiftwidth=4

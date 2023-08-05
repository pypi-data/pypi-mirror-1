#!/usr/bin/env python

# NOTE: Path manipulation may require manual customisation.

import sys, os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../../Common")))

from WebStack.Adapters.ModPython import deploy
from Simple import SimpleResource

# NOTE: Not sure if the resource should be maintained in a resource pool.

resource = SimpleResource()

handler, _no_authentication = deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

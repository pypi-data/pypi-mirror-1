#!/usr/bin/env python

"Start the demonstration program."

import os, sys

# Find out where WebStack's distribution directory is.

cwd = os.getcwd()
parts = os.path.split(cwd)
if parts[-1] == "tools":
    parts = parts[:-1]
base = os.path.join(*parts)

# Set up a sessions directory if necessary.

sessions = os.path.join(base, "WebStack-sessions")
if not os.path.exists(sessions):
    os.mkdir(sessions)

# Set up the environment and run the demo program.

os.environ["PYTHONPATH"] = "%s:%s" % (base, os.path.join(base, "examples", "Common"))
os.system("%s %s" % (sys.executable, os.path.join(base, "examples", "BaseHTTPRequestHandler", "DemoApp.py")))

# vim: tabstop=4 expandtab shiftwidth=4

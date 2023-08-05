#!/usr/bin/env python

"Start the demonstration program."

import os, sys

# Find out where WebStack's distribution directory is.

program = sys.argv[0]
cwd = os.path.split(program)[0]
parts = os.path.split(cwd)
if parts[-1] == "tools":
    parts = parts[:-1]
base = os.path.join(*parts)

# Set up the environment and obtain the demo resource.

sys.path.append(base)
sys.path.append(os.path.join(base, "examples", "Common"))

import DemoApp
resource = DemoApp.get_site()

# Try and open the application in a Web browser.
# The preferred module is Paul's desktop module:
# http://www.python.org/pypi/desktop

if "--nobrowser" not in sys.argv:
    print "Opening a browser to show the application."
    print "If this fails, specify --nobrowser to turn it off."
    try:
        import desktop
    except ImportError:
        import webbrowser as desktop

    desktop.open("http://localhost:8080")

# Special magic incantation to start the demo.

from WebStack.Adapters.BaseHTTPRequestHandler import deploy

# Or try other implementations...

#from WebStack.Adapters.WSGI import deploy_with_wsgiref as deploy
#from WebStack.Adapters.Twisted import deploy

print "Serving..."
deploy(resource, handle_errors=1)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"""
A demonstration of WebStack. This is a quick and dirty combination of an
adapter, employing lots of resources, and the index page resource.
"""

# Import the things which make the adapter code deploy the application.

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
from WebStack.Resources.ResourceMap import MapResource

# Here are all the test resources.

from Cookies import CookiesResource
from Form import FormResource
from Sessions import SessionsResource
from Simple import SimpleResource
from Unicode import UnicodeResource
from VerySimple import VerySimpleResource

# A very simple index page.

from WebStack.Generic import ContentType

class DemoResource:
    def respond(self, trans):
        trans.set_content_type(ContentType("text/html"))
        trans.get_response_stream().write("""
<html>
  <head>
    <title>WebStack Examples</title>
  </head>
  <body>
    <h1>WebStack Examples</h1>
    <p>Here are some of the examples supplied with WebStack:</p>
    <ul>
      <li><a href="cookies">Cookie information</a></li>
      <li><a href="form">Form tests</a></li>
      <li><a href="sessions">Session information</a></li>
      <li><a href="simple">Simple test</a></li>
      <li><a href="unicode">Unicode test</a></li>
      <li><a href="verysimple">Very simple test</a></li>
    </ul>
    <p>You can run all of the examples independently - see the documentation in
       the <code>docs</code> directory, especially the subdirectories for each
       of the server environments or frameworks, for details of how this is
       done.</p>
  </body>
</html>""")
        trans.set_response_code(200)

# Define the resource mapping.

resource = MapResource({
    "cookies" : CookiesResource(),
    "form" : FormResource(),
    "sessions" : SessionsResource(),
    "simple" : SimpleResource(),
    "unicode" : UnicodeResource(),
    "verysimple" : VerySimpleResource(),
    "" : DemoResource(),
    })

# Special magic incantation.

print "Serving..."
deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

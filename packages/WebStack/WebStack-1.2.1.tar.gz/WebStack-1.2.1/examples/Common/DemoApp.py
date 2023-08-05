#!/usr/bin/env python

"""
A demonstration of WebStack.
"""

# Import the things which make the resource work.

from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from WebStack.Resources.Login import LoginResource, LoginAuthenticator

# Here are all the test resources.

from Cookies import CookiesResource
from Form import FormResource
from Sessions import SessionsResource
from Simple import SimpleResource
from Unicode import UnicodeResource
from VerySimple import VerySimpleResource
from Calendar import CalendarResource

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
      <li><a href="simplewithlogin">Simple with login test</a></li>
      <li><a href="unicode">Unicode test</a></li>
      <li><a href="verysimple">Very simple test</a></li>
      <li><a href="webdav://localhost:8080/calendar/">Calendar store example</a> - <strong>requires a WebDAV-capable browser</strong><br />
          Copy calendar files into the directory, view them, delete them, and so on.</li>
    </ul>
    <p>You can run all of the examples independently - see the documentation in
       the <code>docs</code> directory, especially the subdirectories for each
       of the server environments or frameworks, for details of how this is
       done.</p>
  </body>
</html>""")
        trans.set_response_code(200)

def get_site():

    "Define the resource mapping."

    resource = MapResource({
        "cookies" : CookiesResource(),
        "form" : FormResource(),
        "sessions" : SessionsResource(),
        "simple" : SimpleResource(),
        "simplewithlogin" :
            LoginRedirectResource(
                login_url="http://localhost:8080/login",
                app_url="http://localhost:8080",
                resource=SimpleResource(),
                authenticator=LoginRedirectAuthenticator(secret_key="horses"),
                anonymous_parameter_name="anonymous",
                logout_parameter_name="logout"
            ),
        "login" :
            LoginResource(
                LoginAuthenticator(
                    secret_key="horses",
                    credentials=(
                        ("badger", "abc"),
                        ("vole", "xyz"),
                    )
                )
            ),
        "unicode" : UnicodeResource(),
        "verysimple" : VerySimpleResource(),
        "calendar" : CalendarResource(),
        "" : DemoResource()
        })

    # Uncomment the line below to test arbitrary depth URLs/paths.

    #resource.mapping[None] = resource
    return resource

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"A test of cookies."

import WebStack.Generic
import time

class CookiesResource:

    "A resource adding and removing cookies."

    def respond(self, trans):
        trans.set_content_type(WebStack.Generic.ContentType("text/html"))

        # Get the fields and choose an action.

        fields_from_path = trans.get_fields_from_path()
        path = trans.get_path_without_query()

        # If the "set method" form was used, set the new method.

        if fields_from_path.has_key("set"):
            method = (fields_from_path.get("method") or ["GET"])[0]
            message = "Form method set to %s." % method
            cookie_name = cookie_value = None

        # Otherwise, discover the incoming fields.

        else:
            if fields_from_path.has_key("add") or fields_from_path.has_key("delete"):
                fields = fields_from_path
                method = (fields.get("method") or ["GET"])[0]
            else:
                fields = trans.get_fields_from_body()
                method = (fields.get("method") or ["GET"])[0]

            cookie_name_list = fields.get("name") or ["test"]
            cookie_value_list = fields.get("value") or ["test"]
            cookie_path_list = fields.get("path") or ["/"]
            cookie_expires_list = fields.get("expires") or ["60"]

            cookie_name = cookie_name_list[0]
            cookie_value = cookie_value_list[0]
            cookie_path = cookie_path_list[0]
            cookie_expires = int(cookie_expires_list[0])

            message = "No action taken - use add or delete to change the cookies."

            if fields.has_key("add"):
                trans.set_cookie_value(
                    cookie_name,
                    cookie_value,
                    cookie_path,
                    time.time() + cookie_expires
                )
                message = "Cookie %s added!" % cookie_name

            elif fields.has_key("delete"):
                trans.delete_cookie(cookie_name)
                message = "Cookie %s deleted!" % cookie_name

        # Get some information.

        out = trans.get_response_stream()
        out.write("""
<html>
  <head>
    <title>Cookies Example</title>
  </head>
  <body>
    <h1>Cookies</h1>
    <p>%s</p>
    <ul>
      %s
    </ul>
    <h2>Method</h2>
    <form method="GET">
      <p>Method: <select name="method"><option value="GET" %s>GET</option><option value="POST" %s>POST</option></select></p>
      <p><input name="set" type="submit" value="Set method..."/></p>
    </form>
    <h2>Cookie</h2>
    <form method="%s" action="%s">
      <input name="method" type="hidden" value="%s"/>
      <p>Name specified: <input name="name" value="%s"/></p>
      <p>Value found: <input name="value" value="%s"/></p>
      <p>
        <input name="add" type="submit" value="Add..."/>
        <input name="delete" type="submit" value="Delete..."/>
        <input name="refresh" type="submit" value="Refresh..."/>
      </p>
    </form>
  </body>
</html>
""" % (
    message,
    self._format_cookies(trans.get_cookies()),
    self._is_selected(method == "GET"),
    self._is_selected(method == "POST"),
    method,
    path,
    method,
    cookie_name,
    cookie_value,
))

    def _format_cookies(self, d):
        return "".join([
            "<dt>%s</dt><dd>%s</dd>" % (key, value.value)
            for key, value in d.items()
        ])

    def _format_list(self, l):
        return "".join([
            "<li>%s</li>" % value
            for value in l
        ])

    def _is_selected(self, value):
        if value:
            return 'selected="selected"'
        else:
            return ""

# vim: tabstop=4 expandtab shiftwidth=4

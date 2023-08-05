#!/usr/bin/env python

"A test of sessions."

import WebStack.Generic

class SessionsResource:

    "A resource adding and expiring sessions."

    def respond(self, trans):
        trans.set_content_type(WebStack.Generic.ContentType("text/html"))

        # Get the fields and choose an action.

        fields = trans.get_fields_from_body()

        # Get the session, creating one if appropriate.

        create = fields.has_key("create")
        session = trans.get_session(create)
        message = "No action taken - use expire, add and delete to edit sessions."

        # If a session exists, perform editing operations.

        if session is not None:
            names = fields.get("name") or ["test"]
            values = fields.get("value") or ["test"]
            name = names[0]
            value = values[0]

            if fields.has_key("add"):
                session[name] = value
                message = "Attribute %s added!" % name

            elif fields.has_key("delete"):
                try:
                    del session[name]
                except KeyError:
                    pass
                message = "Attribute %s deleted!" % name

            elif fields.has_key("expire"):
                trans.expire_session()
                message = "Session expired!"
                session = None
        else:
            message = "No session present - use create to add one."

        # If a session exists, get its contents.

        if session is not None:
            session_items = session.items()
        else:
            session_items = []

        # Get some information.

        out = trans.get_response_stream()
        out.write("""
<html>
  <head>
    <title>Session Example</title>
  </head>
  <body>
    <h1>Session Details</h1>
    <p>%s</p>
    <dl>
      %s
    </dl>
    <h2>Session</h2>
    <form method="POST">
      <p>
        <input name="create" type="submit" value="Create..."/>
        <input name="expire" type="submit" value="Expire..."/>
      </p>
      <p>Name: <input name="name"/></p>
      <p>Value: <input name="value"/></p>
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
    self._format_attributes(session_items),
))

    def _format_attributes(self, items):
        return "".join([
            "<dt>%s</dt><dd>%s</dd>" % (key, value)
            for key, value in items
        ])

# vim: tabstop=4 expandtab shiftwidth=4

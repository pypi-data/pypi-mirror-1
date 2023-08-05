#!/usr/bin/env python

"A calendar application."

import WebStack.Generic
import time

class DirectoryResource:

    """
    A resource which handles incoming calendars and viewing requests.
    An arbitrary set of rules can be applied to determine what is to be done
    with a request, and in this case, the application appears as a directory of
    calendars, yet also accepts incoming calendars.
    """

    def respond(self, trans):

        """
        Examine the incoming request, either saving a calendar or displaying
        one.
        """

        # Remember uploaded calendars using a session.

        session = trans.get_session(create=1)

        # Determine the action to be taken.

        method = trans.get_request_method()

        # NOTE: Some frameworks do not pass in the content type.

        content_type = trans.get_content_type()

        # Handle uploads.

        if method == "PUT":

            # Get the last path component as the name of the calendar.
            # NOTE: This could be improved to permit hierarchical naming.

            calendar_name = trans.get_path_without_query().split("/")[-1]
            input = trans.get_request_stream()
            data = input.read()

            # Store the calendar in the session.

            session["calendar name"] = calendar_name
            session["media type"] = content_type.media_type
            session["calendar data"] = data
            session["calendar size"] = len(data)
            session["calendar time"] = time.strftime("%Y-%m-%dT%T")

        # Handle directory browsing.

        elif method == "PROPFIND":
            trans.set_response_code(207)
            trans.set_content_type(WebStack.Generic.ContentType("text/html"))
            out = trans.get_response_stream()
            out.write("""<?xml version="1.0"?>
<D:multistatus xmlns:D="DAV:">
""")

            if trans.get_path_info() == "/":
                out.write("""
  <D:response>
    <D:href>%s</D:href>
    <D:propstat>
      <D:prop>
        <D:creationdate>%s</D:creationdate>
        <D:displayname>%s</D:displayname>
        <D:resourcetype>
          <D:collection/>
        </D:resourcetype>
      </D:prop>
      <D:status>HTTP/1.1 200 OK</D:status>
    </D:propstat>
  </D:response>
""" % (trans.get_path_without_query(), time.strftime("%Y-%m-%dT%T"), trans.get_path_without_query()))

            if session.has_key("calendar name"):
                out.write("""
  <D:response>
    <D:href>%s%s</D:href>
    <D:propstat>
      <D:prop>
        <D:creationdate>%s</D:creationdate>
        <D:displayname>%s</D:displayname>
        <D:resourcetype/>
        <D:getcontenttype>%s</D:getcontenttype>
      </D:prop>
      <D:status>HTTP/1.1 200 OK</D:status>
    </D:propstat>
  </D:response>
""" % (trans.get_path_without_query(), session.get("calendar name"), session.get("calendar time") or time.strftime("%Y-%m-%dT%T"),
    session.get("calendar name"), session.get("media type") or ""))

            out.write("""
</D:multistatus>
""")

        # Handle downloads.

        elif method == "GET":
            trans.set_content_type(WebStack.Generic.ContentType("text/html"))
            out = trans.get_response_stream()
            out.write("""
<html>
  <head>
    <title>Last Uploaded Calendar</title>
  </head>
  <body>
    <h1>Calendar %s</h1>
    <p>Media type: %s</p>
    <p>Calendar size: %s</p>
    <pre>%s</pre>
  </body>
</html>
""" % (session.get("calendar name"), session.get("media type"), session.get("calendar size"),
    session.get("calendar data", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")))

        # Disallow other methods.

        else:
            trans.set_response_code(405)

# vim: tabstop=4 expandtab shiftwidth=4

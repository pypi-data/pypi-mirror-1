#!/usr/bin/env python

"A calendar application."

import WebStack.Generic
import time
import os, tempfile

class CalendarResource:

    """
    A resource which handles incoming calendars and viewing requests.
    An arbitrary set of rules can be applied to determine what is to be done
    with a request, and in this case, the application appears as a directory of
    calendars, yet also accepts incoming calendars.
    """

    resource_dir = os.path.join(os.path.split(__file__)[0], "calendars")
    encoding = "utf-8"

    def __init__(self):
        if not os.path.exists(self.resource_dir):
            try:
                os.mkdir(self.resource_dir)
            except OSError:
                self.resource_dir = os.path.join(tempfile.gettempdir(), "calendars")
                if not os.path.exists(self.resource_dir):
                    os.mkdir(self.resource_dir)

        if os.path.supports_unicode_filenames:
            self.fsencoding = None
        else:
            import locale
            self.fsencoding = locale.getdefaultlocale()[1]

    def _convert_name(self, name):
        if self.fsencoding:
            return name.encode(self.fsencoding)
        else:
            return name

    def _convert_fsname(self, name):
        if self.fsencoding:
            return unicode(name, self.fsencoding)
        else:
            return name

    def respond(self, trans):

        """
        Examine the incoming request, either saving a calendar or displaying
        one.
        """

        # Determine the action to be taken.

        method = trans.get_request_method()

        # NOTE: Some frameworks do not pass in the content type.
        # NOTE: We always assume that calendar files are being uploaded.

        calendar_name = trans.get_virtual_path_info(self.encoding).split("/")[-1]

        # Handle uploads.

        if method == "PUT":

            # Get the last path component as the name of the calendar.
            # NOTE: This could be improved to permit hierarchical naming.

            input = trans.get_request_stream()
            data = input.read()

            # Store the calendar in the directory.

            f = open(self._convert_name(os.path.join(self.resource_dir, calendar_name)), "wb")
            f.write(data)
            f.close()

        # Handle directory browsing.

        elif method == "PROPFIND":
            trans.set_response_code(207)
            trans.set_content_type(WebStack.Generic.ContentType("text/xml", self.encoding))
            out = trans.get_response_stream()
            out.write("""<?xml version="1.0"?>
<D:multistatus xmlns:D="DAV:">
""")

            if trans.get_virtual_path_info(self.encoding) == "/":
                time_now = time.strftime("%Y-%m-%dT%TZ", time.gmtime(time.time()))
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
""" % (
    trans.get_path_without_query(self.encoding),
    time_now,
    trans.get_path_without_query(self.encoding)))

            for filename in os.listdir(self.resource_dir):
                pathname = os.path.join(self.resource_dir, filename)
                created = time.strftime("%Y-%m-%dT%TZ", time.gmtime(os.path.getctime(pathname)))
                size = os.path.getsize(pathname)
                out.write("""
  <D:response>
    <D:href>%s%s</D:href>
    <D:propstat>
      <D:prop>
        <D:creationdate>%s</D:creationdate>
        <D:displayname>%s</D:displayname>
        <D:resourcetype/>
        <D:getcontenttype>%s</D:getcontenttype>
        <D:getcontentlength>%s</D:getcontentlength>
      </D:prop>
      <D:status>HTTP/1.1 200 OK</D:status>
    </D:propstat>
  </D:response>
""" % (
    trans.get_path_without_query(self.encoding),
    self._convert_fsname(filename),
    created,
    self._convert_fsname(filename),
    "text/calendar",
    size))

            out.write("""
</D:multistatus>
""")

        # Handle downloads.

        elif method == "GET":
            trans.set_content_type(WebStack.Generic.ContentType("text/calendar"))
            out = trans.get_response_stream()
            f = open(self._convert_name(os.path.join(self.resource_dir, calendar_name)))
            out.write(f.read())
            f.close()

        # Handle deletion.

        elif method == "DELETE":
            try:
                os.remove(os.path.join(self.resource_dir, calendar_name))
            except OSError:
                trans.set_response_code(500)

        # Handle renaming.

        elif method in ("MOVE", "COPY"):
            destinations = trans.get_header_values("Destination")
            if len(destinations) != 1:
                trans.set_response_code(500)
            else:
                try:
                    # Convert the URL into a filename.
                    # NOTE: Assume that the URL references the same "directory".

                    destination = destinations[0].split("/")[-1]
                    destination = trans.decode_path(destination, self.encoding)

                    if method == "MOVE":
                        os.rename(
                            self._convert_name(os.path.join(self.resource_dir, calendar_name)),
                            self._convert_name(os.path.join(self.resource_dir, destination))
                            )
                    elif method == "COPY":
                        f_old = open(self._convert_name(os.path.join(self.resource_dir, calendar_name)), "rb")
                        f_new = open(self._convert_name(os.path.join(self.resource_dir, destination)), "wb")
                        f_new.write(f_old.read())
                        f_new.close()
                        f_old.close()

                    # NOTE: We do not observe the rules regarding overwriting
                    # NOTE: and the appropriate status codes.

                    trans.set_header_value("Location", destinations[0])
                    trans.set_response_code(201)

                except OSError:
                    trans.set_response_code(500)

        # Disallow other methods.

        else:
            trans.set_response_code(405)

# vim: tabstop=4 expandtab shiftwidth=4

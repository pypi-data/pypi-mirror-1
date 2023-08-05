#!/usr/bin/env python

"A calendar application."

import WebStack.Generic
from WebStack.Repositories.Directory import DirectoryRepository
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

    dav_header = \
"""<?xml version="1.0"?>
<D:multistatus xmlns:D="DAV:">
"""
    propfind_header = \
"""<D:response>
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
"""
    propfind_item = \
"""<D:response>
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
"""
    propfind_footer = \
"""</D:multistatus>
"""

    def __init__(self, fsencoding=None):
        try:
            self.repository = DirectoryRepository(self.resource_dir, fsencoding)
        except OSError:
            self.resource_dir = os.path.join(tempfile.gettempdir(), "calendars")
            self.repository = DirectoryRepository(self.resource_dir, fsencoding)

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

            self.repository[calendar_name] = data

        # Handle directory browsing.

        elif method == "PROPFIND":
            trans.set_response_code(207)
            trans.set_content_type(WebStack.Generic.ContentType("text/xml", self.encoding))
            out = trans.get_response_stream()
            out.write(self.dav_header)

            if trans.get_virtual_path_info(self.encoding) == "/":
                time_now = time.strftime("%Y-%m-%dT%TZ", time.gmtime(time.time()))
                out.write(self.propfind_header % (
                    trans.get_path_without_query(self.encoding),
                    time_now,
                    trans.get_path_without_query(self.encoding)))

            for filename in self.repository.keys():
                pathname = self.repository.full_path(filename)
                created = time.strftime("%Y-%m-%dT%TZ", time.gmtime(os.path.getctime(pathname)))
                size = os.path.getsize(pathname)
                out.write(self.propfind_item % (
                    trans.get_path_without_query(self.encoding),
                    filename,
                    created,
                    filename,
                    "text/calendar",
                    size))

            out.write(self.propfind_footer)

        # Handle downloads.

        elif method == "GET":
            trans.set_content_type(WebStack.Generic.ContentType("text/calendar"))
            out = trans.get_response_stream()
            out.write(self.repository[calendar_name])

        # Handle deletion.

        elif method == "DELETE":
            try:
                del self.repository[calendar_name]
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

                    self.repository[destination] = self.repository[calendar_name]
                    if method == "MOVE":
                        del self.repository[calendar_name]

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

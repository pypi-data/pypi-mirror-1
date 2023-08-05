#!/usr/bin/env python

"A simple application for test purposes."

import WebStack.Generic

class SimpleResource:

    "A simple resource."

    def respond(self, trans):
        trans.set_content_type(WebStack.Generic.ContentType("text/html", "utf-8"))

        # Get some information.

        out = trans.get_response_stream()
        if trans.get_content_type():
            content_type = trans.get_content_type().media_type
            charset = trans.get_content_type().charset
        else:
            content_type, charset = None, None

        # Use Unicode strings for correct character encoding.

        out.write(u"""
<html>
  <head>
    <title>Simple Example</title>
  </head>
  <body>
    <h1>Test</h1>
    <ul>
      <li>Path: %s</li>
      <li>Path without query: %s</li>
      <li>Path info: %s</li>
      <li>Virtual path info: %s</li>
      <li>Processed virtual path info: %s</li>
      <li>Query string: %s</li>
      <li>Query string (decoded): %s</li>
      <li>Server name: %s</li>
      <li>Server port: %s</li>
      <li>Request method: %s</li>
      <li>User: %s</li>
      <li>Content type: %s</li>
      <li>Charset: %s</li>
      <li>Languages:
        <ul>
        %s
        </ul>
      </li>
      <li>Charsets:
        <ul>
        %s
        </ul>
      </li>
      <li>Headers:
        <dl>
        %s
        </dl>
      </li>
      <li>User-Agent:
        <ul>
        %s
        </ul>
      </li>
      <li>user-agent:
        <ul>
        %s
        </ul>
      </li>
      <li>Fields from path:
        <ul>
        %s
        </ul>
      </li>
      <li>Fields from path (explicit encoding):
        <ul>
        %s
        </ul>
      </li>
      <li>Fields from body:
        <ul>
        %s
        </ul>
      </li>
      <li>Fields from path and body:
        <ul>
        %s
        </ul>
      </li>
      <li>Cookies:
        <ul>
        %s
        </ul>
      </li>
    </ul>
  </body>
</html>
""" % (
    trans.get_path("utf-8"),
    trans.get_path_without_query("utf-8"),
    trans.get_path_info("utf-8"),
    trans.get_virtual_path_info("utf-8"),
    trans.get_processed_virtual_path_info("utf-8"),
    trans.get_query_string(),
    trans.decode_path(trans.get_query_string(), "utf-8"),
    trans.get_server_name(),
    trans.get_server_port(),
    trans.get_request_method(),
    trans.get_user(),
    content_type,
    charset,
    self._format_list(trans.get_content_languages()),
    self._format_list(trans.get_content_charsets()),
    self._format_dict(trans.get_headers()),
    self._format_list(trans.get_header_values("User-Agent")),
    self._format_list(trans.get_header_values("user-agent")),
    self._format_fields(trans.get_fields_from_path()),
    self._format_fields(trans.get_fields_from_path("utf-8")),
    self._format_fields(trans.get_fields_from_body()),
    self._format_fields(trans.get_fields("utf-8")),
    self._format_cookies(trans.get_cookies()),
))

    def _format_dict(self, d):
        return "".join([
            "<dt>%s</dt><dd>%s</dd>" % (key, value)
            for key, value in d.items()
        ])

    def _format_fields(self, d):
        return "".join([
            "<li>%s<ul>%s</ul></li>" % (key, self._format_list(value))
            for key, value in d.items()
        ])

    def _format_cookies(self, d):
        return "".join([
            "<dt>%s</dt><dd>%s</dd>" % (key, value.value)
            for key, value in d.items()
        ])

    def _format_list(self, l):
        return "".join([
            "<li>%s</li>" % (value or "<em>empty</em>")
            for value in l
        ])

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"A form submission test."

import WebStack.Generic

class FormResource:

    """
    A resource which handles incoming form submissions.
    """

    def respond(self, trans):

        """
        Examine the incoming request, decoding the form information.
        """

        # NOTE: Some frameworks do not pass in the content type.

        content_type = trans.get_content_type()
        if content_type:
            content_type_str = content_type.media_type
            content_type_charset = content_type.charset
        else:
            content_type_str = None
            content_type_charset = None

        # Optional encodings can be employed.

        fields_from_path = trans.get_fields_from_path()

        # Send the appropriate kind of response.

        if fields_from_path.has_key("charset"):
            charset = fields_from_path["charset"][0]
            trans.set_content_type(WebStack.Generic.ContentType("text/html", charset))
        elif content_type_charset:
            charset = content_type_charset
            trans.set_content_type(WebStack.Generic.ContentType("text/html", charset))
        else:
            charset = None
            trans.set_content_type(WebStack.Generic.ContentType("text/html"))

        # Handle charset issues.

        if charset:
            fields = trans.get_fields_from_body(charset)
            all_fields = trans.get_fields(charset)
        else:
            fields = trans.get_fields_from_body()
            all_fields = trans.get_fields()

        out = trans.get_response_stream()

        # Use Unicode for correct character encoding behaviour.

        out.write(u"""
<html>
  <head>
    <title>Form Test</title>
  </head>
  <body>
    <h1>Form Test</h1>
    <table border="1" cellspacing="0" cellpadding="5">
      <tr>
        <th>Normal</th>
        <th>Multipart</th>
      </tr>
      <tr>
        <td>
          <form method="post" action="">
            <input name="x" type="text" value="1"/><br/>
            <input name="x" type="text" value="2"/><br/>
            <input name="y" type="text" value="3"/><br/>
            <input name="f" type="file"/><br/>
            <input name="send" type="submit" value="Send!"/>
          </form>
        </td>
        <td>
          <form method="post" action="" enctype="multipart/form-data">
            <input name="x" type="text" value="1"/><br/>
            <input name="x" type="text" value="2"/><br/>
            <input name="y" type="text" value="3"/><br/>
            <input name="f" type="file"/><br/>
            <input name="send" type="submit" value="Send!"/>
          </form>
        </td>
      </tr>
      <tr>
        <th rowspan="2">Content Type</th>
        <th colspan="2">Charset</th>
      </tr>
      <tr>
        <th>From Content Type</th>
        <th>In Use</th>
      </tr>
      <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
      </tr>
      <tr>
        <th>Fields from Body</th>
        <th>Fields from Body and Path</th>
      </tr>
      <tr>
        <td>
          <ul>%s</ul>
        </td>
        <td>
          <ul>%s</ul>
        </td>
      </tr>
    </table>
  </body>
</html>
""" % (
            content_type_str,
            content_type_charset,
            charset,
            self._format_fields(fields),
            self._format_fields(all_fields),
        ))

    def _format_fields(self, d):
        return "".join([
            "<li>%s<ul>%s</ul></li>" % (key or "<em>empty</em>", self._format_list(value))
            for key, value in d.items()
        ])

    def _format_list(self, l):
        l2 = []
        for value in l:

            # Detect uploads.

            if type(value) not in (type(""), type(u"")):
                value = "%s: %s" % (value.headers.get("content-type") or "No content type", repr(str(value)))

            l2.append("<li>%s</li>" % (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") or "<em>empty</em>"))
        return "".join(l2)

# vim: tabstop=4 expandtab shiftwidth=4

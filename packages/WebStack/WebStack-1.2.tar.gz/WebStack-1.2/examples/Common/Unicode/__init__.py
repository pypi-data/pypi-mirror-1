#!/usr/bin/env python

"A test of Unicode writing."

import WebStack.Generic

class UnicodeResource:

    "A Unicode test resource."

    def respond(self, trans):
        trans.set_content_type(WebStack.Generic.ContentType("text/html", "utf-8"))

        # Define a Unicode sequence.

        l = []
        for i in range(0, 4096, 64):
            l.append("<tr>")
            l.append("<th>%s</th>" % i)
            for j in range(i, i+64):
                l.append("<td>%s</td>" % unichr(j))
            l.append("<tr>\n")
        s = "".join(l)

        # Write the Unicode to the response.

        out = trans.get_response_stream()
        out.write("""
<html>
  <head>
    <title>Unicode Example</title>
  </head>
  <body>
    <table>
      %s
    </table>
  </body>
</html>
""" % s)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"""
Standard error message output.

Copyright (C) 2006 Paul Boddie <paul@boddie.org.uk>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

from WebStack.Generic import ContentType

class ErrorResource:

    "An error resource which should not itself cause error conditions."

    def respond(self, trans):
        trans.set_content_type(ContentType("text/html"))
        out = trans.get_response_stream()
        out.write("""<html>
<head>
  <title>Error</title>
</head>
<body>
  <h1>Error</h1>
  <p>An error has occurred preventing the application from returning a response.</p>
</body>
</html>
""")

# vim: tabstop=4 expandtab shiftwidth=4

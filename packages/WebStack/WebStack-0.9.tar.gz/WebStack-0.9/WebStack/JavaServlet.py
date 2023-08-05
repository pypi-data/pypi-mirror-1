#!/usr/bin/env python

"""
Java Servlet classes.
"""

import Generic
from StringIO import StringIO
from Helpers.Request import Cookie, get_body_fields, get_storage_items, get_fields_from_query_string, filter_fields
import javax.servlet.http

# Form data decoding.

import javax.mail.internet
import javax.mail
import java.util
import java.net
from WebStack.Generic import HeaderValue

class Stream:

    """
    Wrapper around java.io.BufferedReader.
    """

    def __init__(self, stream):

        "Initialise the stream with the given underlying 'stream'."

        self.stream = stream

    def read(self):

        "Read the entire message, returning it as a string."

        characters = StringIO()
        while 1:
            c = self.stream.read()
            if c == -1:
                return characters.getvalue()
            else:
                characters.write(chr(c))

    def readline(self):

        "Read a line from the stream, returning it as a string."

        line = self.stream.readLine()
        if line is not None:
            return line + "\n"
        else:
            return ""

class Transaction(Generic.Transaction):

    """
    Java Servlet transaction interface.
    """

    def __init__(self, request, response):

        """
        Initialise the transaction using the Java Servlet HTTP 'request' and
        'response'.
        """

        self.request = request
        self.response = response
        self.status = None
        self.user = None
        self.path_info = None

        # Remember the cookies received in the request.
        # NOTE: Discarding much of the information received.

        self.cookies_in = {}
        for cookie in self.request.getCookies() or []:
            cookie_name = self.decode_cookie_value(cookie.getName())
            self.cookies_in[cookie_name] = Cookie(cookie_name, self.decode_cookie_value(cookie.getValue()))

        # Cached information.

        self.message_fields = None

    def commit(self):

        """
        A special method, synchronising the transaction with framework-specific
        objects.
        """

        self.get_response_stream().close()

    # Server-related methods.

    def get_server_name(self):

        "Returns the server name."

        return self.request.getServerName()

    def get_server_port(self):

        "Returns the server port as a string."

        return str(self.request.getServerPort())

    # Request-related methods.

    def get_request_stream(self):

        """
        Returns the request stream for the transaction.
        """

        return Stream(self.request.getReader())

    def get_request_method(self):

        """
        Returns the request method.
        """

        return self.request.getMethod()

    def get_headers(self):

        """
        Returns all request headers as a dictionary-like object mapping header
        names to values.

        NOTE: If duplicate header names are permitted, then this interface will
        NOTE: need to change.
        """

        headers = {}
        header_names_enum = self.request.getHeaderNames()
        while header_names_enum.hasMoreElements():

            # NOTE: Retrieve only a single value (not using getHeaders).

            header_name = header_names_enum.nextElement()
            headers[header_name] = self.request.getHeader(header_name)

        return headers

    def get_header_values(self, key):

        """
        Returns a list of all request header values associated with the given
        'key'. Note that according to RFC 2616, 'key' is treated as a
        case-insensitive string.
        """

        values = []
        headers_enum = self.request.getHeaders(key)
        while headers_enum.hasMoreElements():
            values.append(headers_enum.nextElement())
        return values

    def get_content_type(self):

        """
        Returns the content type specified on the request, along with the
        charset employed.
        """

        content_types = self.get_header_values("Content-Type") or []
        if len(content_types) >= 1:
            return self.parse_content_type(content_types[0])
        else:
            return None

    def get_content_charsets(self):

        """
        Returns the character set preferences.
        """

        accept_charsets = self.get_header_values("Accept-Charset") or []
        if len(accept_charsets) >= 1:
            return self.parse_content_preferences(accept_charsets[0])
        else:
            return None

    def get_content_languages(self):

        """
        Returns extracted language information from the transaction.
        """

        accept_languages = self.get_header_values("Accept-Language") or []
        if len(accept_languages) >= 1:
            return self.parse_content_preferences(accept_languages[0])
        else:
            return None

    def get_path(self):

        """
        Returns the entire path from the request.
        """

        # NOTE: To be verified.

        path = self.get_path_without_query()
        qs = self.get_query_string()
        if qs:
            path += "?"
            path += qs
        return path

    def get_path_without_query(self):

        """
        Returns the entire path from the request minus the query string.
        """

        return self.request.getContextPath() + self.request.getServletPath() + self.get_path_info()

    def get_path_info(self):

        """
        Returns the "path info" (the part of the URL after the resource name
        handling the current request) from the request.
        """

        return self.request.getPathInfo() or ""

    def get_query_string(self):

        """
        Returns the query string from the path in the request.
        """

        return self.request.getQueryString() or ""

    # Higher level request-related methods.

    def get_fields_from_path(self):

        """
        Extracts fields (or request parameters) from the path specified in the
        transaction. The underlying framework may refuse to supply fields from
        the path if handling a POST transaction.

        Returns a dictionary mapping field names to lists of values (even if a
        single value is associated with any given field name).
        """

        # There may not be a reliable means of extracting only the fields from
        # the path using the API. Moreover, any access to the request parameters
        # disrupts the proper extraction and decoding of the request parameters
        # which originated in the request body.

        return get_fields_from_query_string(self.get_query_string(), java.net.URLDecoder().decode)

    def get_fields_from_body(self, encoding=None):

        """
        Extracts fields (or request parameters) from the message body in the
        transaction. The optional 'encoding' parameter specifies the character
        encoding of the message body for cases where no such information is
        available, but where the default encoding is to be overridden.

        Returns a dictionary mapping field names to lists of values (even if a
        single value is associated with any given field name). Each value is
        either a Unicode object (representing a simple form field, for example)
        or a plain string (representing a file upload form field, for example).
        """

        # There may not be a reliable means of extracting only the fields
        # the message body using the API. Remove fields originating from the
        # path in the mixture provided by the API.

        all_fields = self._get_fields(encoding)
        fields_from_path = self.get_fields_from_path()
        return filter_fields(all_fields, fields_from_path)

    def _get_fields(self, encoding=None):

        # Override the default encoding if requested.

        if encoding is not None:
            self.request.setCharacterEncoding(encoding)

        # Where the content type is "multipart/form-data", we use javax.mail
        # functionality. Otherwise, we use the Servlet API's parameter access
        # methods.

        if self.get_content_type() and self.get_content_type().media_type == "multipart/form-data":
            if self.message_fields is not None:
                return self.message_fields
            else:
                fields = self.message_fields = self._get_fields_from_message()
        else:
            fields = {}
            parameter_map = self.request.getParameterMap()
            if parameter_map:
                for field_name in parameter_map.keySet():
                    fields[field_name] = parameter_map[field_name]

        return fields

    def get_fields(self, encoding=None):

        """
        Extracts fields (or request parameters) from both the path specified in
        the transaction as well as the message body. The optional 'encoding'
        parameter specifies the character encoding of the message body for cases
        where no such information is available, but where the default encoding
        is to be overridden.

        Returns a dictionary mapping field names to lists of values (even if a
        single value is associated with any given field name). Each value is
        either a Unicode object (representing a simple form field, for example)
        or a plain string (representing a file upload form field, for example).

        Where a given field name is used in both the path and message body to
        specify values, the values from both sources will be combined into a
        single list associated with that field name.
        """

        # NOTE: The Java Servlet API (like Zope) seems to provide only body
        # NOTE: fields upon POST requests.

        if self.get_request_method() == "GET":
            return self._get_fields(encoding)
        else:
            fields = {}
            fields.update(self.get_fields_from_path())
            for name, values in self._get_fields(encoding).items():
                if not fields.has_key(name):
                    fields[name] = values
                else:
                    fields[name] += values
        return fields

    def get_user(self):

        """
        Extracts user information from the transaction.

        Returns a username as a string or None if no user is defined.
        """

        if self.user is not None:
            return self.user
        else:
            return self.request.getRemoteUser()

    def get_cookies(self):

        """
        Obtains cookie information from the request.

        Returns a dictionary mapping cookie names to cookie objects.
        """

        return self.cookies_in

    def get_cookie(self, cookie_name):

        """
        Obtains cookie information from the request.

        Returns a cookie object for the given 'cookie_name' or None if no such
        cookie exists.
        """

        return self.cookies_in.get(cookie_name)

    # Response-related methods.

    def get_response_stream(self):

        """
        Returns the response stream for the transaction.
        """

        return self.response.getWriter()

    def get_response_stream_encoding(self):

        """
        Returns the response stream encoding.
        """

        return self.response.getCharacterEncoding()

    def get_response_code(self):

        """
        Get the response code associated with the transaction. If no response
        code is defined, None is returned.
        """

        return self.status

    def set_response_code(self, response_code):

        """
        Set the 'response_code' using a numeric constant defined in the HTTP
        specification.
        """

        self.status = response_code
        self.response.setStatus(self.status)

    def set_header_value(self, header, value):

        """
        Set the HTTP 'header' with the given 'value'.
        """

        self.response.setHeader(self.format_header_value(header), self.format_header_value(value))

    def set_content_type(self, content_type):

        """
        Sets the 'content_type' for the response.
        """

        self.response.setContentType(str(content_type))

    # Higher level response-related methods.

    def set_cookie(self, cookie):

        """
        Stores the given 'cookie' object in the response.
        """

        self.set_cookie_value(cookie.name, cookie.value)

    def set_cookie_value(self, name, value, path=None, expires=None):

        """
        Stores a cookie with the given 'name' and 'value' in the response.

        The optional 'path' is a string which specifies the scope of the cookie,
        and the optional 'expires' parameter is a value compatible with the
        time.time function, and indicates the expiry date/time of the cookie.
        """

        cookie = javax.servlet.http.Cookie(self.encode_cookie_value(name),
            self.encode_cookie_value(value))
        if path is not None:
            cookie.setPath(path)

        # NOTE: The expires parameter seems not to be supported.

        self.response.addCookie(cookie)

    def delete_cookie(self, cookie_name):

        """
        Adds to the response a request that the cookie with the given
        'cookie_name' be deleted/discarded by the client.
        """

        # Create a special cookie, given that we do not know whether the browser
        # has been sent the cookie or not.
        # NOTE: Magic discovered in Webware.

        cookie = javax.servlet.http.Cookie(self.encode_cookie_value(cookie_name), "")
        cookie.setPath("/")
        cookie.setMaxAge(0)
        self.response.addCookie(cookie)

    # Session-related methods.

    def get_session(self, create=1):

        """
        Gets a session corresponding to an identifier supplied in the
        transaction.

        If no session has yet been established according to information
        provided in the transaction then the optional 'create' parameter
        determines whether a new session will be established.

        Where no session has been established and where 'create' is set to 0
        then None is returned. In all other cases, a session object is created
        (where appropriate) and returned.
        """

        session = self.request.getSession(create)
        if session:
            return Session(session)
        else:
            return None

    def expire_session(self):

        """
        Expires any session established according to information provided in the
        transaction.
        """

        session = self.request.getSession(0)
        if session:
            session.invalidate()

    # Special Java-specific methods.

    def _get_fields_from_message(self):

        "Get fields from a multipart message."

        session = javax.mail.Session.getDefaultInstance(java.util.Properties())

        # Fake a multipart message.

        str_buffer = java.io.StringWriter()
        fp = self.get_request_stream()
        boundary = fp.readline()
        str_buffer.write('Content-Type: multipart/mixed; boundary="%s"\n\n' % boundary[2:-1])
        str_buffer.write(boundary)
        str_buffer.write(fp.read())
        str_buffer.close()

        # Re-read that message.

        input_stream = java.io.StringBufferInputStream(str_buffer.toString())
        message = javax.mail.internet.MimeMessage(session, input_stream)
        content = message.getContent()
        return self._get_fields_from_multipart(content)

    def _get_fields_from_multipart(self, content):

        "Get fields from multipart 'content'."

        fields = {}
        for i in range(0, content.getCount()):
            part = content.getBodyPart(i)
            subcontent = part.getContent()

            # Convert input stream content.

            if isinstance(subcontent, java.io.InputStream):
                subcontent = Stream(subcontent).read()

            # Record string content.

            if type(subcontent) == type(""):

                # Should get: form-data; name="x"

                disposition = self.parse_header_value(HeaderValue, part.getHeader("Content-Disposition")[0])

                # Store and optionally convert the field.

                if disposition.name is not None:
                    if not fields.has_key(disposition.name[1:-1]):
                        fields[disposition.name[1:-1]] = []
                    fields[disposition.name[1:-1]].append(subcontent)

            # Otherwise, descend deeper into the multipart hierarchy.

            else:
                fields.update(self._get_fields_from_multipart(subcontent))

        return fields

class Session:

    """
    A simple session class with behaviour more similar to the Python framework
    session classes.
    """

    def __init__(self, session):

        "Initialise the session object with the framework 'session' object."

        self.session = session

    def keys(self):
        keys = []
        keys_enum = self.session.getAttributeNames()
        while keys_enum.hasMoreElements():
            keys.append(keys_enum.nextElement())
        return keys

    def values(self):
        values = []
        for key in self.keys():
            values.append(self[key])
        return values

    def items(self):
        items = []
        for key in self.keys():
            items.append((key, self[key]))
        return items

    def __getitem__(self, key):
        return self.session.getAttribute(key)

    def __setitem__(self, key, value):
        self.session.setAttribute(key, value)

    def __delitem__(self, key):
        self.session.removeAttribute(key)

# vim: tabstop=4 expandtab shiftwidth=4

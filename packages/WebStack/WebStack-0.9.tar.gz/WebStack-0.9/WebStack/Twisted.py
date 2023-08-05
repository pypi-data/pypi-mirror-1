#!/usr/bin/env python

"""
Twisted classes.
"""

import Generic
from Helpers.Auth import UserInfo
from Helpers.Request import Cookie, get_body_field, filter_fields
from Helpers.Response import ConvertingStream
from Helpers.Session import SessionStore
from cgi import parse_qs

class Transaction(Generic.Transaction):

    """
    Twisted transaction interface.
    """

    def __init__(self, trans):

        "Initialise the transaction using the Twisted transaction 'trans'."

        self.trans = trans
        self.content_type = None
        self.user = None
        self.path_info = None

        # Special objects retained throughout the transaction.

        self.session_store = None

    def commit(self):

        """
        A special method, synchronising the transaction with framework-specific
        objects.
        """

        # Close the session store.

        if self.session_store is not None:
            self.session_store.close()

    # Server-related methods.

    def get_server_name(self):

        "Returns the server name."

        return self.trans.getRequestHostname()

    def get_server_port(self):

        "Returns the server port as a string."

        return str(self.trans.getHost()[2])

    # Request-related methods.

    def get_request_stream(self):

        """
        Returns the request stream for the transaction.
        """

        return self.trans.content

    def get_request_method(self):

        """
        Returns the request method.
        """

        return self.trans.method

    def get_headers(self):

        """
        Returns all request headers as a dictionary-like object mapping header
        names to values.

        NOTE: If duplicate header names are permitted, then this interface will
        NOTE: need to change.
        """

        return self.trans.received_headers

    def get_header_values(self, key):

        """
        Returns a list of all request header values associated with the given
        'key'. Note that according to RFC 2616, 'key' is treated as a
        case-insensitive string.
        """

        # Twisted does not convert the header key to lower case (which is the
        # stored representation).

        return self.convert_to_list(self.trans.received_headers.get(key.lower()))

    def get_content_type(self):

        """
        Returns the content type specified on the request, along with the
        charset employed.
        """

        return self.parse_content_type(self.trans.getHeader("Content-Type"))

    def get_content_charsets(self):

        """
        Returns the character set preferences.
        """

        return self.parse_content_preferences(self.trans.getHeader("Accept-Language"))

    def get_content_languages(self):

        """
        Returns extracted language information from the transaction.
        """

        return self.parse_content_preferences(self.trans.getHeader("Accept-Charset"))

    def get_path(self):

        """
        Returns the entire path from the request.
        """

        return self.trans.uri

    def get_path_without_query(self):

        """
        Returns the entire path from the request minus the query string.
        """

        return self.get_path().split("?")[0]

    def get_path_info(self):

        """
        Returns the "path info" (the part of the URL after the resource name
        handling the current request) from the request.
        """

        return "/%s" % "/".join(self.trans.postpath)

    def get_query_string(self):

        """
        Returns the query string from the path in the request.
        """

        t = self.get_path().split("?")
        if len(t) == 1:
            return ""
        else:

            # NOTE: Overlook erroneous usage of "?" characters in the path.

            return "?".join(t[1:])

    # Higher level request-related methods.

    def get_fields_from_path(self):

        """
        Extracts fields (or request parameters) from the path specified in the
        transaction. The underlying framework may refuse to supply fields from
        the path if handling a POST transaction.

        Returns a dictionary mapping field names to lists of values (even if a
        single value is associated with any given field name).
        """

        # NOTE: Support at best ISO-8859-1 values.

        fields = {}
        for name, values in parse_qs(self.get_query_string(), keep_blank_values=1).items():
            fields[name] = []
            for value in values:
                fields[name].append(unicode(value, "iso-8859-1"))
        return fields

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
        encoding = encoding or self.get_content_type().charset or self.default_charset
        fields = {}
        for field_name, field_values in self.trans.args.items():

            # Find the body values.

            if type(field_values) == type([]):
                fields[field_name] = []

                # Twisted stores plain strings.

                for field_str in field_values:
                    fields[field_name].append(get_body_field(field_str, encoding))
            else:
                fields[field_name] = get_body_field(field_values, encoding)

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

        return self._get_fields(encoding)

    def get_user(self):

        """
        Extracts user information from the transaction.

        Returns a username as a string or None if no user is defined.
        """

        # Twisted makes headers lower case.

        if self.user is not None:
            return self.user

        auth_header = self.get_headers().get("authorization")
        if auth_header:
            return UserInfo(auth_header).username
        else:
            return None

    def get_cookies(self):

        """
        Obtains cookie information from the request.

        Returns a dictionary mapping cookie names to cookie objects.
        NOTE: Twisted does not seem to support this operation via methods. Thus,
        NOTE: direct access has been employed to get the dictionary.
        NOTE: Twisted also returns a plain string - a Cookie object is therefore
        NOTE: introduced.
        """

        return self.process_cookies(self.trans.received_cookies, using_strings=1)

    def get_cookie(self, cookie_name):

        """
        Obtains cookie information from the request.

        Returns a cookie object for the given 'cookie_name' or None if no such
        cookie exists.
        NOTE: Twisted also returns a plain string - a Cookie object is therefore
        NOTE: introduced.
        """

        value = self.trans.getCookie(self.encode_cookie_value(cookie_name))
        if value is not None:
            return Cookie(cookie_name, self.decode_cookie_value(value))
        else:
            return None

    # Response-related methods.

    def get_response_stream(self):

        """
        Returns the response stream for the transaction.
        """

        # Unicode can upset this operation. Using either the specified charset
        # or a default encoding.

        encoding = self.get_response_stream_encoding()
        return ConvertingStream(self.trans, encoding)

    def get_response_stream_encoding(self):

        """
        Returns the response stream encoding.
        """

        if self.content_type:
            encoding = self.content_type.charset
        else:
            encoding = None
        return encoding or self.default_charset

    def get_response_code(self):

        """
        Get the response code associated with the transaction. If no response
        code is defined, None is returned.
        """

        # NOTE: Accessing the request attribute directly.

        return self.trans.code

    def set_response_code(self, response_code):

        """
        Set the 'response_code' using a numeric constant defined in the HTTP
        specification.
        """

        self.trans.setResponseCode(response_code)

    def set_header_value(self, header, value):

        """
        Set the HTTP 'header' with the given 'value'.
        """

        self.trans.setHeader(self.format_header_value(header), self.format_header_value(value))

    def set_content_type(self, content_type):

        """
        Sets the 'content_type' for the response.
        """

        # Remember the content type for encoding purposes later.

        self.content_type = content_type
        self.trans.setHeader("Content-Type", str(content_type))

    # Higher level response-related methods.

    def set_cookie(self, cookie):

        """
        Stores the given 'cookie' object in the response.
        """

        self.set_cookie_value(cookie.name, cookie.value, path=cookie.path, expires=cookie.expires)

    def set_cookie_value(self, name, value, path=None, expires=None):

        """
        Stores a cookie with the given 'name' and 'value' in the response.

        The optional 'path' is a string which specifies the scope of the cookie,
        and the optional 'expires' parameter is a value compatible with the
        time.time function, and indicates the expiry date/time of the cookie.
        """

        self.trans.addCookie(self.encode_cookie_value(name),
            self.encode_cookie_value(value), expires=expires, path=path)

    def delete_cookie(self, cookie_name):

        """
        Adds to the response a request that the cookie with the given
        'cookie_name' be deleted/discarded by the client.
        """

        # Create a special cookie, given that we do not know whether the browser
        # has been sent the cookie or not.
        # NOTE: Magic discovered in Webware.

        self.trans.addCookie(self.encode_cookie_value(cookie_name), "", expires=0, path="/", max_age=0)

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

        # NOTE: Requires configuration.

        if self.session_store is None:
            self.session_store = SessionStore(self, "WebStack-sessions")
        return self.session_store.get_session(create)

    def expire_session(self):

        """
        Expires any session established according to information provided in the
        transaction.
        """

        # NOTE: Requires configuration.

        if self.session_store is None:
            self.session_store = SessionStore(self, "WebStack-sessions")
        self.session_store.expire_session()

# vim: tabstop=4 expandtab shiftwidth=4

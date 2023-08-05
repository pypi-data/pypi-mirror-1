#!/usr/bin/env python

"""
mod_python classes.
"""

import Generic
from Helpers.Request import get_body_field, filter_fields, Cookie
from Helpers.Response import ConvertingStream
from mod_python.util import parse_qs, FieldStorage
from mod_python import apache

# Provide alternative implementations.
# The alternative session support requires cookie support of some kind.

try:
    from mod_python.Cookie import get_cookies, add_cookie, Cookie as SimpleCookie
    have_cookies = 1
except ImportError:
    from Cookie import SimpleCookie
    have_cookies = 0
try:
    from mod_python import Session
except ImportError:
    from Helpers.Session import SessionStore
    import os
    Session = None

class Transaction(Generic.Transaction):

    """
    mod_python transaction interface.
    """

    def __init__(self, trans):

        "Initialise the transaction using the mod_python transaction 'trans'."

        self.trans = trans
        self.response_code = apache.OK
        self.content_type = None
        self.user = None
        self.path_info = None

        # Support non-framework cookies.

        if not have_cookies:

            # Define the incoming cookies.

            self.cookies_in = SimpleCookie(self.get_headers().get("cookie"))

        # Cached information.

        self.storage_body = None

        # Special objects retained throughout the transaction.

        self.session_store = None
        self.session = None # mod_python native session

    def commit(self):

        """
        A special method, synchronising the transaction with framework-specific
        objects.
        """

        # Close the session store.

        if self.session_store is not None:
            self.session_store.close()

        # Commit any native session.

        if self.session is not None:
            self.session.save()

    # Server-related methods.

    def get_server_name(self):

        "Returns the server name."

        return self.trans.connection.local_addr[0]

    def get_server_port(self):

        "Returns the server port as a string."

        return str(self.trans.connection.local_addr[1])

    # Request-related methods.

    def get_request_stream(self):

        """
        Returns the request stream for the transaction.
        """

        return self.trans

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

        return self.trans.headers_in

    def get_header_values(self, key):

        """
        Returns a list of all request header values associated with the given
        'key'. Note that according to RFC 2616, 'key' is treated as a
        case-insensitive string.
        """

        return self.convert_to_list(self.trans.headers_in.get(key))

    def get_content_type(self):

        """
        Returns the content type specified on the request, along with the
        charset employed.
        """

        return self.parse_content_type(self.trans.content_type)

    def get_content_charsets(self):

        """
        Returns the character set preferences.
        """

        return self.parse_content_preferences(self.trans.headers_in.get("Accept-Charset"))

    def get_content_languages(self):

        """
        Returns extracted language information from the transaction.
        """

        return self.parse_content_preferences(self.trans.headers_in.get("Accept-Language"))

    def get_path(self):

        """
        Returns the entire path from the request.
        """

        query_string = self.get_query_string()
        if query_string:
            return self.trans.uri + "?" + query_string
        else:
            return self.trans.uri

    def get_path_without_query(self):

        """
        Returns the entire path from the request minus the query string.
        """

        return self.trans.uri

    def get_path_info(self):

        """
        Returns the "path info" (the part of the URL after the resource name
        handling the current request) from the request.
        """

        return self.trans.path_info

    def get_query_string(self):

        """
        Returns the query string from the path in the request.
        """

        return self.trans.args or ""

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
        for name, values in parse_qs(self.get_query_string(), 1).items(): # keep_blank_values=1
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

        The mod_python.util.FieldStorage class may augment the fields from the
        body with fields found in the path.
        """

        all_fields = self._get_fields(encoding)
        fields_from_path = self.get_fields_from_path()
        return filter_fields(all_fields, fields_from_path)

    def _get_fields(self, encoding=None):
        encoding = encoding or self.get_content_type().charset or self.default_charset

        if self.storage_body is None:
            self.storage_body = FieldStorage(self.trans, keep_blank_values=1)

        # Traverse the storage, finding each field value.

        fields = {}
        for field in self.storage_body.list:
            if not fields.has_key(field.name):
                fields[field.name] = []
            fields[field.name].append(get_body_field(field.value, encoding))
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

        if self.user is not None:
            return self.user
        else:
            return self.trans.user

    def get_cookies(self):

        """
        Obtains cookie information from the request.

        Returns a dictionary mapping cookie names to cookie objects.

        NOTE: No additional information is passed to the underlying API despite
        NOTE: support for enhanced cookies in mod_python.
        """

        if have_cookies:
            found_cookies = get_cookies(self.trans)
        else:
            found_cookies = self.cookies_in
        return self.process_cookies(found_cookies)

    def get_cookie(self, cookie_name):

        """
        Obtains cookie information from the request.

        Returns a cookie object for the given 'cookie_name' or None if no such
        cookie exists.
        """

        return self.get_cookies().get(self.encode_cookie_value(cookie_name))

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

        return self.response_code

    def set_response_code(self, response_code):

        """
        Set the 'response_code' using a numeric constant defined in the HTTP
        specification.
        """

        self.response_code = response_code

    def set_header_value(self, header, value):

        """
        Set the HTTP 'header' with the given 'value'.
        """

        self.trans.headers_out[self.format_header_value(header)] = self.format_header_value(value)

    def set_content_type(self, content_type):

        """
        Sets the 'content_type' for the response.
        """

        # Remember the content type for encoding purposes later.

        self.content_type = content_type
        self.trans.content_type = str(content_type)

    # Higher level response-related methods.

    def set_cookie(self, cookie):

        """
        Stores the given 'cookie' object in the response.
        """

        # NOTE: If multiple cookies of the same name could be specified, this
        # NOTE: could need changing.

        self.set_cookie_value(cookie.name, cookie.value)

    def set_cookie_value(self, name, value, path=None, expires=None):

        """
        Stores a cookie with the given 'name' and 'value' in the response.

        The optional 'path' is a string which specifies the scope of the cookie,
        and the optional 'expires' parameter is a value compatible with the
        time.time function, and indicates the expiry date/time of the cookie.
        """

        name = self.encode_cookie_value(name)

        if have_cookies:
            cookie = SimpleCookie(name, self.encode_cookie_value(value))
            if expires is not None:
                cookie.expires = expires
            if path is not None:
                cookie.path = path
            add_cookie(self.trans, cookie)
        else:
            cookie_out = SimpleCookie()
            cookie_out[name] = self.encode_cookie_value(value)
            if path is not None:
                cookie_out[name]["path"] = path
            if expires is not None:
                cookie_out[name]["expires"] = expires
            self._write_cookie(cookie_out)

    def delete_cookie(self, cookie_name):

        """
        Adds to the response a request that the cookie with the given
        'cookie_name' be deleted/discarded by the client.
        """

        # Create a special cookie, given that we do not know whether the browser
        # has been sent the cookie or not.
        # NOTE: Magic discovered in Webware.

        name = self.encode_cookie_value(cookie_name)

        if have_cookies:
            cookie = SimpleCookie(name, "")
            cookie.path = "/"
            cookie.expires = 0
            cookie.max_age = 0
            add_cookie(self.trans, cookie)
        else:
            cookie_out = SimpleCookie()
            cookie_out[name] = ""
            cookie_out[name]["path"] = "/"
            cookie_out[name]["expires"] = 0
            cookie_out[name]["max-age"] = 0
            self._write_cookie(cookie_out)

    def _write_cookie(self, cookie):

        "An internal method adding the given 'cookie' to the headers."

        # NOTE: May not be using the appropriate method.

        for morsel in cookie.values():
            self.set_header_value("Set-Cookie", morsel.OutputString())

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

        if Session:
            # NOTE: Not exposing all functionality.
            self.session = Session.Session(self.trans)
            self.session.load()
            return self.session
        else:
            # NOTE: Requires configuration.

            if self.session_store is None:
                self.session_store = SessionStore(self, os.path.join(apache.server_root(), "WebStack-sessions"))
            return self.session_store.get_session(create)

    def expire_session(self):

        """
        Expires any session established according to information provided in the
        transaction.
        """

        if Session:
            if self.session is None:
                self.session = self.get_session(create=0)
            if self.session:
                self.session.invalidate()
                self.session = None
        else:
            # NOTE: Requires configuration.

            if self.session_store is None:
                self.session_store = SessionStore(self, os.path.join(apache.server_root(), "WebStack-sessions"))
            self.session_store.expire_session()

# vim: tabstop=4 expandtab shiftwidth=4

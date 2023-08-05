#!/usr/bin/env python

"""
Session helper functions.

Copyright (C) 2004, 2005 Paul Boddie <paul@boddie.org.uk>

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

import shelve
import os
import time
import random
import sys

class SessionStore:

    "A class representing a session store."

    def __init__(self, trans, session_directory, session_cookie_name="SID", concurrent=1, delay=1):

        """
        Initialise the session store, specifying the transaction 'trans' within
        which all session access will occur, a base 'session_directory', the
        optional 'session_cookie_name' where the session identifier is held for
        each user, and specifying using the optional 'concurrent' parameter
        whether concurrent access within the framework might occur (1) or
        whether the framework queues accesses at some other level (0). The
        optional 'delay' argument specifies the time in seconds between each
        poll of the session file when that file is found to be locked for
        editing.
        """

        self.trans = trans
        self.session_directory = session_directory
        self.session_cookie_name = session_cookie_name
        self.concurrent = concurrent
        self.delay = delay

        # Internal state.

        self.store = None
        self.store_filename, self.edit_filename = None, None
        self.to_expire = None

        # Attempt to create a session directory if it does not exist.

        if not os.path.exists(self.session_directory):
            os.mkdir(self.session_directory)

    def close(self):

        "Close the store, tidying up files and filenames."

        if self.store is not None:
            self.store.close()
            self.store = None
        if self.edit_filename is not None:
            try:
                os.rename(self.edit_filename, self.store_filename)
            except OSError:
                pass
            self.edit_filename, self.store_filename = None, None

        # Handle expiry appropriately.

        if self.to_expire is not None:
            self._expire_session(self.to_expire)
            self.trans.delete_cookie(self.session_cookie_name)

    def expire_session(self):

        """
        Expire the session in the given transaction.
        """

        # Perform expiry.

        cookie = self.trans.get_cookie(self.session_cookie_name)
        if cookie:
            self.to_expire = cookie.value

    def _expire_session(self, session_id):

        """
        Expire the session with the given 'session_id'. Note that in concurrent
        session stores, this operation will block if another execution context
        is editing the session.
        """

        filename = os.path.join(self.session_directory, session_id)
        if self.concurrent:
            while 1:
                try:
                    os.unlink(filename)
                except OSError:
                    time.sleep(self.delay)
                else:
                    break
        else:
            try:
                os.unlink(filename)
            except OSError:
                pass

    def get_session(self, create):

        """
        Get the session for the given transaction, creating a new session if
        'create' is set to 1 (rather than 0). Where new sessions are created, an
        appropriate session identifier cookie will be created.
        Returns a session object or None if no session exists and none is then
        created.
        """

        if self.store is not None:
            return self.store

        # No existing store - get the token and the actual session.

        cookie = self.trans.get_cookie(self.session_cookie_name)
        if cookie:
            return self._get_session(cookie.value, create)
        elif create:
            session_id = self._get_session_identifier()
            self.trans.set_cookie_value(self.session_cookie_name, session_id)
            return self._get_session(session_id, create)
        else:
            return None

    def _get_session(self, session_id, create):

        """
        Get a session with the given 'session_id' and whether new sessions
        should be created ('create' set to 1).
        Returns a dictionary-like object representing the session.
        """

        filename = os.path.join(self.session_directory, session_id)

        # Enforce locking.

        if self.concurrent:

            # Where the session is present (possibly being edited)...

            if os.path.exists(filename) or os.path.exists(filename + ".edit"):
                while 1:
                    try:
                        os.rename(filename, filename + ".edit")
                    except OSError:
                        time.sleep(self.delay)
                    else:
                        break

            # Where no session is present and none should be created, return.

            elif not create:
                return None

            self.store_filename = filename
            filename = filename + ".edit"
            self.edit_filename = filename

        # For non-concurrent situations, return if no session exists and none
        # should be created.

        elif not os.path.exists(filename) and not create:
            return None

        self.store = shelve.open(filename)
        return Wrapper(self.store)

    def _get_session_identifier(self):

        "Return a session identifier as a string."

        g = random.Random()
        return str(g.randint(0, sys.maxint - 1))

class Wrapper:

    "A wrapper around shelf objects."

    def __init__(self, store):
        self.store = store

    def __getattr__(self, name):
        if hasattr(self.store, name):
            return getattr(self.store, name)
        else:
            raise AttributeError, name

    def __getitem__(self, name):
        # Convert to UTF-8 to avoid bsddb limitations.
        return self.store[name.encode("utf-8")]

    def __delitem__(self, name):
        # Convert to UTF-8 to avoid bsddb limitations.
        del self.store[name.encode("utf-8")]

    def __setitem__(self, name, value):
        # Convert to UTF-8 to avoid bsddb limitations.
        self.store[name.encode("utf-8")] = value

    def keys(self):
        l = []
        for key in self.store.keys():
            # Convert from UTF-8 to avoid bsddb limitations.
            l.append(unicode(key, "utf-8"))
        return l

    def items(self):
        l = []
        for key in self.keys():
            l.append((key, self[key]))
        return l

# vim: tabstop=4 expandtab shiftwidth=4

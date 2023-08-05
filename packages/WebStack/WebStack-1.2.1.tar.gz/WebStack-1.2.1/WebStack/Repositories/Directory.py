#!/usr/bin/env python

"""
Directory repositories for WebStack.

Copyright (C) 2005, 2006 Paul Boddie <paul@boddie.org.uk>

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

import os
import time

class DirectoryRepository:

    "A directory repository providing session-like access to files."

    new_filename = "__new__"

    def __init__(self, path, fsencoding=None, delay=1):

        """
        Initialise the repository using the given 'path' to indicate the
        location of the repository. If no such location exists in the filesystem
        an attempt will be made to create the directory.

        The optional 'fsencoding' parameter can be used to assert a particular
        character encoding used by the filesystem to represent filenames. By
        default, the default encoding is detected (or Unicode objects are used
        if appropriate).

        The optional 'delay' argument specifies the time in seconds between each
        poll of an opened repository file when that file is found to be locked
        for editing.
        """

        # Convert the path to an absolute path.

        self.path = os.path.abspath(path)
        self.fsencoding = fsencoding
        self.delay = delay

        # Create a directory and initialise it with a special file.

        if not os.path.exists(path):
            os.mkdir(path)
            f = open(self.full_path(self.new_filename), "wb")
            f.close()

        # Guess the filesystem encoding.

        if fsencoding is None:
            if os.path.supports_unicode_filenames:
                self.fsencoding = None
            else:
                import locale
                self.fsencoding = locale.getdefaultlocale()[1] or 'ascii'

        # Or override any guesses.

        else:
            self.fsencoding = fsencoding or 'ascii'

    def _convert_name(self, name):

        "Convert the given 'name' to a plain string in the filesystem encoding."

        if self.fsencoding:
            return name.encode(self.fsencoding)
        else:
            return name

    def _convert_fsname(self, name):

        """
        Convert the given 'name' as a plain string in the filesystem encoding to
        a Unicode object.
        """

        if self.fsencoding:
            return unicode(name, self.fsencoding)
        else:
            return name

    def keys(self):

        "Return the names of the files stored in the repository."

        # NOTE: Special names converted using a simple rule.
        l = []
        for name in os.listdir(self.path):
            if name.endswith(".edit"):
                name = name[:-5]
            if name != self.new_filename:
                l.append(name)
        return map(self._convert_fsname, l)

    def full_path(self, key, edit=0):

        """
        Return the full path to the 'key' in the filesystem. If the optional
        'edit' parameter is set to a true value, the returned path will refer to
        the editable version of the file.
        """

        # NOTE: Special names converted using a simple rule.
        path = os.path.abspath(os.path.join(self.path, self._convert_name(key)))
        if edit:
            path = path + ".edit"
        if not path.startswith(self.path):
            raise ValueError, key
        else:
            return path

    def edit_path(self, key):

        """
        Return the full path to the 'key' in the filesystem provided that the
        file associated with the 'key' is locked for editing.
        """

        return self.full_path(key, edit=1)

    def has_key(self, key):

        """
        Return whether a file with the name specified by 'key is stored in the
        repository.
        """

        return key in self.keys()

    # NOTE: Methods very similar to Helpers.Session.Wrapper.

    def items(self):

        """
        Return a list of (name, value) tuples for the files stored in the
        repository.
        """

        results = []
        for key in self.keys():
            results.append((key, self[key]))
        return results

    def values(self):

        "Return the contents of the files stored in the repository."

        results = []
        for key in self.keys():
            results.append(self[key])
        return results

    def lock(self, key, create=0, opener=None):

        """
        Lock the file associated with the given 'key'. If the optional 'create'
        parameter is set to a true value (unlike the default), the file will be
        created if it did not already exist; otherwise, a KeyError will be
        raised.

        If the optional 'opener' parameter is specified, it will be used to
        create any new file in the case where 'create' is set to a true value;
        otherwise, the standard 'open' function will be used to create the file.

        Return the full path to the editable file.
        """

        path = self.full_path(key)
        edit_path = self.edit_path(key)

        # Attempt to lock the file by renaming it.
        # NOTE: This assumes that renaming is an atomic operation.

        if os.path.exists(path) or os.path.exists(edit_path):
            while 1:
                try:
                    os.rename(path, edit_path)
                except OSError:
                    time.sleep(self.delay)
                else:
                    break

        # Where a file does not exist, attempt to create a new file.
        # Since file creation is probably not atomic, we use the renaming of a
        # special file in an attempt to impose some kind of atomic "bottleneck".

        elif create:

            # NOTE: Avoid failure case where no __new__ file exists for some
            # NOTE: reason.

            try:
                self.lock(self.new_filename)
            except KeyError:
                f = open(self.edit_path(self.new_filename), "wb")
                f.close()

            try:
                if opener is None:
                    f = open(edit_path, "wb")
                    f.close()
                else:
                    f = opener(edit_path)
                    f.close()
            finally:
                self.unlock(self.new_filename)

        # Where no creation is requested, raise an exception.

        else:
            raise KeyError, key

        return edit_path

    def unlock(self, key):

        """
        Unlock the file associated with the given 'key'.

        Important note: this method should be used in a finally clause in order
        to avoid files being locked and never being unlocked by the same process
        because an unhandled exception was raised.
        """

        path = self.full_path(key)
        edit_path = self.edit_path(key)
        os.rename(edit_path, path)

    def __delitem__(self, key):

        "Remove the file associated with the given 'key'."

        path = self.full_path(key)
        edit_path = self.edit_path(key)
        if os.path.exists(path) or os.path.exists(edit_path):
            while 1:
                try:
                    os.remove(path)
                except OSError:
                    time.sleep(self.delay)
                else:
                    break
        else:
            raise KeyError, key

    def __getitem__(self, key):

        "Return the contents of the file associated with the given 'key'."

        edit_path = self.lock(key, create=0)
        try:
            f = open(edit_path, "rb")
            s = ""
            try:
                s = f.read()
            finally:
                f.close()
        finally:
            self.unlock(key)

        return s

    def __setitem__(self, key, value):

        """
        Set the contents of the file associated with the given 'key' using the
        given 'value'.
        """

        edit_path = self.lock(key, create=1)
        try:
            f = open(edit_path, "wb")
            try:
                f.write(value)
            finally:
                f.close()
        finally:
            self.unlock(key)

# vim: tabstop=4 expandtab shiftwidth=4

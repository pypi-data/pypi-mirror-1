# -*- coding:utf-8 -*-

## Copyright (c) 2006, 2007, Joerg Zinke, Jonas Weismueller (team@petunial.com)
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions
## are met:
##
##  * Redistributions of source code must retain the above copyright
##    notice, this list of conditions and the following disclaimer.
##  * Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in
##    the documentation and/or other materials provided with the
##    distribution.
##  * Neither the name of the Petunial Team nor the names of its
##    contributors may be used to endorse or promote products derived
##    from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
## FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
## COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
## INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
## BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
## CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
## LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
## ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
## POSSIBILITY OF SUCH DAMAGE.

"""

latua - test/latua/core/test_files.py

latua test class for files

"""

__version__ = "$Revision: 302 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/test/latua/_system/test_files.py $

## standard modules
import os
import tempfile
import unittest

## latua modules
import latua

class FilesTestCase(unittest.TestCase):
    """Test cases for latua files class."""
    def setUp(self):
        """Test set up."""
        self.__system = latua.System()
        self.__test_directory = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        self.__test_file_handle, self.__test_file_name = tempfile.mkstemp(prefix="latua_test_temp_", dir=self.__test_directory)

    def test_directory(self):
        """Test files directory exceptions."""
        self.assertRaises(latua.error.FilesError,
                          self.__system.files.search, "")
        self.assertRaises(latua.error.FilesError,
                          self.__system.files.integrity, "", [])

    def test_integrity(self):
        """Test files integrity."""
        result = self.__system.files.integrity(os.path.dirname(self.__test_file_name), [os.path.basename(self.__test_file_name)])
        self.assertEqual(len(result), 0,
                         "failed to check integrity for existing file %s" % (self.__test_file_name))
        handle, name = tempfile.mkstemp(prefix="latua_test_temp_", dir=self.__test_directory)
        os.close(handle)
        os.remove(name)
        result = self.__system.files.integrity(os.path.dirname(name), [os.path.basename(name)])
        self.assertEqual(result, [os.path.basename(name)],
                         "failed to check integrity for non-existent file %s" % (name))

    def test_permission(self):
        """Test files permission."""
        os.chmod(self.__test_file_name, 0000)
        result = self.__system.files.permission(self.__test_file_name)
        self.assertEqual(result, ("---", "---", "---"),
                         "permission do not match expected 0000")
        os.chmod(self.__test_file_name, 0444)
        result = self.__system.files.permission(self.__test_file_name)
        self.assertEqual(result, ("r--", "r--", "r--"),
                         "permission do not match expected 0444")
        os.chmod(self.__test_file_name, 0555)
        result = self.__system.files.permission(self.__test_file_name)
        self.assertEqual(result, ("r-x", "r-x", "r-x"),
                         "permission do not match expected 0555")
        os.chmod(self.__test_file_name, 0666)
        result = self.__system.files.permission(self.__test_file_name)
        self.assertEqual(result, ("rw-", "rw-", "rw-"),
                         "permission do not match expected 0666")
        os.chmod(self.__test_file_name, 0777)
        result = self.__system.files.permission(self.__test_file_name)
        self.assertEqual(result, ("rwx", "rwx", "rwx"),
                         "permission do not match expected 0777")

    def test_search(self):
        """Test files search."""
        result = self.__system.files.search(self.__test_directory, "file", ".py", absolute=False)
        self.assert_(len(result) > 0, "search found no files")
        ## search result contains at least one init file
        self.assertEqual(os.path.join(self.__test_directory, "__init__.py") in result, True,
                         "no init file found in search result")
        result = self.__system.files.search(self.__test_directory, "directory", absolute=False)
        self.assert_(len(result) > 0, "search found no files")
        ## search result contains at least the latua directory
        self.assertEqual(os.path.join(self.__test_directory, "latua") in result, True,
                         "latua directiory not found in search result")

    def test_types(self):
        """Test files search types exceptions."""
        self.assertRaises(latua.error.FilesError,
                          self.__system.files.search, self.__test_directory, "test_type")

    def tearDown(self):
        """Clean up after tests."""
        os.close(self.__test_file_handle)
        os.remove(self.__test_file_name)
        self.__test_file_handle = None
        self.__test_file_name = None
        self.__test_directory = None
        self.__system = None

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """

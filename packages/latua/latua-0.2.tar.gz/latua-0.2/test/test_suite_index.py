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

test - test/test_suite_index.py

latua test index suite

"""

__version__ = "$Revision: 293 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/test/test_suite_index.py $

## standard modules
import unittest

## latua test modules
import test.latua._index.test_file
import test.latua._index.test_search
import test.latua._index.test_handler
import test.latua._index.test_database
import test.latua._index.test_connection

class IndexTestSuite(unittest.TestSuite):
    """Suite for testing latuas index system."""
    def __init__(self):
        unittest.TestSuite.__init__(self)
        self.addTest(unittest.makeSuite(test.latua._index.test_connection.ConnectionTestCase))
        self.addTest(unittest.makeSuite(test.latua._index.test_database.DatabaseTestCase))
        self.addTest(unittest.makeSuite(test.latua._index.test_file.FileTestCase))
        self.addTest(unittest.makeSuite(test.latua._index.test_search.SearchTestCase))
        self.addTest(unittest.makeSuite(test.latua._index.test_handler.HandlerTestCase))

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """

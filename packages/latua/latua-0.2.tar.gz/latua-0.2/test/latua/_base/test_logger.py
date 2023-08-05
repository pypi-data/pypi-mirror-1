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

latua - test/latua/_base/test_logger.py

latua test class for logger

"""

__version__ = "$Revision: 258 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/test/latua/_base/test_logger.py $

## standard modules
import os
import sys
import smtpd
import smtplib
import asyncore
import logging
import cStringIO
import threading
import unittest

## latua modules
import latua
import latua._context

class LoggerTestCase(unittest.TestCase):
    """Test cases for latuas logging system."""
    def setUp(self):
        """Set up needed objects."""
        latua._context._loggers = []
        self.__base = latua.Base()
        ## catch console logger output
        self.__output = cStringIO.StringIO()
        sys.stderr = self.__output
        ## reinitialize console logger after setting stderr output
        self.__base.logger.reset()

    def test_console(self):
        """Test logging to console."""
        for item in self.__base.logger.levels:
            ## test console logging with different levels
            getattr(self.__base.logger, item)("latua test console %s" % (item))
            self.__base.logger.flush()
            if getattr(logging, item.upper()) >= logging.ERROR:
                self.assert_(self.__output.getvalue().find("latua test console %s" % (item)) >= 0,
                             "%s logging to console failed" % (item))
            else:
                self.assert_(self.__output.getvalue().find("latua test console %s" % (item)) == -1,
                             "logged to console with level %s" % (item))

    def test_context(self):
        """Test logging context initialization."""
        self.assertEqual(len(latua._context._loggers), 1,
                         "wrong length of logging context")

    def test_logfile(self):
        """Test logging to logfile."""
        ## remove console logger
        self.__base.logger.reset()
        self.__base.logger.logfile("test_file.log")
        ## get filehandle for logfile
        test_file_handle = open("test_file.log")
        for value in self.__base.logger.levels:
            ## test different logging levels
            getattr(self.__base.logger, value)("latua test logfile %s" % (value))
            self.__base.logger.flush()
            ## read line from logfile
            line =  test_file_handle.readline()
            self.assert_(line.find("latua test logfile %s" % (value)) >= 0,
                         "%s logging to logfile failed" % (value))
        ## close filehandle
        test_file_handle.close()
        ## remove created logfile
        os.remove("test_file.log")

    def test_reset(self):
        """Test logging reset."""
        self.__base.logger.reset()
        ## at least console logging handler is there
        self.assertEqual(len(latua._context._loggers), 1,
                         "failed to reset logging handlers")

    def test_smtp(self):
        """Test logging to smtp."""
        address = ("127.0.0.1", 11001)
        ## start smtp debugging server on port 11001 to avoid collision
        ## with other mailservers
        server = smtpd.DebuggingServer(address, None)
        ## smtp server is based on asyncore
        ## use polling to avoid socket timout exceptions from select on close
        server_thread = threading.Thread(target=asyncore.loop, kwargs={"use_poll": True})
        server_thread.start()
        ## smtp debugging server logs to stdout
        output = cStringIO.StringIO()
        sys.stdout = output
        ## create smtp logger
        self.__base.logger.smtp(address, "test", ["test"], "test")
        for item in self.__base.logger.levels:
            ## test smtp logging with different levels
            getattr(self.__base.logger, item)("latua test smtp %s" % (item))
            self.__base.logger.flush()
            self.assert_(output.getvalue().find("latua test smtp %s" % (item)) >= 0,
                         "%s logging to smtp failed" % (item))
        ## shutdown mailserver and exit thread
        server.close()
        ## restore original stderr
        sys.stdout = sys.__stdout__

    def test_syslog(self):
        """Test logging to syslog."""
        ## remove console logger
        self.__base.logger.reset()
        self.__base.logger.syslog()
        for item in self.__base.logger.levels:
            ## test syslog logging with different levels
            getattr(self.__base.logger, item)("latua test syslog %s" % (item))
            self.__base.logger.flush()
            ## nothing to assert here

    def test_types(self):
        """Test logging available types."""
        for item in self.__base.logger.types:
            self.assertEqual(hasattr(self.__base.logger, item), True,
                             "logging type is not available %s" % (item))

    def tearDown(self):
        """Clean up after tests."""
        ## restore original stderr
        sys.stderr = sys.__stderr__
        self.__output = None
        self.__base = None

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """

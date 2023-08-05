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

__version__ = "$Revision: 211 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1.1/test/latua/_base/test_logger.py $

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

    def test_console(self):
        """Test logging to console."""
        output = cStringIO.StringIO()
        sys.stderr = output
        ## reinitialize console logger after setting stderr output
        self.__base.logger.reset()
        self.__base.logger._console("test_console")
        for item in self.__base.logger.levels:
            ## test console logging with different levels
            getattr(self.__base.logger, item)("latua test console %s" % (item))
            self.__base.logger._flush()
            if getattr(logging, item.upper()) >= logging.ERROR:
                self.assert_(output.getvalue().find("latua test console %s" % (item)) >= 0,
                             "%s logging to console failed" % (item))
            else:
                self.assert_(output.getvalue().find("latua test console %s" % (item)) == -1,
                             "logged to console with level %s" % (item))
        ## restore original stderr
        sys.stderr = sys.__stderr__

    def test_logfile(self):
        """Test logging to logfile."""
        ## remove console logger
        self.__base.logger.reset()
        self.__base.logger.logfile("test_logfile", "test_file.log")
        ## get filehandle for logfile
        test_file_handle = open("test_file.log")
        for key, value in enumerate(self.__base.logger.levels):
            ## test different logging levels
            getattr(self.__base.logger, value)("latua test logfile %s" % (value))
            self.__base.logger._flush()
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
        self.assertEqual(len(latua._context._loggers), 0,
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
        ## remove console logger
        self.__base.logger.reset()
        ## create smtp logger
        self.__base.logger.smtp("test_smtp", address, "test", ["test"], "test")
        for item in self.__base.logger.levels:
            ## test smtp logging with different levels
            getattr(self.__base.logger, item)("latua test smtp %s" % (item))
            self.__base.logger._flush()
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
        self.__base.logger.syslog("test_syslog")
        for item in self.__base.logger.levels:
            ## test syslog logging with different levels
            getattr(self.__base.logger, item)("latua test syslog %s" % (item))
            self.__base.logger._flush()
            ## nothing to assert here

    def tearDown(self):
        """Clean up after tests."""
        self.__base = None

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """

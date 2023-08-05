# -*- coding: utf-8 -*-

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

latua - latua/_base/_logger.py

latua logger classes

following logger levels
are available:

critical     50
error        40
warning      30
info         20
debug        10
notset       0

"""

__version__ = "$Revision: 218 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1.1/latua/_base/_logger.py $

## standard modules
import os
import sys
import logging
import logging.handlers

## latua modules
import latua._context

class _Logger(logging.Logger):
    """Logger class"""
    def __init__(self, name):
        logging.Logger.__init__(self, name)
        ## get platform
        self.__platform = latua._base._platform._Platform()
        ## set logging handlers to context (restore)
        self.handlers = latua._context._loggers
        if len(self.handlers) == 0:
            ## every logger has at least the console
            ## handle as default using the application name
            self._console(self.name)
        ## do not overwrite logger level of parent class
        self.levels = ["critical", "error", "warning", "info", "debug"]
        self.types = ["syslog", "logfile"]#, "smtp"]

    def __function(self):
        """Return function name of logging caller."""
        result = ""
        ## get current frame
        frame = sys._getframe()
        ## one step back to __function caller
        frame = frame.f_back
        ## one step back to logging caller
        frame = frame.f_back
        ## check if caller was inside a function
        if not frame.f_code.co_name == "?":
            result = "%s(): " % (frame.f_code.co_name)
        return result

    def _flush(self):
        """Flush stream of logging handlers."""
        for item in self.handlers:
            item.flush()

    def _console(self, name):
        """Set default logging handler to sys.stderr."""
        handle = logging.StreamHandler()
        ## console handler logs only errors by default
        ## debugging should be done with logfile handler or via syslog
        handle.setLevel(logging.ERROR)
        ## set logging format
        handle.setFormatter(logging.Formatter("%s %s %s: %s%s" % ("%(asctime)s",
                                                                  name,
                                                                  "%(levelname)s",
                                                                  self.__function(),
                                                                  "%(message)s (%(filename)s at line %(lineno)d)")))
        ## add new handler
        self.addHandler(handle)

    def logfile(self, name, log_file=None, log_file_size=None, log_file_rotate=None):
        """Set logging handle to logging to file."""
        if log_file == None:
            log_file = "%s.log" % (name)
        if log_file_size == None:
            log_file_size = "3"
        if log_file_rotate == None:
            log_file_rotate = "3"
        ## append to logfile and rotate logfiles by size and number of cycles
        handle = logging.handlers.RotatingFileHandler(log_file,
                                                      "a",
                                                      int(log_file_size) * 1024 * 1024,
                                                      int(log_file_rotate))
        ## set logging format
        handle.setFormatter(logging.Formatter("%s %s %s: %s%s" % ("%(asctime)s",
                                                                  name,
                                                                  "%(levelname)s",
                                                                  self.__function(),
                                                                  "%(message)s (%(filename)s at line %(lineno)d)")))
        ## add new handler
        self.addHandler(handle)

    def smtp(self, name, mailhost, fromaddr, toaddrs, subject):
        """Set logging handle to smtp."""
        ## send log messages via mail
        handle = logging.handlers.SMTPHandler(mailhost, fromaddr, toaddrs, subject)
        ## set logging format
        handle.setFormatter(logging.Formatter("%s %s: %s%s" % (name,
                                                               "%(levelname)s",
                                                               self.__function(),
                                                               "%(message)s (%(filename)s at line %(lineno)d)")))
        ## add new handler
        self.addHandler(handle)

    def syslog(self, name):
        """Set logging handle to syslog."""
        handle = self.__platform.logging_handler
        ## set logging format
        handle.setFormatter(logging.Formatter("%s %s: %s%s" % (name,
                                                               "%(levelname)s",
                                                               self.__function(),
                                                               "%(message)s (%(filename)s at line %(lineno)d)")))
        ## add new handler
        self.addHandler(handle)

    def log_level(self, level=None):
        """Set log level for all loggers."""
        ## default logging level depends on platform
        log_level = self.__platform.logging_level
        if level in self.levels:
            ## set logging level from string
            log_level = getattr(logging, level.upper())
        ## set log level for parent logger
        ## console handler keeps error level
        self.setLevel(log_level)

    def reset(self):
        """Remove all logging handlers."""
        self._flush()
        for item in self.handlers:
            self.removeHandler(item)

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """

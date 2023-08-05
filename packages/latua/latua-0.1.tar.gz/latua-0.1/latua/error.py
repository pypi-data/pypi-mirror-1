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

latua - latua/error.py

latua error classes

"""

__version__ = "$Revision: 191 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1/latua/error.py $

## standard modules
import traceback

class _LatuaError(Exception):
    """Exception base class for errors in latua."""
    def __init__(self, message, details=""):
        self.message = message
        self.details = details

class _BaseError(_LatuaError):
    """Exception base class for base errors in latua."""
    def __init__(self, message, details=""):
        _LatuaError.__init__(self, message, details="")

class _SystemError(_LatuaError):
    """Exception base class for system errors in latua."""
    def __init__(self, message, details=""):
        _LatuaError.__init__(self, message, details="")

class PlatformError(_BaseError):
    """Indicates an error in accessing platform attributes."""
    def __init__(self, attribute, message, details=""):
        _BaseError.__init__(self, message, details="")
        self.attribute = attribute

    def __str__(self):
        """Representation of exception."""
        return "%s\n[%s]: %s %s" % (traceback.format_exc(),
                                    self.attribute,
                                    self.message,
                                    self.details)

class I18nError(_BaseError):
    """Indicates an error in i18n configuration."""
    def __init__(self, language, message, details=""):
        _BaseError.__init__(self, message, details="")
        self.language = language

    def __str__(self):
        """Representation of exception."""
        return "%s\n[%s]: %s (%s)" % (traceback.format_exc(),
                                      self.language,
                                      self.message,
                                      self.details)

class ConfigurationError(_SystemError):
    """Indicates an error in configuration."""
    def __init__(self, path, message, details=""):
        _SystemError.__init__(self, message, details="")
        self.path = path

    def __str__(self):
        """Representation of exception."""
        return "%s\n[%s]: %s %s" % (traceback.format_exc(),
                                    self.path,
                                    self.message,
                                    self.details)

class ModulesError(_SystemError):
    """Indicates an error in modules class."""
    def __init__(self, module, message, details=""):
        _SystemError.__init__(self, message, details="")
        self.module = module

    def __str__(self):
        """Representation of exception."""
        return "%s\n[%s]: %s %s" % (traceback.format_exc(),
                                    self.module,
                                    self.message,
                                    self.details)

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """

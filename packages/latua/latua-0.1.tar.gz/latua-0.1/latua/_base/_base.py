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

latua - latua/_base/_base.py

latua base class

inherit from or use base in other classes to have all variables
which just initialized only once: translation, platform and loggers

never inherit or use a class from _base/ directly
outside of _base/ directory to avoid faults in
initialization order

"""

__version__ = "$Revision: 101 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1/latua/_base/_base.py $

## standard modules
import os
import sys

## latua modules
import latua._context
import latua._base._platform
import latua._base._i18n
import latua._base._logger

class _Base(object):
    """Provide translation, platform, logger and requirements."""
    def __init__(self, application=None):
        ## get actual platform
        self.platform = latua._base._platform._Platform()
        ## initialization of translation
        self.i18n = latua._base._i18n._I18n()
        ## initialization of logger
        self.logger = latua._base._logger._Logger(self.platform.application_name)

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """

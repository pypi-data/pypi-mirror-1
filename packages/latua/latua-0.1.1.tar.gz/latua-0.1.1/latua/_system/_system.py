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

latua - latua/_system/_system.py

system class contains generic system services

"""

__version__ = "$Revision: 190 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1.1/latua/_system/_system.py $

## standard modules
import os
import time

## latua modules
import latua._system._crypt
import latua._system._files
import latua._system._modules
import latua._system._configuration

class _System(object):
    """System services."""
    def __init__(self):
        ## add configuration object
        self.configuration = latua._system._configuration._Configuration()
        ## add crypt object
        self.crypt = latua._system._crypt._Crypt()
        ## add files object
        self.files = latua._system._files._Files()
        ## add modules object
        self.modules = latua._system._modules._Modules()

    def sort(self, dictionary, values=False):
        """Sort a dict by keys or values."""
        if values == True:
            ## sort by values
            dictionary_values = dictionary.values()
            dictionary_values.sort()
            return dictionary_values
        else:
            ## sort by keys
            dictionary_keys = dictionary.keys()
            dictionary_keys.sort()
            return [dictionary[key] for key in dictionary_keys]

    def system(self, item):
        """Check if item belongs to system."""
        result = False
        if item.startswith("_"):
            ## system item starts with underscore
            result = True
        return result

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """

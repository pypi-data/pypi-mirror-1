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

latua - latua/singleton.py

singleton class implemented as borg pattern and as real singleton

"""

__version__ = "$Revision:300 $"
# $URL:http://www.linuxnetworkcare.com:5335/svn/petunial/trunk/source/petunial/base/_borg.py $

class Borg(object):
    """Singleton as borg pattern."""
    __shared_state = {}
    def __new__(cls, *arguments, **keywords):
        self = object.__new__(cls, *arguments, **keywords)
        ## basic idea of borg pattern is:
        ## all objects have the same (shared) state
        ## but object ids are different (not real singletons)
        self.__dict__ = cls.__shared_state
        return self

class Singleton(object):
    """Real singleton pattern."""
    def __new__(cls, *arguments, **keywords):
        if not "_the_instance" in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        ## return the same instance with same object id
        return cls._the_instance

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """

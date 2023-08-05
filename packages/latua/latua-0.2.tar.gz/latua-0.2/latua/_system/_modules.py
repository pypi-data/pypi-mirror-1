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

latua - latua/_system/_modules.py

modules class for working with modules

"""

__version__ = "$Revision: 321 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/latua/_system/_modules.py $

## standard modules
import os
import sys
import imp

## latua modules
import latua.error

class _Modules(object):
    """Modules class for working with modules."""
    def __init__(self):
        pass

    def _import(self, module_path, variable=None):
        """Import module from path and get given variable."""
        result = None
        path = module_path.split(".")
        name = path.pop()
        try:
            ## see if the module has already been imported
            module = sys.modules[name]
        except KeyError, error:
            module = __import__(module_path, globals(), locals(), [""])
        result = module
        if variable and not result == None:
            ## get only a specific class from module
            result = getattr(module, variable)()
        return result

    def append(self, target, path, value=None):
        """Create and append a module to another."""
        result = None
        ## get whole module path from targets name
        module_path = [target.__name__]
        ## split module name from element of path
        name = ""
        if not path == "":
            name = path.split(".").pop()
        else:
            raise latua.error.ModulesError(module_path, "given module path is empty")
        ## iterate over path
        for item in path.split("."):
            if not hasattr(".".join(module_path), item):
                ## module does not already exists
                new_module = imp.new_module(item)
                if item == name and not value == None:
                    ## set last element to given module
                    new_module = value
                ## set full name of new modules
                new_module.__name__ = "%s.%s" % (".".join(module_path), item)
                ## append new module
                setattr(self._import(".".join(module_path)), item, new_module)
                ## append module to sys search path
                sys.modules["%s.%s" % (".".join(module_path), item)] = new_module
                module_path.append(item)
                ## set result to new module
                result = new_module
        return result

    def filename_modulename(self, filename):
        """Convert filename to modulename."""
        modulename = filename.replace(os.sep, ".")
        ## strip .py
        modulename = os.path.splitext(modulename)[0]
        return modulename

    def modulename_filename(self, modulename):
        """Convert modulename to filename."""
        filename = modulename.replace(".", os.sep)
        ## append .py
        filename = "%s%spy" % (filename, os.path.extsep)
        return filename

##    def modulename(self):
##        """Find name of the calling module."""
##        if self.__class__.__module__ == "latua._base":
##            ## class is only used no inheritance
##            return sys.argv[0]
##        else:
##            ## inherited from class in child class
##            if self.__class__.__module__ == "__main__":
##                return sys.argv[0]
##            return self.__class__.__module__

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """

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

__version__ = "$Revision: 191 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1/latua/_system/_modules.py $

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

    def _import(self, module_path, class_name=None):
        """Import module from path and get given variable."""
        return_value = None
        path = module_path.split(".")
        name = path.pop()
        try:
            ## see if the module has already been imported
            module = sys.modules[name]
        except KeyError, error:
            module = __import__(module_path, globals(), locals(), [""])
        return_value = module
        if class_name and not return_value == None:
            ## get only a specific class from module
            return_value = getattr(module, class_name)()
        return return_value

    def append(self, target, path, value=None):
        """Create or append a module to another."""
        module_path = [target.__name__]
        name = ""
        if not path == "":
            ## split module name from element of path
            name = path.split(".").pop()
        else:
            raise latua.error.ModulesError(target.__name__, "given module path is empty")
        ## iterate over path
        for item in path.split("."):
            if not hasattr(".".join(module_path), item):
                ## module does not already exists
                new_module = imp.new_module(item)
                if item == name and not value == None:
                    ## set last element to given module
                    new_module = value
                setattr(self._import(".".join(module_path)), item, new_module)
                ## append module to sys search path
                sys.modules["%s.%s" % (".".join(module_path), item)] = new_module
                module_path.append(item)

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

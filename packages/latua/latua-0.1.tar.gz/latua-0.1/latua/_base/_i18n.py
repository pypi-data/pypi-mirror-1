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

latua - latua/_base/_i18n.py

classes for internationalization

"""

__version__ = "$Revision: 203 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1/latua/_base/_i18n.py $

## standard modules
import locale
import gettext

## latua modules
import latua._context

class _I18n(object):
    """Load and install languages."""
    def __init__(self):
        ## get platform data
        self.__platform = latua._base._platform._Platform()
        ## available languages with installed translations
        self.languages = latua._context._languages
        ## maybe no translations found
        ## retry again on every init
        ## bad for performance but gives the
        ## possibility to add languages on the fly
        if len(self.languages) == 0:
            ## find all available languages with installed translations
            self.languages = gettext.find(self.__platform.application_name,
                                          self.__platform.locales_directory,
                                          languages=self.__platform.languages,
                                          all=True)
            ## set the locale for all categories
            ## to the users default setting
            locale.setlocale(locale.LC_ALL, '')

    def install_translation(self, language=None):
        """Install actual translation."""
        if len(self.languages) == 0:
            raise latua.error.I18nError(None, "no languages available",
                                        self.languages)
        if language not in self.languages:
            raise latua.error.I18nError(language, "language is not available",
                                        self.languages)
        ## get translation
        translation = gettext.translation(self.__platform.application_name,
                                          self.__platform.locales_directory,
                                          languages=[language],
                                          unicode=1,
                                          fallback=True)
        ## change translation on the fly
        translation.install()

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """

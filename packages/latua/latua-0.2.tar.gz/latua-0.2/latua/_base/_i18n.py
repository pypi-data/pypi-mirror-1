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

__version__ = "$Revision: 318 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/latua/_base/_i18n.py $

## standard modules
import os
import locale
import gettext

## latua modules
import latua._context
import latua._base._platform

class _I18n(object):
    """Load and install languages."""
    def __init__(self):
        ## get platform data
        self.__platform = latua._base._platform._Platform()
        ## available languages with installed translations
        self.languages = latua._context._languages
        ## native names for languages
        ## from http://people.w3.org/rishida/names/languages.html
        self.natives = {'af'   : u'Afrikaans',
                        'ar'   : u'العربية',
                        'bg'   : u'Български',
                        'bs'   : u'Bosanski',
                        'ca'   : u'Català',
                        'cs'   : u'Čeština',
                        'cy'   : u'Cymraeg',
                        'da'   : u'Dansk',
                        'de'   : u'Deutsch',
                        'el'   : u'Ελληνικά',
                        'en'   : u'English',
                        'es'   : u'Español',
                        'es_MX': u'Español de Mexico ',
                        'eo'   : u'Esperanto',
                        'et'   : u'Eesti',
                        'eu'   : u'Euskara',
                        'fa'   : u'فارسی',
                        'fi'   : u'Suomi',
                        'fr'   : u'Français',
                        'ga'   : u'Gaeilge',
                        'gl'   : u'Galego',
                        'he'   : u'עברית',
                        'hi'   : u'हिंदी',
                        'hr'   : u'Hrvatski',
                        'hu'   : u'Magyar',
                        'hy'   : u'Հայերեն',
                        'in'   : u'Bahasa indonesia',
                        'is'   : u'Íslenska',
                        'it'   : u'Italiano',
                        'ja'   : u'日本語',
                        'ka'   : u'ქართული ენა',
                        'ko'   : u'한국어',
                        'lt'   : u'Lietuvių',
                        'ml'   : u'Malayalam',
                        'ms'   : u'Bahasa melayu',
                        'nb_NO': u'Norsk bokmål',
                        'nl'   : u'Nederlands',
                        'nn_NO': u'Norsk Nynorsk',
                        'pl'   : u'Polski',
                        'pt'   : u'Português',
                        'pt_BR': u'Português do Brasil',
                        'ro'   : u'Română',
                        'ru'   : u'Русский',
                        'sk'   : u'Slovenský',
                        'sl'   : u'Slovensko',
                        'sq'   : u'Shqipe',
                        'sv'   : u'Svenska',
                        'te'   : u'     తెలుగు',
                        'th'   : u'ภาษาไทย',
                        'tlh'  : u'tlhIngan-Hol',
                        'tr'   : u'Türkçe',
                        'uk'   : u'Українська',
                        'vi'   : u'Tiê?ng Viê?t',
                        'zh_CN': u'简体中文',
                        'zh_TW': u'繁體中文'}
        ## maybe no translations found retry again on every init
        ## bad for performance but gives the possibility to add
        ## languages on the fly
        if len(self.languages) == 0:
            self.find_translation()
            ## set the locale for all categories
            ## to the users default setting
            locale.setlocale(locale.LC_ALL, '')
            ## install at least null translation
            self.install_translation()

    def find_translation(self, domain=None):
        """Find translations."""
        if domain == None:
            ## fall back to script name
            domain = self.__platform.application_name
        ## find all languages with translations
        languages = gettext.find(domain,
                                 self.__platform.locales_directory,
                                 languages=self.__platform.languages,
                                 all=True)
        for item in languages:
            ## split mo file
            item = os.path.split(item)[0]
            ## split lc messages
            item = os.path.split(item)[0]
            ## split language
            item = os.path.split(item)[1]
            ## try to add native name
            if item in self.natives.keys():
                self.languages.append((item, self.natives[item]))
            else:
                self.languages.append((item, item.title()))
            ## sort languages
            self.languages.sort()

    def install_translation(self, language="en", domain=None):
        """Install actual translation."""
        if domain == None:
            ## fall back to script name
            domain = self.__platform.application_name
        ## get translation
        translation = gettext.translation(domain,
                                          self.__platform.locales_directory,
                                          languages=[language],
                                          #unicode=True,
                                          fallback=True)
        ## install translation on the fly
        translation.install()

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """

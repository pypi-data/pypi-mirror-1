# -*- coding: utf8 -*-
# Copyright (c) 2007 Tarek Ziadé <tziade@nuxeo.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
import os

__all__ =  ['applyFilter', 'applyFilters', 'AllFilters']
filters = {}
USE_ZOPYX = True

try:
    from zopyx.txng3 import stemmer
except ImportError:
    USE_ZOPYX = False
   
def registerFilter(filter_object):
    global filters
    filters[filter_object.getName()] = filter_object

def applyFilter(name, text, options):
    return filters[name].transform(text, options)

def applyFilters(names, text, options):
    if options is None:
        options = {}
    for name in names:
        text = applyFilter(name, text, options)
    return text

class AllFilters(object):

    name = 'allfilters'

    def getName(self):
        return self.name

    def transform(self, text, options):
        tokenizers = ('normalizer', 'splitter', 'stopwords', 'stemmer')
        return applyFilters(tokenizers, text, options)


class BaseFilter(object):

    def setInitialState(self, text, options):
        if isinstance(text, list):
            if len(text) > 0:
                self.was_str = isinstance(text[0], str)
            else:
                self.was_str = False
        else:
            self.was_str = isinstance(text, str)

        if 'charset' in options:
            self.charset = options['charset']
        else:
            self.charset = 'utf8'

    def getFinalState(self, result):
        if isinstance(result, list):
            return [self.getFinalState(element) for element in result]
        if isinstance(result, unicode) and self.was_str:
            return result.encode(self.charset, "replace")
        elif isinstance(result, str) and not self.was_str:
            return result.decode(self.charset)
        return result

class TextSplitter(BaseFilter):

    name = 'splitter'

    char_list = ',;:/\'"#?!.-=+_`|()[]{}<>~&§%'
    uchar_list = u',;:/\'"#?!.-=+_`|()[]{}<>~&§%'

    def getName(self):
        return self.name

    def _cleanChar(self, char):
        """ XXX at this time, we'll just use a small
            black list we'll see later on adding a real normalizer
            for each language that does all this in one pass
        """
        if char not in self.char_list:
            return char
        return ' '

    def transform(self, text, options):
        # removing unwanted character
        self.setInitialState(text, options)
        if USE_ZOPYX:
            from zopyx.txng3.splitter import Splitter
            if 'treshold' in options:
                return self.getFinalState([word for word in
                                           Splitter(singlechar=0).split(text)])
            else:
                return self.getFinalState([word for word in
                                           Splitter().split(text)])

        if isinstance(text, unicode):
            char_list = self.uchar_list
        else:
            char_list = self.char_list

        for char in char_list:
            text = text.replace(char, ' ')
        result = text.split()

        if 'treshold' in options:
            treshold = options['treshold']
            return self.getFinalState([word.lower() for word in result
                                       if len(word) >= treshold])
        else:
            return self.getFinalState([word.lower() for word in result])

registerFilter(TextSplitter())

class StopWords(object):

    name = 'stopwords'
    treshold = 2

    def getName(self):
        return self.name

    def _getStopWords(self, lang=None):
        """ simple text file, but will
        probably move to a DB storage"""
        currentpath = os.path.dirname(__file__)
        basefilename = os.path.join(currentpath, 'stopwords.txt')
        if lang is not None:
            filename = os.path.join(currentpath, 'stopwords.%s.txt' % lang)
            if not os.path.exists(filename):
                filename = basefilename
        else:
            filename = basefilename

        return [word.strip() for word in open(filename).readlines()
                if not (word.startswith('#') or word.strip() == '')]

    def transform(self, text, options):
        if 'lang' not in options:
            return text

        if isinstance(text, unicode) or isinstance(text, str):
            text = text.split()

        treshold = options.get('treshold', self.treshold)
        lang = options['lang']
        stopwords = self._getStopWords(lang)
        return [word for word in text if (word not in stopwords
                and len(word) > treshold)]

registerFilter(StopWords())

class Normalizer(BaseFilter):

    name = 'normalizer'

    def getName(self):
        return self.name

    def _getNormalizedChars(self, lang=None):
        """ simple text file, but will
        probably move to a DB storage"""
        currentpath = os.path.dirname(__file__)
        basefilename = os.path.join(currentpath, 'normalized.txt')
        if lang is not None:
            filename = os.path.join(currentpath, 'normalized.%s.txt' % lang)
            if not os.path.exists(filename):
                filename = basefilename
        else:
            filename = basefilename

        words = [word.strip() for word in open(filename).readlines()
                 if not (word.startswith('#') or word.strip() == '')]

        result = {}
        for word in words:
            splited = word.split()
            result[splited[0].decode('utf8')] = splited[1]
        return result

    def _normalize(self, word, normalizer):
        def normalized(car):
            if car in normalizer:
                return normalizer[car]
            else:
                return car

        #normalized = [normalized(car) for car in word]
        for car in normalizer:
            word = word.replace(car, normalizer[car])

        return word
        #''.join(normalized)

    def transform(self, text, options):
        self.setInitialState(text, options)

        if 'lang' not in options:
            return text

        if isinstance(text, unicode) or isinstance(text, str):
            text = text.split()

        lang = options['lang']
        table = self._getNormalizedChars(lang)
        if not USE_ZOPYX:
            result = [self._normalize(word, table) for word in text]
        else:
            from zopyx.txng3 import normalizer
            result = normalizer.Normalizer(table.items()).normalize(text)

        return self.getFinalState(result)

registerFilter(Normalizer())

class Stemmer(BaseFilter):

    name = 'stemmer'
    charset = 'utf8'

    def getName(self):
        return self.name

    def getStemmerLanguage(self, lang):
        # pystemmer uses its own lang codes
        # XXX get the real ones
        langs = {'dn': 'danish', 'dt':'dutch', 'en': 'english',
                 'fr': 'french', 'de': 'german', 'it': 'italian',
                 'nw': 'norwegian', 'pr': 'porter',
                 'pg': 'portuguese', 'ru': 'russian', 'sp': 'spanish',
                 'sw': 'swedish'}
        if lang in langs:
            return langs[lang]
        return None

    def transform(self, text, options):
        self.setInitialState(text, options)

        if 'lang' not in options:
            return text

        if 'charset' not in options:
            charset = self.charset
        else:
            charset = options['charset']

        if isinstance(text, str) or isinstance(text, unicode):
            text = text.split()

        def right_type(result):
            if isinstance(result, unicode) and was_str:
                return result.encode(charset, "replace")
            elif isinstance(result, str) and not was_str:
                return result.decode(charset)
            return result

        def checktype(element):
            if isinstance(element, str):
                return element.decode(charset, 'replace')
            return element

        text = [checktype(element) for element in text]

        if not USE_ZOPYX:
            # module not available
            return self.getFinalState(text)
        
        from zopyx.txng3 import stemmer
        lang = self.getStemmerLanguage(options['lang'])
        if lang not in stemmer.availableStemmers():
            return self.getFinalState(text)

        stemmer = stemmer.Stemmer(lang)
        return self.getFinalState(stemmer.stem(text))

registerFilter(Stemmer())


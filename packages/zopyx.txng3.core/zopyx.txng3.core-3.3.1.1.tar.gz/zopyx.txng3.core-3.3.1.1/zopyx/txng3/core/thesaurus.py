###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import os, re
from zope.interface import implements
from zopyx.txng3.core.interfaces import IThesaurus

th_dir = os.path.join(os.path.dirname(__file__), 'data', 'thesaurus')

# match the encoding header
enc_reg = re.compile('#\s*encoding\s*=\s*([\w\-]+)')


def readThesaurus(language, casefolding=True):
    """ read thesaurus file """

    d = {}
    encoding = None

    filename = os.path.join(th_dir, '%s.txt' % language) 
    if not os.path.exists(filename):
        raise ValueError('No thesaurus file for "%s" found'% language)

    for l in open(filename):
        if not l.strip(): continue

        mo = enc_reg.match(l)
        if mo:
            encoding= mo.group(1)
            continue

        if l.startswith('#'): continue

        term, words = l.split(' ', 1)
        if encoding:
            term = unicode(term.strip(), encoding)
            words = [unicode(w.strip(), encoding) for w in words.split(',')]
            if casefolding:
                term = term.lower()
                words = [w.lower() for w in words]
            d[term] = words  
        else:
            raise ValueError("Thesaurus file %s has no 'encoding' parameter specified" % filename)

    return d


class Thesaurus:
        
    implements(IThesaurus)

    def __init__(self, language, casefolding=True):
        self._language = language
        self._data = {}  # word : [related terms]
        self._casefolding = casefolding
        self._loaded = False

    def _load(self):
        self._data = readThesaurus(self._language, self._casefolding)
        self._loaded = True

    def getTermsFor(self, word):
        """ return a list of similiar terms for a the given word in a given language"""
        if not self._loaded: self._load()
        if self._casefolding:
            word = word.lower()
        return self._data.get(word, None)

    def getLanguage(self):
        """ return the language of the thesaurus """
        return self._language

    def getContent(self):
        """ return the content of the thesaurus """
        if not self._loaded: self._load()
        return self._data

    def getSize(self):
        if not self._loaded: self._load()
        return len(self._data)


GermanThesaurus = Thesaurus('de')

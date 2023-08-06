#-*- coding: iso-8859-1 -*-

###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import sys, os, unittest

from zope.interface.verify import verifyClass
from zopyx.txng3.core.interfaces import IThesaurus
from zopyx.txng3.core.thesaurus import Thesaurus


class ThesaurusTests(unittest.TestCase):

    def testInterface(self):
        verifyClass(IThesaurus, Thesaurus)

    def testWithExistingLanguagesNoCasefolding(self):
        T = Thesaurus('de',False)
        self.assertEqual(T.getTermsFor(u'abrechnung'), None)
        self.assertEqual(T.getTermsFor(u'Abrechnung'), [u'Bilanz', u'Schlussrechnung'])

    def testWithExistingLanguagesWithCaseFolding(self):
        T = Thesaurus('de', True)
        self.assertEqual(T.getTermsFor(u'Abrechnung'), [u'bilanz', u'schlussrechnung'])
        self.assertEqual(T.getTermsFor(u'abrechnung'), [u'bilanz', u'schlussrechnung'])

    def testWithNonExistingThesaurus(self):
        T = Thesaurus('foobar')
        self.assertRaises(ValueError, T._load)

def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(ThesaurusTests))
    return s

def main():
   unittest.TextTestRunner().run(test_suite())

def debug():
   test_suite().debug()

def pdebug():
    import pdb
    pdb.run('debug()')
   
if __name__=='__main__':
   import sys
   if len(sys.argv) > 1:
      globals()[sys.argv[1]]()
   else:
      main()


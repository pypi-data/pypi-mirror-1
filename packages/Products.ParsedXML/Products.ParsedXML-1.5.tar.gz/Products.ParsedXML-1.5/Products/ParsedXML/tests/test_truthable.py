##############################################################################
#
# Copyright (c) 2001-2004 Zope Corporation and Contributors. All
# Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"tests to make sure that DOM objects support truth testing"

import os, sys
  
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ParsedXML')

from Products.ParsedXML import ParsedXML, DOM

from operator import truth

class WrappedTruthableTestCaseBase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.document = doc = ParsedXML.ParsedXML('foo')
        self.floating_element = doc.createElement("per")
        self.attached_element = doc.documentElement

class DOMTruthableTestCaseBase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.document = doc = DOM.theDOMImplementation.createDocument(
            None, 'root', None)
        self.floating_element = doc.createElement("per")
        self.attached_element = doc.documentElement

class TruthableTestCaseTests:

    def testFloatingTruthable(self):
        assert truth(self.floating_element) == 1

    def testDOMTruthable(self):
        assert truth(self.document) == 1
        assert truth(self.document.documentElement.parentNode) == 1

    def testAttachedTruthable(self):
        assert truth(self.attached_element) == 1

class DOMTruthableTestCase(DOMTruthableTestCaseBase,
                           TruthableTestCaseTests):
    pass

class WrappedTruthableTestCase(WrappedTruthableTestCaseBase,
                               TruthableTestCaseTests):
    pass

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(DOMTruthableTestCase))
        suite.addTest(unittest.makeSuite(WrappedTruthableTestCase))
        return suite

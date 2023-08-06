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

"Tests for garbage collection."
import os, sys
  
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
  
ZopeTestCase.installProduct('ParsedXML')

from Products.ParsedXML import ParsedXML, DOM

import App.ApplicationManager

class ReferenceTestCase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.dbman = App.ApplicationManager.DebugManager() 

    def getRefcounts(self, ob):
        "return number of refcounts for instances of ob's class"
        name = '%s.%s' % (ob.__module__, ob.__class__.__name__)
        for i in self.dbman.refcount():
            if i[1] == name:
                return i[0]
        return 0

# XXX this leaks 1 refcount when I test it with python2.1
##     def testParsedXMLCollect(self):
##         "see if refcounts from ParsedXML product init are released"
##         doc = ParsedXML.ParsedXML('foo')
##         refcounts1 = self.getRefcounts(doc)
##         doc = ParsedXML.ParsedXML('foo')
##         refcounts2 = self.getRefcounts(doc)
##         assert refcounts2 == refcounts1, (
##             "ParsedXML leaked %d refcounts" % (refcounts2 - refcounts1))

    def testDOMParseCollect(self):
        "see if refcounts from DOM parse creation are released"
        testDir = os.path.join(
            sys.modules['Products.ParsedXML'].__path__[0],
            'tests')
        filename = os.path.join(testDir, 'xml', '4ohn4ktj.xml')
        doc = DOM.ExpatBuilder.parse(filename)
        refcounts1 = self.getRefcounts(doc)
        doc = DOM.ExpatBuilder.parse(filename)        
        refcounts2 = self.getRefcounts(doc)
        assert refcounts2 == refcounts1, (
            "DOM parse leaked %d refcounts" % (refcounts2 - refcounts1))

    def testDOMCreateCollect(self):
        "see if refcounts from DOM creation are released"
        doc = DOM.theDOMImplementation.createDocument(None, 'doc', None)
        refcounts1 = self.getRefcounts(doc)
        doc = DOM.theDOMImplementation.createDocument(None, 'doc', None)
        refcounts2 = self.getRefcounts(doc)
        assert refcounts2 == refcounts1, (
            "DOM parse leaked %d refcounts" % (refcounts2 - refcounts1))

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(ReferenceTestCase))
        return suite

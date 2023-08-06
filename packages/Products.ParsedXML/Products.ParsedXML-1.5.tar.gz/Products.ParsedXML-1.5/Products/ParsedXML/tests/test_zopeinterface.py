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

"""Test that some Zope interfaces are supported properly."""

import os, sys
  
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ParsedXML')

from Products.ParsedXML import ParsedXML
from StringIO import StringIO

def assertSize(doc):
    "assert that the document size what's reported by len"
    gs = doc.get_size()
    l = len(str(doc))
    assert gs == l, "get_size reports %d while len reports %d" % (gs, l)
    
class GetSizeTestCase(ZopeTestCase.ZopeTestCase):
    "test that get_size works.  We only test on the persistent Document."

    def setUp(self):
        self.document = ParsedXML.ParsedXML('foo')

    def testGetSize(self):
        "assert that get_size works"
        assertSize(self.document)

    def testGetSizeParse(self):
        "assert that get_size works after a parse"        
        inStr = '<spam><eggs attr1="foo"><ham/>text</eggs></spam>'
        self.document.parseXML(StringIO(inStr))
        assertSize(self.document)        
        self.document.documentElement.parseXML(StringIO(inStr))
        assertSize(self.document)        

    def testGetSizeDOMMethods(self):
        "assert that get_size works after some DOM method manipulations"
        self.document.documentElement.appendChild(
            self.document.createElement('spam'))
        assertSize(self.document)
        self.document.documentElement.appendChild(
            self.document.createTextNode('spam'))
        assertSize(self.document)
        self.document.documentElement.appendChild(
            self.document.createTextNode('spam'))
        assertSize(self.document)
        self.document.normalize()
        assertSize(self.document)
        self.document.documentElement.setAttribute('eggs', 'ham')
        assertSize(self.document)

    def testGetSizeDOMAttributes(self):
        "assert that get_size works after some DOM attribute manipulations"
        self.document.documentElement.appendChild(
            self.document.createTextNode('spam'))
        self.document.documentElement.firstChild.data = "spamspamspam"
        assertSize(self.document)
        self.document.documentElement.setAttribute('eggs', 'ham')
        self.document.documentElement.attributes.item(0).value = 'spam'
        assertSize(self.document)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(GetSizeTestCase))
        return suite
    

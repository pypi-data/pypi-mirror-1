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

"test that the ParsedXML DOM object acquire implicitly"

import os, sys
  
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
  
ZopeTestCase.installProduct('ParsedXML')

from Products.ParsedXML import ParsedXML

# We currently have to have a Zope instance
# to mount; we need a persistent container & Zope traversal to acquire
# properly, because we don't want to acquire through the transient
# proxy objects.

def checkAcquire(aqer, aqee, name):
    "check that acquisition of name from aqee to aqer happens"
    assert hasattr(aqer, name)
    assert getattr(aqer, name) == getattr(aqee, name)
    assert getattr(aqer, name) is getattr(aqee, name)

def checkAcquireNot(aqer, aqee, name):
    "check that acquisition of name from aqee to aqer doesn't happen"
    assert getattr(aqer, name) != getattr(aqee, name)
    assert getattr(aqer, name) is not getattr(aqee, name)


class WrappedAcquisitionTestCase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        
        self.tmpId = 'TempParsedXMLUnitTestInstance'
        self.app._setObject(self.tmpId, ParsedXML.ParsedXML(self.tmpId))
        self.doc = getattr(self.app, self.tmpId)
        
        self.app.string = 'a string'
        self.app.firstChild = "a string that shouldn't be acquired"

        elt1 = self.doc.createElement('eggs')
        elt2 = self.doc.createElement('ham')
        self.doc.documentElement.appendChild(elt1)
        self.doc.documentElement.appendChild(elt2)
        self.doc.documentElement.setAttribute('color', 'green')

    def _acquisitionTest(self, DOMObj):
        checkAcquire(DOMObj, self.app, 'string')
        checkAcquireNot(DOMObj, self.app, 'firstChild')

    def testTraversalAcquisition(self):
        "make sure we can acquire through DOM traversal"
        self._acquisitionTest(self.doc)
        self._acquisitionTest(self.doc.documentElement)
        self._acquisitionTest(self.doc.documentElement.firstChild)
        self._acquisitionTest(self.doc.documentElement.firstChild.nextSibling)
        self._acquisitionTest(self.doc.documentElement.ownerDocument)
        self._acquisitionTest(self.doc.documentElement.getAttributeNode(
            'color'))

    def testMethodAcquisition(self):
        "make sure we acquire through proxied DOM methods"
        elt = self.doc.createElement('foo')
        self._acquisitionTest(self.doc.documentElement.appendChild(elt))

    def testNodeListAcquisition(self):
        "make sure we can acquire through a NodeList"
        self._acquisitionTest(self.doc.documentElement.childNodes.item(0))

    def testNamedNodeMapAcquisition(self):
        "make sure we can acquire through a NamedNodeMap"
        self._acquisitionTest(
            self.doc.documentElement.attributes.getNamedItem('color'))

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
 
        suite.addTest(unittest.makeSuite(WrappedAcquisitionTestCase))
        
        return suite


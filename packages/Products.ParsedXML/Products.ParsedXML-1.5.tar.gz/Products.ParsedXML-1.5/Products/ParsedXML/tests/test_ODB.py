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

"Test some ODB interactions."

import os, sys
  
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ParsedXML')

from Products.ParsedXML import ParsedXML

class ODBTestCase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.document = ParsedXML.ParsedXML('foo')

    def shotgunTpStuff(self, node):
        "assert that the Tp* functions work"
        children = node.childNodes
        tpVals = node.tpValues()

        for i in range(children.length):
            assert children.item(i).isSameNode(tpVals[i])
            
        for i in range(children.length):
            assert children.item(i).tpURL() == str(i)
            assert children.item(i).tpId() == str(i)

        for node in tpVals:
            self.shotgunTpStuff(node)
        
    def testTpStuff(self):
        "check that the Tp* functions work"
        self.document.documentElement.appendChild(
            self.document.createElement('zero'))
        self.document.documentElement.appendChild(
            self.document.createElement('one'))
        self.document.documentElement.firstChild.appendChild(
            self.document.createElement('zero-zero'))
        self.document.documentElement.firstChild.appendChild(
            self.document.createElement('zero-one'))

        self.shotgunTpStuff(self.document.documentElement)        

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(ODBTestCase))
        return suite

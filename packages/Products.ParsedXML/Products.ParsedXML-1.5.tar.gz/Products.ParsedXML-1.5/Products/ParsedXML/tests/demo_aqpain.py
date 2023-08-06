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

"""Test that checks the fragility of using acquistion wrappers to
indicate tree hierarchy.

The current implementation of the DOM uses acquisition wrappers to
store references to a node's parent node.  While this allows very
efficient access to the parent, it is fragile in the case of multiple
wrappers referring to the same node.  If client code holds two
wrappers for a node and modifies the node's position in the tree using
one of them, the other will store incorrect information on the shape
of the tree.

For acquisition to be used to adequately be used to present the
containment hierarchy for a node, a complete chain of wrappers would
need to be constructed each time a node is reparented, starting from
the outermost node in the ancestor chain.  Application code would need
to be wary that old references to a node are replaced by the new
wrapper.  The Python DOM API makes no such requirement at the present
time, nor should it need to.

This script shows a contrived example that exercises this DOM bug.
While this particular code is unlikely in real applications, the ease
with which multiple acquisition wrappers can be produced in more
complex application code is easy to see.

"""
import os, sys
  
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
  
ZopeTestCase.installProduct('ParsedXML')

from Products.ParsedXML.DOM.ExpatBuilder import ExpatBuilder

class AcquisitionPainTestCase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.doc = ExpatBuilder().parseString("<doc><e1/><e2/></doc>")

    def testParentReferenceIntegrity(self):
        e1a = self.doc.documentElement.firstChild
        e1b = self.doc.documentElement.firstChild
        e2 = e1b.nextSibling
        e2.appendChild(e1b)
        assert e1a.parentNode.isSameNode(e1b.parentNode), \
               "Two references to the same node return different parent nodes."

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(AcquisitionPainTestCase))
        return suite

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

import os, sys
  
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ParsedXML')

from Products.ParsedXML import DOM
from Products.ParsedXML.DOM import ExpatBuilder
from StringIO import StringIO
from domapi import DOMImplementationTestSuite

def DOMParseString(xml):
    file = StringIO(xml)
    return ExpatBuilder.parse(file)

def get_element_ids(node):
    result = []
    if node.nodeType == node.ELEMENT_NODE:
        result.append(node.elementId)
    for child in node.childNodes:
        result.extend(get_element_ids(child))
    return result

def check_unique_ids(node):
    element_ids = get_element_ids(node)
    element_ids.sort()
    last = element_ids[0]
    for element_id in element_ids[1:]:
        assert last != element_id,\
               'Found at least one double element_id: %s' % element_id
        last = element_id

class ElementIdTestCase(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        self.doc = DOMParseString('''
        <doc>
        <p>Test</p>
        <p>Another test</p>
        <p>Foo<sub/><sub2>hey</sub2></p>
        </doc>
        ''')

    def testElementIdsAfterParse(self):
        element_ids = get_element_ids(self.doc)
        for i in xrange(len(element_ids)):
            assert i == element_ids[i]
            
    def testElementIdsAfterAppend(self):
        element = self.doc.createElement('foo')
        self.doc.documentElement.appendChild(element)
        check_unique_ids(self.doc)

    def testElementIdsAfterAppend2(self):
        element = self.doc.createElement('foo')
        self.doc.documentElement.insertBefore(
            element, self.doc.documentElement.childNodes[0])
        check_unique_ids(self.doc)

    def testCloneNodeShallow(self):
        cloned = self.doc.documentElement.cloneNode(0)
        self.doc.documentElement.appendChild(cloned)
        check_unique_ids(self.doc)

    def testCloneNodeDeep(self):
        cloned = self.doc.documentElement.cloneNode(1)
        self.doc.documentElement.appendChild(cloned)
        check_unique_ids(self.doc)

    def testImportNodeShallow(self):
        otherdoc = DOMParseString('''
        <hey><some></some></hey>
        ''')
        imported = self.doc.importNode(
            otherdoc.documentElement, 0)
        self.doc.documentElement.appendChild(imported)
        check_unique_ids(self.doc)
        
    def testImportNodeDeep(self):
        otherdoc = DOMParseString('''
        <hey><some></some></hey>
        ''')
        imported = self.doc.importNode(
            otherdoc.documentElement, 1)
        self.doc.documentElement.appendChild(imported)
        check_unique_ids(self.doc)
        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(ElementIdTestCase))
        return suite

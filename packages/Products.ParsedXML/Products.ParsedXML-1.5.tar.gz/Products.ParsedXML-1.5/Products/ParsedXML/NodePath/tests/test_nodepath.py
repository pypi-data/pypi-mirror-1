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

import unittest
# needed to import NodePath module
import sys
sys.path.insert(0, '../..')

from NodePath import registry

def DOMParseString(xml):
    # FIXME: change this if using another DOM
    from StringIO import StringIO
    from Products.ParsedXML.DOM import ExpatBuilder
    file = StringIO(xml)
    return ExpatBuilder.parse(file)

class NodePathTestCase(unittest.TestCase):
    def setUp(self):
        doc = DOMParseString('''
        <doc>
        <chapter title="one">
        <p>This is a very trival <i>XML</i> document.</p>
        <p>We will test whether our node path facility works with it.</p>
        </chapter>
        <chapter title="two">
        <p>Here is a second chapter, which contains a list.</p>
        <list>
        <element>Foo</element>
        <element>Bar</element>
        <element>Baz</element>
        </list>
        </chapter>
        </doc>
        ''')
        self._doc = doc
        
    def _shotgun_check(self, top_node, node, scheme_name):
        path = registry.create_path(top_node, node, scheme_name)
        found = registry.resolve_path(top_node, path)
        assert found == node, ("Found %s with '%s', wanted %s" %
                               (found, path, node))
        cycled_path = registry.create_path(top_node, node, scheme_name)
        assert path == cycled_path, ("Cycled path %s found, wanted %s" %
                                     (cycled_path, path))
        for child in node.childNodes:
            self._shotgun_check(top_node, child, scheme_name)

    def _shotgun_check_robust(self, top_node, node):
        path = registry.create_path(top_node, node, 'robust')
        found = registry.resolve_path(top_node, path)
        assert found == node, ("Found %s with '%s', wanted %s" %
                               (found, path, node))
        # can't cycle path as words are selected randomly
        for child in node.childNodes:
            self._shotgun_check_robust(top_node, child)
  
    def checkChildPath(self):
        self._shotgun_check(self._doc, self._doc.documentElement, 'child')
        
    def checkElementIdPath(self):
        self._shotgun_check(self._doc, self._doc.documentElement, 'element_id')
        
    def checkRobustPath(self):
        self._shotgun_check_robust(self._doc, self._doc.documentElement)

    def checkEmptyPath(self):
        self.assertEquals('',
                          registry.create_path(self._doc, self._doc, 'child'))
        self.assertEquals('',
                          registry.create_path(self._doc, self._doc, 'element_id'))     
        #self.assertEquals('',
        #                  registry.create_path(self._doc, self._doc, 'robust'))
        found = registry.resolve_path(self._doc, '')
        self.assertEquals(self._doc, found)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NodePathTestCase, "check"))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == "__main__":
    main()
    

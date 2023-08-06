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

# FIXME: could test with Core DOM instead, do we want to?
from Products.ParsedXML import ParsedXML, PrettyPrinter
from StringIO import StringIO

def printElement(element):
    output = StringIO()
    PrettyPrinter.PrintVisitor(element, output)()
    return output.getvalue()

def checkOutput(wanted, got, message="Bad output"):
    assert wanted == got, \
           ("%s.  Wanted:\n%s[[EOF]]\nGot:\n%s[[EOF]]\n" 
            % (message, wanted, got))


class PrintTestBase(ZopeTestCase.ZopeTestCase):
    implementation = ParsedXML.theDOMImplementation

    def parse(self, xml):
        return ParsedXML.ParsedXML('foo', xml)


class PrintTestCase(PrintTestBase):

    def testAttrOrder(self):
        inStr = '<?xml version="1.0" ?>\n<doc a1="v1" a2="v2" a3="v3"/>\n'
        doc = self.parse(inStr)
        output = printElement(doc)

        checkOutput(inStr, output, "attribute order not preserved")

    def testDefaultAttrSkipped(self):
        inStr = '<!DOCTYPE doc [<!ELEMENT doc EMPTY>' \
                '<!ATTLIST doc a1 CDATA "v1">]><doc></doc>'
        outStr = '<?xml version="1.0" ?>\n<doc/>\n'
        doc = self.parse(inStr)
        output = printElement(doc)

        checkOutput(outStr, output, "default attribute printed")

    def testAttrEntRefExpansion(self):
        "entity references must be expanded in attributes"
        doc = self.implementation.createDocument(None, 'root', None)
        attr = doc.createAttribute("attrName")
        # this is a text string; &test; is not an entity reference,
        # so its & should be converted to the proper ref on printing,
        # as should the & and < and >.
        attr.value = "&test; &<>"
        # this reference should be expanded to the empty string
        attr.appendChild(doc.createEntityReference('foo'))
        doc.documentElement.setAttributeNode(attr)

        outStr = '<root attrName="&amp;test; &amp;&lt;&gt;"/>'
        output = printElement(doc.documentElement)
        checkOutput(outStr, output, "improper attr entity expansion")

    def testTextEntRefExpansion(self):
        "only some entity references should be expanded in text"
        doc = self.implementation.createDocument(None, 'root', None)
        # &< must be converted to the proper reference; > should not.
        text = doc.createTextNode("&<>]]>")
        outStr = '&amp;&lt;>]]&gt;'
        output = printElement(text)
        checkOutput(outStr, output, "improper text entity expansion")

    #TODO: check for expansion of entity refs in other contexts;
    #currently we're expanding aggressively, but it's not a priority
    #because the parser gets to play around with refs too

class Lvl2PrintTestCase(PrintTestBase):

    def testNamespacePrint(self):
        outStr = '<?xml version="1.0" ?>\n' \
                    '<bar xmlns:foo="uri:foo">\n' \
                    '<foo:baz/></bar>\n'
        doc = self.parse(outStr)
        output = printElement(doc)
        checkOutput(outStr, output)

    def testNamespaceAttrOrder(self):
        inStr = ('<?xml version="1.0" ?>\n'
                  '<doc>'
                  '  <fooE xmlns="defaultURL" xmlns:oneN="oneURL" '
                          'xmlns:twoN="twoURL" xmlns:threeN="threeURL"/>'
                  '</doc>\n')
        doc = self.parse(inStr)
        output = printElement(doc)
        checkOutput(inStr, output, "attribute order not preserved")


    def testHierarchicalElementNamespacePrint(self):
        # print new ns, don't print ns printed by ancestor
        outStr = ('<?xml version="1.0" ?>\n'
                  '<fooN:fooE xmlns:fooN="fooURL">'
                  '  <barN:barE xmlns:barN="barURL">'
                  '  <fooN:fooE>'
                  '    <fooN:fooE/>'
                  '  </fooN:fooE>'
                  '  </barN:barE>'
                  '</fooN:fooE>\n')
        doc = self.parse(outStr)
        output = printElement(doc)
        checkOutput(outStr, output)

    def testDefaultNamespacePrint(self):
        outStr = ('<?xml version="1.0" ?>\n'
                  '<fooE xmlns="defaultURL"><fooE xmlns="barURL"/>'
                  '</fooE>\n')
        doc = self.parse(outStr)
        output = printElement(doc)
        checkOutput(outStr, output)

    def testDefaultAndPrefixNamespacePrint(self):
        # try and tickle a namespace printing bug
        outStr = ('<?xml version="1.0" ?>\n'
                  '<doc>'
                  '  <fooE xmlns="defaultURL" xmlns:fooN="fooURL" '
                          'xmlns:barN="barUrl" xmlns:bazN="bazUrl">'
                  '  <barE bazN:bazE="baz"/>'
                  '  <bazN:bazE/>'
                  '  <quxN xmlns:quxE="quxUrl"/>'
                  '  <quxN xmlns:quxE="quxUrl" bazN:bazE="baz"/>'
                  '  </fooE>'
                  '</doc>\n')
        doc = self.parse(outStr)
        output = printElement(doc)
        checkOutput(outStr, output)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(PrintTestCase))
        suite.addTest(unittest.makeSuite(Lvl2PrintTestCase))
        return suite

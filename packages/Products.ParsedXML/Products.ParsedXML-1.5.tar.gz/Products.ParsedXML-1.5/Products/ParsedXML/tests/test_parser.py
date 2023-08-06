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

from domapi.Base import checkAttribute

from Products.ParsedXML import ParsedXML, ExtraDOM, DOM, PrettyPrinter
from StringIO import StringIO

# the printer is a convenient way to track changes made by the parser
def printElement(element):
    output = StringIO()
    PrettyPrinter.PrintVisitor(element, output)()
    return output.getvalue()

def checkOutput(wanted, got, message="Bad output"):
    assert wanted == got, \
           ("%s.  Wanted:\n%s[[EOF]]\nGot:\n%s[[EOF]]\n" 
            % (message, wanted, got))

class ParsedXMLTestCaseBase(ZopeTestCase.ZopeTestCase):

    def shotgunParse(self, doc, namespaces = 1):
        "parse and print every node in the document"
        # first we parse a print of the document, to avoid errors from
        # comparing before and after infospace-lossyness
        docStr = StringIO(ExtraDOM.writeStream(doc).getvalue().encode('UTF-8'))
        doc = ExtraDOM.parseFile(doc, docStr, namespaces)
        from Products.ParsedXML.DOM.Traversal import NodeFilter
        nodes = []
        iterator = doc.createNodeIterator(doc, NodeFilter.SHOW_ALL, None, 0)
        # parse from the bottom up because parsing a node replaces children
        # it'd be simpler to not store a list of nodes, but this way we
        # miss possible iterator bugs
        while iterator.nextNode():
            pass
        node = iterator.previousNode()
        while node:
            if node.nodeType != DOM.Core.Node.DOCUMENT_TYPE_NODE:
                nodes.append(node)
            node = iterator.previousNode()
        # parse print of each node and compare printed doc, node.
        for node in nodes:
            docStrIn = ExtraDOM.writeStream(doc).getvalue().encode('UTF-8')
            nodeStrIn = ExtraDOM.writeStream(node).getvalue().encode('UTF-8')
            ExtraDOM.parseFile(node, StringIO(nodeStrIn), namespaces)
            nodeStrOut = ExtraDOM.writeStream(node).getvalue().encode('UTF-8')
            docStrOut = ExtraDOM.writeStream(doc).getvalue().encode('UTF-8')
            checkOutput(nodeStrIn, nodeStrOut,
                        "parsing print of node %s changed node print" % node)
            checkOutput(docStrIn, docStrOut,
                        "parsing print of node %s changed doc print" % node)

class ParseOasisXMLTestSaTestCase(ParsedXMLTestCaseBase):

    # set this to true to generate new output files
    generate = 0

    def testParse001(self):
        self._checkParse("001.xml")
    def testParse002(self):
        self._checkParse("002.xml")
    def testParse003(self):
        self._checkParse("003.xml")
    def testParse004(self):
        self._checkParse("004.xml")
    def testParse005(self):
        self._checkParse("005.xml")
    def testParse006(self):
        self._checkParse("006.xml")
    def testParse007(self):
        self._checkParse("007.xml")
    def testParse008(self):
        self._checkParse("008.xml")
    def testParse009(self):
        self._checkParse("009.xml")
    def testParse010(self):
        self._checkParse("010.xml")
    def testParse011(self):
        self._checkParse("011.xml")
    # This test fails when we use namespaces to determine valid tagnames.
    # We want to parse namespaces always.
    #def testParse012(self):
    #    self._checkParse("012.xml")
    def testParse013(self):
        self._checkParse("013.xml")
    def testParse014(self):
        self._checkParse("014.xml")
    def testParse015(self):
        self._checkParse("015.xml")
    def testParse016(self):
        self._checkParse("016.xml")
    def testParse017(self):
        self._checkParse("017.xml")
    def testParse018(self):
        self._checkParse("018.xml")
    def testParse019(self):
        self._checkParse("019.xml")
    def testParse020(self):
        self._checkParse("020.xml")
    def testParse021(self):
        self._checkParse("021.xml")
    def testParse022(self):
        self._checkParse("022.xml")
##     def testParse023(self):
##         self._checkParse("023.xml")
##     def testParse024(self):
##         self._checkParse("024.xml")
    def testParse025(self):
        self._checkParse("025.xml")
    def testParse026(self):
        self._checkParse("026.xml")
    def testParse027(self):
        self._checkParse("027.xml")
    def testParse028(self):
        self._checkParse("028.xml")
    def testParse029(self):
        self._checkParse("029.xml")
    def testParse030(self):
        self._checkParse("030.xml")
    def testParse031(self):
        self._checkParse("031.xml")
    def testParse032(self):
        self._checkParse("032.xml")
    def testParse033(self):
        self._checkParse("033.xml")
    def testParse034(self):
        self._checkParse("034.xml")
    def testParse035(self):
        self._checkParse("035.xml")
    def testParse036(self):
        self._checkParse("036.xml")
    def testParse037(self):
        self._checkParse("037.xml")
    def testParse038(self):
        self._checkParse("038.xml")
    def testParse039(self):
        self._checkParse("039.xml")
    def testParse040(self):
        self._checkParse("040.xml")
    def testParse041(self):
        self._checkParse("041.xml")
    def testParse042(self):
        self._checkParse("042.xml")
    def testParse043(self):
        self._checkParse("043.xml")
    def testParse044(self):
        self._checkParse("044.xml")
    def testParse045(self):
        self._checkParse("045.xml")
    def testParse046(self):
        self._checkParse("046.xml")
    def testParse047(self):
        self._checkParse("047.xml")
    def testParse048(self):
        self._checkParse("048.xml")
    def testParse049(self):
        self._checkParse("049.xml")
    def testParse050(self):
        self._checkParse("050.xml")     
##     def testParse051(self):
##        self._checkParse("051.xml")
    def testParse052(self):
        self._checkParse("052.xml")
##     def testParse053(self):
##         self._checkParse("053.xml")
    def testParse054(self):
        self._checkParse("054.xml")
    def testParse055(self):
        self._checkParse("055.xml")
    def testParse056(self):
        self._checkParse("056.xml")
    def testParse057(self):
        self._checkParse("057.xml")
    def testParse058(self):
        self._checkParse("058.xml")
    def testParse059(self):
        self._checkParse("059.xml")
    def testParse060(self):
        self._checkParse("060.xml")
    def testParse061(self):
        self._checkParse("061.xml")
    def testParse062(self):
        self._checkParse("062.xml")
##     def testParse063(self):
##         self._checkParse("063.xml")
    def testParse064(self):
        self._checkParse("064.xml")
##     def testParse065(self):
##         self._checkParse("065.xml")
##     def testParse066(self):
##         self._checkParse("066.xml")
    def testParse067(self):
        self._checkParse("067.xml")
##     def testParse068(self):
##         self._checkParse("068.xml")
##     def testParse069(self):
##          self._checkParse("069.xml")
    def testParse070(self):
        self._checkParse("070.xml")
    def testParse071(self):
        self._checkParse("071.xml")
    def testParse072(self):
        self._checkParse("072.xml")
    def testParse073(self):
        self._checkParse("073.xml")
    def testParse074(self):
        self._checkParse("074.xml")
    def testParse075(self):
        self._checkParse("075.xml")
##     def testParse076(self):
##         self._checkParse("076.xml")
    def testParse077(self):
        self._checkParse("077.xml")
    def testParse078(self):
        self._checkParse("078.xml")
    def testParse079(self):
        self._checkParse("079.xml")
    def testParse080(self):
        self._checkParse("080.xml")
    def testParse081(self):
        self._checkParse("081.xml")
    def testParse082(self):
        self._checkParse("082.xml")
    def testParse083(self):
        self._checkParse("083.xml")
    def testParse084(self):
        self._checkParse("084.xml")
##     def testParse085(self):
##         self._checkParse("085.xml")
##     def testParse086(self):
##         self._checkParse("086.xml")
##     def testParse087(self):
##         self._checkParse("087.xml")
##     def testParse088(self):
##         self._checkParse("088.xml")
##     def testParse089(self):
##         self._checkParse("089.xml")
##     def testParse090(self):
##         self._checkParse("090.xml")
##     def testParse091(self):
##         self._checkParse("091.xml")
    def testParse092(self):
        self._checkParse("092.xml")
    def testParse093(self):
        self._checkParse("093.xml")
    def testParse094(self):
        self._checkParse("094.xml")
    def testParse095(self):
        self._checkParse("095.xml")
    def testParse096(self):
        self._checkParse("096.xml")
    def testParse097(self):
        self._checkParse("097.xml")
    def testParse098(self):
        self._checkParse("098.xml")
    def testParse099(self):
        self._checkParse("099.xml")
##     def testParse100(self):
##         self._checkParse("100.xml")
##     def testParse101(self):
##         self._checkParse("101.xml")
    def testParse102(self):
        self._checkParse("102.xml")
    def testParse103(self):
        self._checkParse("103.xml")
    def testParse104(self):
        self._checkParse("104.xml")
    def testParse105(self):
        self._checkParse("105.xml")
    def testParse106(self):
        self._checkParse("106.xml")
    def testParse107(self):
        self._checkParse("107.xml")
##     def testParse108(self):
##         self._checkParse("108.xml")
    def testParse109(self):
        self._checkParse("109.xml")
##     def testParse110(self):
##         self._checkParse("110.xml")
    def testParse111(self):
        self._checkParse("111.xml")
    def testParse112(self):
        self._checkParse("112.xml")
    def testParse113(self):
        self._checkParse("113.xml")
##     def testParse114(self):
##         self._checkParse("114.xml")
##     def testParse115(self):
##         self._checkParse("115.xml")
##     def testParse116(self):
##         self._checkParse("116.xml")
##     def testParse117(self):
##         self._checkParse("117.xml")
##     def testParse118(self):
##         self._checkParse("118.xml")

    def testParse119(self):
        self._checkParse("119.xml")

    def _checkParse(self, iterFileName):
        testDir = os.path.join(sys.modules['Products.ParsedXML'].__path__[0],
            'tests')
        saDir = os.path.join(testDir, 'xml', 'conf', 'xmltest', 'sa')
        outDir = os.path.join(saDir, 'ParsedXMLTestOut')

        # Read the test input
        inFilename = os.path.join(saDir, iterFileName)
        inFile = open(inFilename).read()
        doc = ParsedXML.ParsedXML('foo', inFile)

        # Read the output to test against
        outFilename = os.path.join(outDir, iterFileName)
        outFile = open(outFilename).read()
        # FIXME: if the next line is enabled, the tests will succeed
        # with python 2.1. Unfortunately the whole testsuite will
        # segfault at about test 23 (it'll vary)
        outFile = unicode(outFile, 'utf-8')
        
        # Print the DOM, and compare against the expected output.
        output = printElement(doc)
        
        # All line separators are supposed to normalize to Unix-style
        # (XML 1.0, section 2.11).
##         outFile = string.replace(outFile, "\r\n", "\n")
##         outFile = string.replace(outFile, "\r", "\n")

        if self.generate:
            # re-generate the expected output file, but only if it changed
            if outFile != output:
                fp = open(outFilename, "w")
                fp.write(output)
                fp.close()
        else:
            checkOutput(outFile, output)
            self.shotgunParse(doc.getDOMObj())

class ParseTestCase(ParsedXMLTestCaseBase):

    def testParseException(self):
        "assert exception & exception args are correct"
        from xml.parsers import expat
        text = "<doc>\nfoobar<</doc>" # parse error line 2 column 7
        try:
            ParsedXML.ParsedXML('foo', text)
        except expat.error, e:
            assert e.lineno == 2, (
                "parse exception give wrong line number.  Wanted %s got %s"
                % (2, e.lineno))
            assert e.offset == 7, (
                "parse exception give wrong column number.  Wanted %s got %s"
                % (7, e.offset))
        else:
            assert 0, "parse of malformed XML doesn't raise properly"

    def testSubnodeParseException(self):
        "assert exception & exception args are correct"        
        from xml.parsers import expat
        docText = "<doc><child/></doc>"
        subText = "<child>\nfoobar<</child>" # parse error line 2 column 7
        doc = ParsedXML.ParsedXML('foo', docText)
        try:
            doc.documentElement.firstChild.parseXML(StringIO(subText))
        except expat.error, e:
            assert e.lineno == 2, (
                "parse exception gives wrong line number.  Wanted %s, got %s"
                % (2, e.lineno))
            assert e.offset == 7, (
                "parse exception gives wrong offset.  Wanted %s, got %s"
                % (7, e.offset))
        else:
            assert 0, "parse of malformed XML doesn't raise properly"

class Lvl2ParseTestCase(ParsedXMLTestCaseBase):

    def testNamespaceAttrOfDocumentElement(self):
        """we should be able to parse an element that uses a namespace
        declared on the element itself"""
        inStr = '<?xml version="1.0" ?>\n' \
                '<foo:bar xmlns:foo="uri:test_namespace"/>\n'
        doc = ParsedXML.ParsedXML('foo', inStr)
        self.shotgunParse(doc.getDOMObj())        

    def testNamespaceAttrOfElement(self):
        """we should be able to parse an element that uses a namespace
        declared on the element itself"""
        inStr = '<?xml version="1.0" ?>\n' \
                '<doc><foo:bar xmlns:foo="uri:test_namespace"/></doc>\n'
        doc = ParsedXML.ParsedXML('foo', inStr)
        self.shotgunParse(doc.getDOMObj())        

    def testSubnodeAncestorNamespace(self):
        """we should be able to parse a subtree that uses a namespace
        declared on an ancestor that we don't parse"""
        inStr = ('<?xml version="1.0" ?>\n'
                 '<doc><spam xmlns:spamNs="uri:test_namespace">'
                 '<eggs><spamNs:ham spamNs:foo="bar"/></eggs>'
                 '</spam></doc>\n')
        doc = ParsedXML.ParsedXML('foo', inStr)
        self.shotgunParse(doc.getDOMObj())

    def testSubnodeParseXMLNamepsaceDecl(self):
        """Check that we can parse at a subnode with an xml ns decl attr, and
        that parsing a subnode's output doesn't change the document.
        The external entity parser that the fragment builder uses likes
        to add this namespace, so we want to make sure we don't break
        anything that uses it."""
        inStr = '<spam xmlns:xml="http://www.w3.org/XML/1998/namespace"/>'
        doc = ParsedXML.ParsedXML('foo', inStr)
        self.shotgunParse(doc.getDOMObj())

    def testSubnodeParseXMLNamepsace(self):
        """Check that we can parse at a subnode with an xml ns attr, and
        that parsing a subnode's output doesn't change the document.
        The external entity parser that the fragment builder uses likes
        to add this namespace, so we want to make sure we don't break
        anything that uses it."""
        # we should use a real XML name here, it's not an error if the
        # parser notices that we're abusign the xml namespace
        inStr = '<spam xml:spam="spam"/>'
        doc = ParsedXML.ParsedXML('foo', inStr)
        self.shotgunParse(doc.getDOMObj())

    def testXMLNSPrefixParse(self):
        "check that xmlns prefix attrs are parsed properly"
        inStr = '<doc xmlns:spamNS="uri:test_namespace"/>'
        doc = ParsedXML.ParsedXML('foo', inStr)
        attr = doc.documentElement.attributes.item(0)
        checkAttribute(attr, 'prefix', 'xmlns')
        checkAttribute(attr, 'localName', 'spamNS')
        checkAttribute(attr, 'namespaceURI', 'http://www.w3.org/2000/xmlns/')
        checkAttribute(attr, 'value', 'uri:test_namespace')        

    def testXMLNSParse(self):
        "check that xmlns attrs are parsed properly"
        inStr = '<doc xmlns="uri:test_namespace"/>'
        doc = ParsedXML.ParsedXML('foo', inStr)
        attr = doc.documentElement.attributes.item(0)
        checkAttribute(attr, 'prefix', 'xmlns')
        checkAttribute(attr, 'localName', None)
        checkAttribute(attr, 'namespaceURI', 'http://www.w3.org/2000/xmlns/')
        checkAttribute(attr, 'value', 'uri:test_namespace')        

    def testNoNSParse(self):
        """check that attrs parsed with no NS but with NS aware parse
        can be retrieved with NS of None"""
        inStr = '<doc version="1.0"/>'
        doc = ParsedXML.ParsedXML('foo', inStr)
        assert doc.documentElement.getAttributeNS(None, 'version'), (
            "NS-free attribute not gotten by NS-free getAttributeNS")

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(ParseOasisXMLTestSaTestCase))
        suite.addTest(unittest.makeSuite(ParseTestCase))
        suite.addTest(unittest.makeSuite(Lvl2ParseTestCase))
        return suite



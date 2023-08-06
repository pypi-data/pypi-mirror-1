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

"""Constructor for ParsedXML.DOM, based on a SAX parser."""

import os
import urllib
import xml.sax


class SAXBuilder(xml.sax.ContentHandler):
    _locator = None
    document = None
    documentElement = None

    def __init__(self, documentFactory=None):
        self.documentFactory = documentFactory
        self._ns_contexts = [{}] # contains uri -> prefix dicts
        self._current_context = self._ns_contexts[-1]

    def install(self, parser):
        parser.setContentHandler(self)

    def setDocumentLocator(self, locator):
        self._locator = locator

    def startPrefixMapping(self, prefix, uri):
        self._ns_contexts.append(self._current_context.copy())
        self._current_context[uri] = prefix or None

    def endPrefixMapping(self, prefix):
        self._current_context = self._ns_contexts.pop()

    def _make_qname(self, uri, localname, tagname):
        # When using namespaces, the reader may or may not
        # provide us with the original name. If not, create
        # *a* valid tagName from the current context.
        if uri:
            if tagname is None:
                prefix = self._current_context.get(uri)
                if prefix:
                    tagname = "%s:%s" % (prefix, localname)
                else:
                    tagname = localname
        else:
            tagname = localname
        return tagname

    def startElementNS(self, name, tagName, attrs):
        uri, localname = name
        tagName = self._make_qname(uri, localname, tagName)
        if not self.document:
            factory = self.documentFactory
            self.document = factory.createDocument(uri or None, tagName, None)
            node = self.document.documentElement
        else:
            if uri:
                node = self.document.createElementNS(uri, tagName)
            else:
                node = self.document.createElement(localname)
            self.curNode.appendChild(node)
        self.curNode = node

        for aname, value in attrs.items():
            a_uri, a_localname = aname
            if a_uri:
                qname = "%s:%s" % (self._current_context[a_uri], a_localname)
                node.setAttributeNS(a_uri, qname, value)
            else:
                attr = self.document.createAttribute(a_localname)
                node.setAttribute(a_localname, value)

    def endElementNS(self, name, tagName):
        self.curNode = self.curNode.parentNode

    def startElement(self, name, attrs):
        if self.documentElement is None:
            factory = self.documentFactory
            self.document = factory.createDocument(None, name, None)
            node = self.document.documentElement
            self.documentElement = 1
        else:
            node = self.document.createElement(name)
            self.curNode.appendChild(node)
        self.curNode = node

        for aname, value in attrs.items():
            node.setAttribute(aname, value)

    def endElement(self, name):
        self.curNode = self.curNode.parentNode

    def comment(self, s):
        node = self.document.createComment(s)
        self.curNode.appendChild(node)

    def processingInstruction(self, target, data):
        node = self.document.createProcessingInstruction(target, data)
        self.curNode.appendChild(node)

    def ignorableWhitespace(self, chars):
        node = self.document.createTextNode(chars)
        self.curNode.appendChild(node)

    def characters(self, chars):
        node = self.document.createTextNode(chars)
        self.curNode.appendChild(node)


def parse(file, namespaces=1, dom=None, parser=None):
    if not parser:
        parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, namespaces)
    if not dom:
        import Core
        dom = Core.theDOMImplementation
    if isinstance(file, type('')):
        try:
            fp = open(file)
        except IOError, e:
            if e.errno != errno.ENOENT:
                raise
            fp = urllib.urlopen(file)
            systemId = file
        else:
            # Ugh!  Why doesn't urllib.pathname2url() do something useful?
            systemId = "file://" + os.path.abspath(file)
    else:
        source = xml.sax.InputSource()
        fp = file
        try:
            systemId = file.name
        except AttributeError:
            systemId = None
    source = xml.sax.InputSource(file)
    source.setByteStream(fp)
    source.setSystemId(systemId)
    builder = SAXBuilder(documentFactory=dom)
    builder.install(parser)
    parser.parse(source)
    if fp is not file:
        fp.close()
    return builder.document

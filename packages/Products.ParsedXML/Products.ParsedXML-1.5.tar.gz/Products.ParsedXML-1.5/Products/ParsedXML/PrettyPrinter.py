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
import re
from DOM.Core import Node, XMLNS_NS, XML_NS
import sys
from StringIO import StringIO

# an XML printer which:
#   * can do pretty printing, optionally
#   * as opposed to the one defined in Printer.py, actually should
#     be less buggy

class PrintVisitor:
    
    def __init__(self, root, stream=sys.stdout, encoding=None,
                 entityReferenceExpansion=1,
                 prettyPrint=0, indentLevel=2):

        self.root = root
        self.stream = stream
        self.encoding = encoding
        self.entityReferenceExpansion = entityReferenceExpansion
        self.prettyPrint = prettyPrint
        self.indent = 0
        self.indentLevel = indentLevel
        
        self.nodeType2method = { 
            Node.ELEMENT_NODE: self.renderElement,
            Node.ATTRIBUTE_NODE: self.renderAttr,
            Node.TEXT_NODE: self.renderText,
            Node.CDATA_SECTION_NODE: self.renderCDATASection,
            Node.ENTITY_REFERENCE_NODE: self.renderEntityReference,
            Node.ENTITY_NODE: self.renderEntity,
            Node.PROCESSING_INSTRUCTION_NODE:\
            self.renderProcessingInstruction,
            Node.COMMENT_NODE: self.renderComment,
            Node.DOCUMENT_NODE: self.renderDocument,
            Node.DOCUMENT_TYPE_NODE: self.renderDocumentType,
            Node.DOCUMENT_FRAGMENT_NODE: self.renderDocumentFragment,
            Node.NOTATION_NODE: self.renderNotation,
        }

    def renderAll(self):
        return self.render(self.stream, self.root)

    __call__ = renderAll
    
    def render(self, f, node):
        self.nodeType2method[node.nodeType](f, node)
        
    def renderElement(self, f, node):
        if self.prettyPrint:
            f.write(" " * self.indent * self.indentLevel)
        f.write("<")
        f.write(node.tagName)
        for attribute in node.attributes.values():
            self.renderAttr(f, attribute)
        if not node.hasChildNodes():
            f.write('/>')
            if self.prettyPrint:
                f.write("\n")
        else:
            f.write('>')
            prettyPrint = self.prettyPrint

            stream = f
            if prettyPrint:
                f.write("\n")                    
                no_indentation = 0
                for child in node.childNodes:
                    if (child.nodeType == Node.TEXT_NODE and
                        child.data.strip() != ''):
                        no_indentation = 1
                        break
                if no_indentation:
                    stream = StringIO()
                    self.prettyPrint = 0
                self.indent += 1
                
            for child in node.childNodes:
                self.render(stream, child)

            self.prettyPrint = prettyPrint
            
            if prettyPrint:
                if no_indentation:
                    f.write(indentBlock(
                        stream.getvalue().strip(),
                        self.indent * self.indentLevel, 70))
                    f.write('\n')
                self.indent -= 1
                
                f.write(" " * self.indent * self.indentLevel)
            f.write("</%s>" % node.tagName)
            if self.prettyPrint:
                f.write("\n")

    def renderAttr(self, f, node):
        if not node.specified:
            return
        text, delimiter = _translateCdataAttr(node.value)
        f.write(" %s=%s%s%s" % (node.name,
                                delimiter, text, delimiter))
        
    def renderText(self, f, node):
        data = node.data
        if self.prettyPrint:
            data = node.data.strip()
            if data == "":
                return
            data = indentBlock(data, self.indent * self.indentLevel, 70)
        f.write(_translateCdata(data))
        if self.prettyPrint:
            f.write('\n')
            
    def renderCDATASection(self, f, node):
        f.write("<![CDATA[")
        f.write(node.data.replace("]]>", "]]]><![CDATA[]>"))
        f.write("]]>")

    def renderEntityReference(self, f, node):
        f.write('&')
        f.write(node.nodeName)
        f.write(';')

    def renderEntity(self, f, node):
        st = "<!ENTITY " + node.nodeName
        if not node.systemId:
            # internal entity
            s = node.firstChild.data
            st = '%s "%s"' % (st, _translateCdata(s))
        if node.publicId:
            st = st + ' PUBLIC "%s"' % node.publicId
            if node.systemId:
                st = '%s "%s"' % (st, node.systemId)
        elif node.systemId:
            st = st + ' SYSTEM "%s"' % node.systemId
        if node.notationName:
            st = st + ' NDATA %s' % node.notationName
        f.write(st + '>\n')
    
    def renderProcessingInstruction(self, f, node):
        f.write('<?')
        f.write(node.target + ' ')
        f.write(node.data)
        f.write('?>')

    def renderComment(self, f, node):
        f.write('<!--')
        f.write(node.data)
        f.write('-->')

    def renderDocument(self, f, node):    
        f.write('<?xml version="1.0" ?>\n')
        #if self.encoding:
        #    f.write(' encoding="%s"' % self.encoding)
        #f.write(' ?>\n')
        for child in node.childNodes:
            self.render(f, child)
        f.write('\n')
        
    def renderDocumentType(self, f, node):
        if (not node.entities.length and
            not node.notations.length and
            not node.systemId):
            return

        f.write("<!DOCTYPE ")
        f.write(node.name)

        if node.systemId:
            if node.publicId:
                if '"' not in node.publicId:
                    f.write(' PUBLIC "' + node.publicId + '" ')
                else:
                    f.write(" PUBLIC '" + node.publicId + "' ")
            else:
                f.write(' SYSTEM ')

            if '"' not in node.systemId:
                f.write('"' + node.systemId + '"')
            else:
                f.write("'" + node.systemId + "'")

        if node.internalSubset:
            f.write(" [%s]" % node.internalSubset)
        elif node.entities.length or node.notations.length:
            f.write(' [\n')
            for i in range(node.entities.length):
                self.render(f, node.entities.item(i))
            for i in range(node.notations.length):
                self.render(f, node.notations.item(i))
            f.write(']')
        f.write('>\n')
       
    def renderNotation(self, f, node):
        st = "<!NOTATION %s" % node.nodeName
        if node.publicId:
            st = st + ' PUBLIC "%s"' % node.publicId
            if node.systemId:
                st = '%s "%s"' % (st, node.systemId)
        elif node.systemId:
            st = st + ' SYSTEM "%s"' % node.systemId
        f.write(st + '>\n')

    def renderDocumentFragment(self, f, node):
        for child in node.childNodes:
            self.render(f, child)
            
# regexps used by _translateCdata(),
# made global to compile once.
# see http://www.xml.com/axml/target.html#dt-character
ILLEGAL_LOW_CHARS = '[\x01-\x08\x0B-\x0C\x0E-\x1F]'
ILLEGAL_HIGH_CHARS = '\xEF\xBF[\xBE\xBF]'
# Note: Prolly fuzzy on this, but it looks as if characters from the
# surrogate block are allowed if in scalar form, which is encoded in UTF8 the
# same was as in surrogate block form
XML_ILLEGAL_CHAR_PATTERN = re.compile(
    '%s|%s' % (ILLEGAL_LOW_CHARS, ILLEGAL_HIGH_CHARS))
# the characters that we will want to turn into entrefs
# We must do so for &, <,  and > following ]].
# The xml parser has more leeway, but we're not the parser.
# http://www.xml.com/axml/target.html#dt-chardata
# characters that we must *always* turn to entrefs:
g_cdataCharPatternReq = re.compile('[&<]|]]>')
g_charToEntityReq = {
    '&': '&amp;',
    '<': '&lt;',
    ']]>': ']]&gt;',
    }
# characters that we must turn to entrefs in attr values:
g_cdataCharPattern = re.compile('[&<>"\']|]]>')
g_charToEntity = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&apos;',
    ']]>': ']]&gt;',
    }

def _translateCdata(characters, allEntRefs = None):
    """Translate characters into a legal format."""
    if not characters:
        return ''
    if allEntRefs: # translate all chars to entrefs; for attr value
        if g_cdataCharPattern.search(characters):
            new_string = g_cdataCharPattern.subn(
                lambda m, d=g_charToEntity: d[m.group()],
                characters)[0]
        else:
            new_string = characters
    else: # translate only required chars to entrefs
        if g_cdataCharPatternReq.search(characters):
            new_string = g_cdataCharPatternReq.subn(
                lambda m, d=g_charToEntityReq: d[m.group()],
                characters)[0]
        else:
            new_string = characters
    if XML_ILLEGAL_CHAR_PATTERN.search(new_string):
        new_string = XML_ILLEGAL_CHAR_PATTERN.subn(
            lambda m: '&#%i;' % ord(m.group()),
            new_string)[0]
    return new_string
    
def _translateCdataAttr(characters):
    """
    Translate attribute value characters into a legal format;
    return the value and the delimiter used.
    """
    if not characters:
        return '', '"'
    if '"' not in characters or "'" in characters:
        delimiter = '"'
        new_chars = _translateCdata(characters, allEntRefs = 1)
        new_chars = re.sub("&apos;", "'", new_chars)
    else:
        delimiter = "'"
        new_chars = _translateCdata(characters, allEntRefs = 1)
        new_chars = re.sub("&quot;", '"', new_chars)
    return new_chars, delimiter

def indentBlock(text, indent, line_length):
    words = text.split()
    lines = []
    i = 0
    while i < len(words):
        line = []
        while i < len(words) and indent + len(" ".join(line)) < line_length:
            line.append(words[i])
            i += 1
        if len(line) > 1 and indent + len(" ".join(line)) >= line_length:
            i -= 1
            line.pop()
        lines.append(" " * indent + " ".join(line))
    return '\n'.join(lines)

    

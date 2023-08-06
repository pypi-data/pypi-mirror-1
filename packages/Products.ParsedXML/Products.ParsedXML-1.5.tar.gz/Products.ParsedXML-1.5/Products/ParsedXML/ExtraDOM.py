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

"""
Non-DOM helper functions useful when working with either of our DOM
implementations, but not specific to any instantiation.
"""

from xml.dom import Node

import DOM.ExpatBuilder
import PrettyPrinter
from StringIO import StringIO


def parseFile(node, file, namespaces = 1):
    """
    Parse XML file, replace node with the resulting tree,
    return replacement.
    Node must be in an existing DOM tree if not a Document.
    """
    if node.nodeType == Node.DOCUMENT_NODE:
        return DOM.ExpatBuilder.parse(file, namespaces)
    elif node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
        raise Exception, "replacing a document fragment doesn't make sense"
    else:
        fragment = DOM.ExpatBuilder.parseFragment(
            file, node.parentNode, namespaces)
        #if fragment.childNodes.length != 1:
        #    # we could do this, actually, if we wanted
        #    raise Exception, "replacing a Node with less or more " + \
        #          "than one tree of Nodes is not implemented"
        sib = node.nextSibling
        parent = node.parentNode
        parent.removeChild(node)
        #print fragment.childNodes.length
        #for child in fragment.childNodes:
        #    print child.nodeType, node.nodeName
        #    if child.nodeType == Node.TEXT_NODE:
        #        print repr(child.data) 
        return parent.insertBefore(fragment.firstChild, sib) # frag.firstChild
         

def writeStream(node, stream = None, encoding=None, prettyPrint = 0):
    "Write the XML representation of node to stream."
    if stream is None:
        stream = StringIO()
    PrettyPrinter.PrintVisitor(
        node, stream, encoding, prettyPrint=prettyPrint)()
    return stream

    

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

"""Implementation of DOM Level 2 Traversal.

Based on the W3C recommendation at:
    http://www.w3.org/TR/DOM-Level-2-Traversal-Range/
"""

# This code could be sped up.
# - uses DOM methods, could use implementation internals, esp. childNodes
# - if we had mutation events, NodeIterator could build an array as it
#   iterated, and move over that, only updating on mutation

import xml.dom


__all__ = [
    "NodeFilter",
    "NodeIterator",
    "TreeWalker",
    ]


class NodeFilter:
    # Constants returned by acceptNode():
    FILTER_ACCEPT                  = 1
    FILTER_REJECT                  = 2
    FILTER_SKIP                    = 3

    # Constants for whatToShow:
    SHOW_ALL                       = 0xFFFFFFFF
    SHOW_ELEMENT                   = 0x00000001
    SHOW_ATTRIBUTE                 = 0x00000002
    SHOW_TEXT                      = 0x00000004
    SHOW_CDATA_SECTION             = 0x00000008
    SHOW_ENTITY_REFERENCE          = 0x00000010
    SHOW_ENTITY                    = 0x00000020
    SHOW_PROCESSING_INSTRUCTION    = 0x00000040
    SHOW_COMMENT                   = 0x00000080
    SHOW_DOCUMENT                  = 0x00000100
    SHOW_DOCUMENT_TYPE             = 0x00000200
    SHOW_DOCUMENT_FRAGMENT         = 0x00000400
    SHOW_NOTATION                  = 0x00000800

    def acceptNode(self, node):
        # Just accept everything by default:
        return NodeFilter.FILTER_ACCEPT


_whatToShow_bits = (
    (xml.dom.Node.ELEMENT_NODE, NodeFilter.SHOW_ELEMENT),
    (xml.dom.Node.ATTRIBUTE_NODE, NodeFilter.SHOW_ATTRIBUTE),
    (xml.dom.Node.TEXT_NODE, NodeFilter.SHOW_TEXT),
    (xml.dom.Node.CDATA_SECTION_NODE, NodeFilter.SHOW_CDATA_SECTION),
    (xml.dom.Node.ENTITY_REFERENCE_NODE, NodeFilter.SHOW_ENTITY_REFERENCE),
    (xml.dom.Node.ENTITY_NODE, NodeFilter.SHOW_ENTITY),
    (xml.dom.Node.PROCESSING_INSTRUCTION_NODE,
     NodeFilter.SHOW_PROCESSING_INSTRUCTION),
    (xml.dom.Node.COMMENT_NODE, NodeFilter.SHOW_COMMENT),
    (xml.dom.Node.DOCUMENT_NODE, NodeFilter.SHOW_DOCUMENT),
    (xml.dom.Node.DOCUMENT_TYPE_NODE, NodeFilter.SHOW_DOCUMENT_TYPE),
    (xml.dom.Node.DOCUMENT_FRAGMENT_NODE, NodeFilter.SHOW_DOCUMENT_FRAGMENT),
    (xml.dom.Node.NOTATION_NODE, NodeFilter.SHOW_NOTATION),
    )

class AccessorBase:
    def __init__(self, root, whatToShow, filter, entityReferenceExpansion):
        if root is None:
            raise xml.dom.NotSupportedErr(
                "root of traversal object can't be None")
        d = self.__dict__
        d['root'] = root
        d['whatToShow'] = whatToShow
        d['filter'] = filter
        d['expandEntityReferences'] = entityReferenceExpansion
        #
        # Decode the whatToShow flags for faster tests; the W3C
        # reserves the first 200 NodeType values, but the whatToShow
        # flags have to fit in 32 bits (leave slot 0 empty since it's
        # not a valid NodeType).
        #
        d['_whatToShow'] = what = [0] * 33
        for nodeType, bit in _whatToShow_bits:
            what[nodeType] = whatToShow & bit

    def __setattr__(self, name, value):
        setter = getattr(self, '_set_' + name, None)
        if setter is None:
            getter = getattr(self, '_get_' + name, None)
            if getter:
                raise xml.dom.NoModificationAllowedErr(
                    "read-only attribute: " + `name`)
            else:
                raise AttributeError, "no such attribute: " + `name`
        setter(value)

    def _get_root(self):
        return self.root

    def _get_whatToShow(self):
        return self.whatToShow

    def _get_filter(self):
        return filter

    def _get_expandEntityReferences(self):
        return self.expandEntityReferences

    def _should_show(self, node):
        if not self._whatToShow[node.nodeType]:
            return NodeFilter.FILTER_SKIP
        else:
            if (  node.nodeType == xml.dom.Node.ENTITY_REFERENCE_NODE
                  and not self.expandEntityReferences):
                return NodeFilter.FILTER_REJECT
            elif self.filter is not None:
                return self._filterNode(node)
        return NodeFilter.FILTER_ACCEPT

    def _nextInTree(self, node):
        """Return first visible node in node's subtree, or None."""
        # check given node first
        if self._should_show(node) == NodeFilter.FILTER_ACCEPT:
            return node
        elif self._should_show(node) == NodeFilter.FILTER_REJECT:
            return None
        for c in node.childNodes:
            child = self._nextInTree(c)
            if child:
                return child
            if c.isSameNode(self.root): # don't leave root subtree
                return None
        return None

    def _lastInTree(self, node):
        """Return last visible node in node's subtree, or None."""
        if self._should_show(node) == NodeFilter.FILTER_REJECT:
            return None
        childNodes = node.childNodes
        childNums = range(childNodes.length)
        childNums.reverse()
        for c in childNums:
            childNode = childNodes[c]
            child = self._lastInTree(childNode)
            if child:
                return child
            if childNode.isSameNode(self.root): # don't leave root subtree
                return None
        # subtree exhausted, check given node
        if self._should_show(node) == NodeFilter.FILTER_ACCEPT:
            return node
        return None

    # we don't do any visibilty tests here, _nextInTree does.
    def _nextNode(self, startNode):
        """Return next visible node after startNode, or None."""
        # check children
        for child in startNode.childNodes:
            node = self._nextInTree(child)
            if node:
                return node
            if child.isSameNode(self.root): # don't leave root subtree
                return None
        # check next siblings
        sib = startNode.nextSibling
        while sib:
            node = self._nextInTree(sib)
            if node:
                return node
            if sib.isSameNode(self.root): # don't leave root subtree
                return None
            sib = sib.nextSibling
        # check ancestors' next siblings; don't visit ancestors
        ancestor = startNode.parentNode
        while ancestor:
            sib = ancestor.nextSibling
            while sib:
                node = self._nextInTree(sib)
                if node:
                    return node
                if sib.isSameNode(self.root): # don't leave root subtree
                    return None
                sib = sib.nextSibling
            # no visible nodes in siblings or subtrees of this ancestor
            if ancestor.isSameNode(self.root):
                # don't leave root subtree                
                return None
            ancestor = ancestor.parentNode
        return None

    # we *do* a visibilty test here, _lastInTree does too.
    def _previousNode(self, startNode):
        """Return the previous visible node after startNode, or None."""
        # check previous siblings
        sib = startNode.previousSibling
        while sib:
            node = self._lastInTree(sib)
            if node:
                return node
            if sib.isSameNode(self.root): # don't leave root subtree
                return None
            sib = sib.previousSibling
        # check ancestors, then ancestors' previous siblings
        ancestor = startNode.parentNode
        while ancestor:
            if self._should_show(ancestor) == NodeFilter.FILTER_ACCEPT:
                return ancestor
            sib = ancestor.previousSibling
            while sib:
                node = self._lastInTree(sib)
                if node:
                    return node
                if sib.isSameNode(self.root): # don't leave root subtree
                    return None
                sib = sib.previousSibling
            if ancestor.isSameNode(self.root):
                # don't leave root subtree
                return None
            ancestor = ancestor.parentNode
        return None

# Since we don't need to know about structure, we could probably be a lot
# faster if we kept a list of nodes in document order and updated
# it when we got a mutation event - once we have mutation events.
class NodeIterator(AccessorBase):
    BEFORE_NODE = 1 # iterator crossed reference node moving forward
    AFTER_NODE = 0  # iterator crossed reference node moving backward

    def __init__(self, root, whatToShow=NodeFilter.SHOW_ALL, filter=None,
                 entityReferenceExpansion=1):
        AccessorBase.__init__(self, root, whatToShow,
                              filter, entityReferenceExpansion)
        self.__dict__['_refNode'] = None
        self.__dict__['_refPos'] = NodeIterator.BEFORE_NODE

    def detach(self):
        self.__dict__['root'] = None

    def nextNode(self):
        if self.root is None:
            raise xml.dom.InvalidStateErr(
                "can't iterate using a detached NodeIterator")
        if self._refNode == None:
            self.__dict__['_refNode'] = self.root
            self.__dict__['_refPos'] = NodeIterator.AFTER_NODE
            if self._should_show(self._refNode) == NodeFilter.FILTER_ACCEPT:
                return self._refNode
        elif self._refPos == NodeIterator.BEFORE_NODE:
            if self._should_show(self._refNode) == NodeFilter.FILTER_ACCEPT:
                self.__dict__['_refPos'] = NodeIterator.AFTER_NODE
                return self._refNode
        
        node = AccessorBase._nextNode(self, self._refNode)
        if node:
            self.__dict__['_refNode'] = node
        self.__dict__['_refPos'] = NodeIterator.AFTER_NODE
        return node

    def previousNode(self):
        if self.root is None:
            raise xml.dom.InvalidStateErr(
                "can't iterate using a detached NodeIterator")
        if self._refNode == None:
            self.__dict__['_refNode'] = self.root
            self.__dict__['_refPos'] = NodeIterator.BEFORE_NODE
        elif self._refPos == NodeIterator.AFTER_NODE:
            if self._should_show(self._refNode) == NodeFilter.FILTER_ACCEPT:
                self.__dict__['_refPos'] = NodeIterator.BEFORE_NODE
                return self._refNode
        
        node = AccessorBase._previousNode(self, self._refNode)
        if node:
            self.__dict__['_refNode'] = node            
        self.__dict__['_refPos'] = NodeIterator.BEFORE_NODE        
        return node

    def __getitem__(self, index):
        node = self.nextNode()
        if node is None:
            raise IndexError, "NodeIterator index out of range"
        return node

    def _filterNode(self, node):
        """Return what the filter says to do with node,
        translating reject into skip"""
        filterAction = self.filter.acceptNode(node)
        if filterAction == NodeFilter.FILTER_REJECT:
            return NodeFilter.FILTER_SKIP
        return filterAction


class TreeWalker(AccessorBase):
    def __init__(self, root, whatToShow=NodeFilter.SHOW_ALL, filter=None,
                 entityReferenceExpansion=1):
        AccessorBase.__init__(self, root, whatToShow,
                              filter, entityReferenceExpansion)
        self.__dict__['currentNode'] = root
        
    def _get_currentNode(self):
        return self.currentNode

    def _set_currentNode(self, node):
        if node is None:
            raise xml.dom.NotSupportedErr("can't set current node to None")
        self.__dict__['currentNode'] = node

    def parentNode(self):
        if self.root.isSameNode(self.currentNode):
            return None
        node = self.currentNode.parentNode
        while node is not None and (
            self._should_show(node) != NodeFilter.FILTER_ACCEPT):
            if node.isSameNode(self.root):
                # can't step any further up
                return
            else:
                node = node.parentNode
        if node is not None:
            self.__dict__['currentNode'] = node
        return node

    def firstChild(self):
        node = self.currentNode.firstChild
        while node is not None and (
            self._should_show(node) != NodeFilter.FILTER_ACCEPT):
            node = node.nextSibling
        if node is not None:
            self.__dict__['currentNode'] = node
        return node

    def lastChild(self):
        node = self.currentNode.lastChild
        while node is not None and (
            self._should_show(node) != NodeFilter.FILTER_ACCEPT):
            node = node.previousSibling
        if node is not None:
            self.__dict__['currentNode'] = node
        return node

    # the rec doesn't say that *Sibling should pay attention to root!
    def previousSibling(self):
        node = self.currentNode.previousSibling
        while node is not None and (
            self._should_show(node) != NodeFilter.FILTER_ACCEPT):
            node = node.previousSibling
        if node is not None:
            self.__dict__['currentNode'] = node
        return node

    def nextSibling(self):
        node = self.currentNode.nextSibling
        while node is not None and (
            self._should_show(node) != NodeFilter.FILTER_ACCEPT):
            node = node.nextSibling
        if node is not None:
            self.__dict__['currentNode'] = node
        return node

    # TreeWalkers don't move if there is no visible next or previous,
    # so we do nothing for a None return.
    def nextNode(self):
        node = AccessorBase._nextNode(self, self.currentNode)
        if node:
            self.__dict__['currentNode'] = node
        return node

    def previousNode(self):
        node = AccessorBase._previousNode(self, self.currentNode)
        if node:
            self.__dict__['currentNode'] = node
        return node

    def _filterNode(self, node):
        """Return what the filter says to do with node."""
        return self.filter.acceptNode(node)

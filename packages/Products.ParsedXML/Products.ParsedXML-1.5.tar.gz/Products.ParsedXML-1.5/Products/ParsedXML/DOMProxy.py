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

import DOM
import xml.dom

from ComputedAttribute import ComputedAttribute

import string

_DOM_PROXY_FEATURES = ()

class DOMImplementationProxy:
    def __init__(self):
        self._domimplementation = DOM.theDOMImplementation

    def hasFeature(self, feature, version):
        feature = string.lower(feature)
        if (feature, version) in _DOM_PROXY_FEATURES:
            return 1
        return self._domimplementation.hasFeature(feature, version)

    def _createDOMDocumentType(self, qualifiedName, publicId, systemId):
        return self._domimplementation.createDocumentType(
            qualifiedName, publicId, systemId)

    def _createDOMDocument(self, namespaceURI, qualifiedName, docType=None):
        return self._domimplementation.createDocument(
            namespaceURI, qualifiedName, docType)

class DOMProxy:

    def __init__(self, node, persistentDoc=None):
        self._node = node
        self._persistentDoc = persistentDoc
        
    def getDOMObj(self):
        """Return the node without wrappers.
        """
        return self._node
    
    def getPersistentDoc(self):
        """Return a reference to a security friendly persistent document
        if we can, or None.  This can be None when OwnerDocument, if it
        exsists, is not None.  If you don't need to reach the document
        through the security checks, you don't need to use this method.
        """    
        # We do this because the userfolder container needs to be in the aq
        # context of the unwrapped returned object.
        if self._persistentDoc and getattr(
            self._persistentDoc, "_container", None):
            
            try:
                # If we can get to self, we can get to the persistent doc -
                # but restrictedTraverse is necessary for some reason for
                # what we return to be used in an acquisition chain
                return self._persistentDoc._container.restrictedTraverse(
                    self._persistentDoc.getPhysicalPath())
            except:
                pass
        return None

    def __setattr__(self, name, value):
        """Proxy DOM attribute writes, else write to our attribute.
        """
        if name in self._DOMAttrs:
            setattr(self._node, name, value)
        else:
            self.__dict__[name] = value
            # flag that we're dirty if we're persistent
            # FIXME: perhaps there's a better way to make those
            # test cases work?
            if hasattr(self, '_p_changed'):
                self._p_changed = 1
            
    def __nonzero__(self):
        "is this node true?"
        # FIXME: not sure this makes sense
        try:
            return self._node.__nonzero__()
        except:
            if self._node:
                return 1
            else:
                return 0
        
    # no need to avoid aq bugs fixed in Zope 2.3.1 so no __len__

class NodeProxy(DOMProxy):
    _DOMAttrs = ("nodeName", "attributes", "childNodes", "firstChild",
                 "lastChild", "localName", "namespaceURI", "nextSibling",
                 "previousSibling",
                 "nodeType", "nodeValue", "ownerDocument", "parentNode",
                 "prefix")
    
    ELEMENT_NODE = 1
    ATTRIBUTE_NODE = 2
    TEXT_NODE = 3
    CDATA_SECTION_NODE = 4
    ENTITY_REFERENCE_NODE = 5
    ENTITY_NODE = 6
    PROCESSING_INSTRUCTION_NODE = 7
    COMMENT_NODE = 8
    DOCUMENT_NODE = 9
    DOCUMENT_TYPE_NODE = 10
    DOCUMENT_FRAGMENT_NODE = 11
    NOTATION_NODE = 12
    
    def _get_nodeName(self):
        return self._node._get_nodeName()
    nodeName = ComputedAttribute(_get_nodeName)
    
    def _get_attributes(self):
        return self.wrapNamedNodeMap(self._node._get_attributes())
    attributes = ComputedAttribute(_get_attributes)

    def _get_childNodes(self):
        return self.wrapNodeList(self._node._get_childNodes())
    childNodes = ComputedAttribute(_get_childNodes)
    
    def _get_firstChild(self):
        return self.wrapDOMObj(self._node._get_firstChild())
    firstChild = ComputedAttribute(_get_firstChild)
    
    def _get_lastChild(self):
        return self.wrapDOMObj(self._node._get_lastChild())
    lastChild = ComputedAttribute(_get_lastChild)
    
    def _get_localName(self):
        return self._node._get_localName()
    localName = ComputedAttribute(_get_localName)
    
    def _get_namespaceURI(self):
        return self._node._get_namespaceURI()
    namespaceURI = ComputedAttribute(_get_namespaceURI)
    
    def _get_nextSibling(self):
        return self.wrapDOMObj(self._node._get_nextSibling())
    nextSibling = ComputedAttribute(_get_nextSibling)
    
    def _get_previousSibling(self):
        return self.wrapDOMObj(self._node._get_previousSibling())
    previousSibling = ComputedAttribute(_get_previousSibling)
    
    def _get_nodeType(self):
        return self._node._get_nodeType()
    nodeType = ComputedAttribute(_get_nodeType)
    
    def _get_nodeValue(self):
        return self._node._get_nodeValue()
    nodeValue = ComputedAttribute(_get_nodeValue)
        
    def _get_parentNode(self):
        return self.wrapDOMObj(self._node._get_parentNode())
    parentNode = ComputedAttribute(_get_parentNode)
    
    def _get_prefix(self):
        return self._node._get_prefix()
    prefix = ComputedAttribute(_get_prefix)
    
    def hasAttributes(self):
        return self._node.hasAttributes()

    def hasChildNodes(self):
        return self._node.hasChildNodes()

    def appendChild(self, newChild):
        self._node.appendChild(newChild._node)
        return newChild
    
    def insertBefore(self, newChild, refChild):
        self._node.insertBefore(newChild._node,
                                getattr(refChild, "_node", None))
        return newChild

    def removeChild(self, oldChild):
        self._node.removeChild(oldChild._node)
        return oldChild

    def replaceChild(self, newChild, oldChild):
        self._node.replaceChild(newChild._node, oldChild._node)
        return oldChild

    def normalize(self):
        self._node.normalize()

    def isSupported(self, feature, version):
        return self._node.isSupported(feature, version)

    def isSameNode(self, other):
        return self._node.isSameNode(other._node)

    def cloneNode(self, deep):
        return self.wrapDOMObj(self._node.cloneNode(deep))

    def __cmp__(self, other):
        try:
            return cmp(self._node, other._node)
        except AttributeError:
            return 1
    
    def _get_ownerDocument(self):
        """
        Return the DOM document - the persistent document that was instantiated
        if we can, otherwise another generated proxy node.
        """
        return (self.getPersistentDoc() or
                self.wrapDOMObj(self._node._get_ownerDocument()))

    ownerDocument = ComputedAttribute(_get_ownerDocument)

    def __hash__(self):
        return self._node.__hash__()
    
class NodeListProxy(DOMProxy):
    _DOMAttrs = ("length",)

    def __len__(self):
        return self._node.__len__()

    def _get_length(self):
        return self._node._get_length()

    length = ComputedAttribute(_get_length)

    def __nonzero__(self):
        return self._node.__nonzero__()

    def __setitem__(self, i, newChild):
        self._node.__setitem__(i, newChild._node)

    def __delitem__(self, i):
        self._node.__delitem__(i)

    def __getitem__(self, i):
        return self.wrapDOMObj(self._node.__getitem__(i))

    def __getslice__(self, i, j):
        return self.wrapNodeList(self._node.__getslice__(i, j))

    def item(self, i):
        return self.wrapDOMObj(self._node.item(i))

    def count(self, value):
        return self._node.count(value._node)
    
    def index(self, value):
        return self._node.index(value._node)
    
class NamedNodeMapProxy(DOMProxy):
    _DOMAttrs = ("length", "keys")

    def getDOMObj(self):
        """Return the Node without any of our wrappers
        """
        return self._node

    def __len__(self):
        return self._node.__len__()
    
    def _get_length(self):
        return self._node._get_length()
    length = ComputedAttribute(_get_length)

    def setNamedItem(self, arg):
        return self.wrapDOMObj(self._node.setNamedItem(arg._node))

    def setNamedItemNS(self, arg):
        return self.wrapDOMObj(self._node.setNamedItemNS(arg._node))

    def removeNamedItem(self, name):
        return self.wrapDOMObj(self._node.removeNamedItem(name))

    def removeNamedItemNS(self, namespaceURI, localName):
        return self.wrapDOMObj(self._node.removeNamedItemNS(namespaceURI,
                                                            localName))

    def get(self, name, default=None):
        node = self._node.getNamedItem(name)
        if node is None:
            return default
        else:
            return self.wrapDOMObj(node)

    def has_key(self, name):
        return self._node.has_key(name)

    def item(self, i):
        return self.wrapDOMObj(self._node.item(i))

    def getNamedItem(self, name):
        return self.wrapDOMObj(self._node.getNamedItem(name))

    def getNamedItemNS(self, namespaceURI, localName):
        return self.wrapDOMObj(self._node.getNamedItemNS(namespaceURI,
                                                         localName))

    def __setitem__(self, name, node):
        self._node.__setitem__(name, node._node)

    def __getitem__(self, name):
        return self.wrapDOMObj(self._node.__getitem__(name))

    def __delitem__(self, name):
        self._node.__delitem__(name)

    def keys(self):
        return self._node.keys()
    
    def values(self):
        return map(self.wrapDOMObj, self._node.values())

    def items(self):
        result = []
        for key, value in self.getDOMObj().items():
            result.append((key, self.wrapDOMObj(value)))
        return result

class DocumentFragmentProxy(NodeProxy):
    pass
    
class ElementProxy(NodeProxy):
    _DOMAttrs = NodeProxy._DOMAttrs + ("tagName", 'element_id')

    def _get_tagName(self):
        return self._node._get_tagName()
    
    tagName = ComputedAttribute(_get_tagName)

    def _get_elementId(self):
        return self._node._get_elementId()

    elementId = ComputedAttribute(_get_elementId)
    
    def getAttribute(self, name):
        return self._node.getAttribute(name)

    def getAttributeNS(self, namespaceURI, localName):
        return self._node.getAttributeNS(namespaceURI, localName)

    def getAttributeNode(self, name):
        return self.wrapDOMObj(self._node.getAttributeNode(name))

    def getAttributeNodeNS(self, namespaceURI, localName):
        return self.wrapDOMObj(self._node.getAttributeNodeNS(namespaceURI,
                                                           localName))

    def getElementsByTagName(self, name):
        return self.wrapNodeList(self._node.getElementsByTagName(name))
    
    def getElementsByTagNameNS(self, namespaceURI, localName):
        return self.wrapNodeList(self._node.getElementsByTagNameNS(namespaceURI,
                                                                   localName))

    def hasAttribute(self, name):
        return self._node.hasAttribute(name)

    def hasAttributeNS(self, namespaceURI, localName):
        return self._node.hasAttributeNS(namespaceURI, localName)

    def removeAttribute(self, name):
        self._node.removeAttribute(name)

    def removeAttributeNS(self, namespaceURI, localName):
        self._node.removeAttributeNS(namespaceURI, localName)

    def removeAttributeNode(self, oldAttr):
        return self.wrapDOMObj(self._node.removeAttributeNode(oldAttr._node))

    def setAttribute(self, name, value):
        self._node.setAttribute(name, value)

    def setAttributeNS(self, namespaceURI, qualifiedName, value):
        self._node.setAttributeNS(namespaceURI, qualifiedName, value)

    def setAttributeNode(self, newAttr):
        return self.wrapDOMObj(self._node.setAttributeNode(newAttr._node))

    def setAttributeNodeNS(self, newAttr):
        return self.wrapDOMObj(self._node.setAttributeNodeNS(newAttr._node))

class CharacterDataProxy(NodeProxy):
    _DOMAttrs = NodeProxy._DOMAttrs + ("data", "length")
    
    def __len__(self):
        return self._node.__len__()

    def _get_data(self):
        return self._node._get_data()

    data = ComputedAttribute(_get_data)

    def _set_data(self, value):
        self._node._set_data(value)
        
    def _get_length(self):
        return self._node._get_length()
    
    length = ComputedAttribute(_get_length)

    def appendData(self, arg):
        self._node.appendData(arg)

    def deleteData(self, offset, count):
        self._node.deleteData(offset, count)

    def insertData(self, offset, arg):
        self._node.insertData(offset, arg)

    def replaceData(self, offset, count, arg):
        self._node.replaceData(offset, count, arg)

    def substringData(self, offset, count):
        return self._node.substringData(offset, count)
        
class TextProxy(CharacterDataProxy):
    def splitText(self, offset):
        return self.wrapDOMObj(self._node.splitText(offset))

class CDATASectionProxy(TextProxy):
    pass

class CommentProxy(CharacterDataProxy):
    pass

class ProcessingInstructionProxy(NodeProxy):
    _DOMAttrs = NodeProxy._DOMAttrs + ("target", "data")

    def _get_target(self):
        return self._node._get_target()

    target = ComputedAttribute(_get_target)

    def _get_data(self):
        return self._node._get_data()

    data = ComputedAttribute(_get_data)

    def _set_data(self, value):
        self._node._set_data(value)
        
class AttrProxy(NodeProxy):
    _DOMAttrs = NodeProxy._DOMAttrs + ("name", "value", "specified",
                                       "ownerElement")

    def _get_name(self):
        return self._node._get_name()

    name = ComputedAttribute(_get_name)
    
    def _get_value(self):
        return self._node._get_value()
    # setting should also be okay
    value = ComputedAttribute(_get_value)

    def _set_value(self, value):
        self._node._set_value(value)
        
    def _get_specified(self):
        return self._node._get_specified()

    specified = ComputedAttribute(_get_specified)
    
    def _get_ownerElement(self):
        return self.wrapDOMObj(self._node._get_ownerElement())

    ownerElement = ComputedAttribute(_get_ownerElement)
    
class DocumentProxy(NodeProxy):
    _DOMAttrs = NodeProxy._DOMAttrs + ("doctype", "documentElement")
    
    def _get_doctype(self):
        return self.wrapDOMObj(self._node._get_doctype())

    doctype = ComputedAttribute(_get_doctype)

    def _get_documentElement(self):
        return self.wrapDOMObj(self._node._get_documentElement())

    documentElement = ComputedAttribute(_get_documentElement)

    # _get_implementation defined in subclass
    
    def createAttribute(self, name):
        return self.wrapDOMObj(self._node.createAttribute(name))

    def createAttributeNS(self, namespaceURI, qualifiedName):
        return self.wrapDOMObj(self._node.createAttributeNS(namespaceURI,
                                                            qualifiedName))

    def createCDATASection(self, data):
        return self.wrapDOMObj(self._node.createCDATASection(data))

    def createComment(self, data):
        return self.wrapDOMObj(self._node.createComment(data))

    def createDocumentFragment(self):
        return self.wrapDOMObj(self._node.createDocumentFragment())

    def createElement(self, tagName):
        return self.wrapDOMObj(self._node.createElement(tagName))

    def createElementNS(self, namespaceURI, qualifiedName):
        return self.wrapDOMObj(self._node.createElementNS(namespaceURI,
                                                           qualifiedName))
    def createEntityReference(self, name):
        return self.wrapDOMObj(self._node.createEntityReference(name))

    def createProcessingInstruction(self, target, data):
        return self.wrapDOMObj(self._node.createProcessingInstruction(target,
                                                                      data))
    def createTextNode(self, data):
        return self.wrapDOMObj(self._node.createTextNode(data))

    def getElementById(self, elementId):
        return self.wrapDOMObj(self._node.getElementById(elementId))

    def getElementsByTagName(self, tagName):
        return self.wrapNodeList(self._node.getElementsByTagName(tagName))

    def getElementsByTagNameNS(self, namespaceURI, localName):
        return self.wrapNodeList(self._node.getElementsByTagNameNS(namespaceURI,
                                                                   localName))
    
    def importNode(self, importedNode, deep):
        return self.wrapDOMObj(self._node.importNode(importedNode._node,
                                                     deep))

    def createNodeIterator(self, root, whatToShow, filter,
                           entityReferenceExpansion):
        # FIXME: needs wrapper!
        return self._node.createNodeIterator(root, whatToShow, filter,
                                             entityReferenceExpansion)

    def createTreeWalker(self, root, whatToShow, filter,
                         entityReferenceExpansion):
        # FIXME: needs wrapper!
        return self._node.createTreeWalker(root, whatToShow, filter,
                                           entityReferenceExpansion)
    
class EntityProxy(NodeProxy):
    _DOMAttrs = NodeProxy._DOMAttrs + ("publicId", "systemId", "notationName")

    def _get_publicId(self):
        return self._node._get_publicId()

    publicId = ComputedAttribute(_get_publicId)

    def _get_systemId(self):
        return self._node._get_systemId()

    systemId = ComputedAttribute(_get_systemId)

    def _get_notationName(self):
        return self._node._get_notationName()

    notationName = ComputedAttribute(_get_notationName)

class EntityReferenceProxy(NodeProxy):
    pass

class NotationProxy(NodeProxy):
    _DOMAttrs = NodeProxy._DOMAttrs + ("publicId", "systemId")

    def _get_publicId(self):
        return self._node._get_publicId()

    publicId = ComputedAttribute(_get_publicId)

    def _get_systemId(self):
        return self._node._get_systemId()

    systemId = ComputedAttribute(_get_systemId)
    
class DocumentTypeProxy(NodeProxy):
    _DOMAttrs = NodeProxy._DOMAttrs + ("publicId", "systemId",
                                       "name", "entities", "notations",
                                       "internalSubset")
    def _get_entities(self):
        return self.wrapNamedNodeMap(self._node._get_entities())

    entities = ComputedAttribute(_get_entities)
    
    def _get_internalSubset(self):
        return self._node._get_internalSubset()

    internalSubset = ComputedAttribute(_get_internalSubset)
    
    def _get_name(self):
        return self._node._get_name()

    name = ComputedAttribute(_get_name)
    
    def _get_notations(self):
        return self.wrapNamedNodeMap(self._node._get_notations())

    notations = ComputedAttribute(_get_notations)
    
    def _get_publicId(self):
        return self._node._get_publicId()

    publicId = ComputedAttribute(_get_publicId)
    
    def _get_systemId(self):
        return self._node._get_systemId()

    systemId = ComputedAttribute(_get_systemId)
    

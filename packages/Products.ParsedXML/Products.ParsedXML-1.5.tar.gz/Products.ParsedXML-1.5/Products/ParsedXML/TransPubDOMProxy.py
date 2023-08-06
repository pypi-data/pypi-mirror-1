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
A simple example implementation of DOMProxy.

Provide a class to implement wrapDOMObj(), mix that and the DOMProxy proxy
classes, and add whatever you want to make it interesting.
"""

import DOMProxy
import Acquisition

class TransPubWrapper:
    """
    Mixin class to go alongside DOMProxy classes.  Provides the wrapDOMObj
    function to create TransPubNode classes.  This is what makes TransPubNodes
    transient - we never re-use proxies, but create new ones when we need them.
    """
    
    # In the future we may want to return different proxy types based
    # on non-DOM node types, such as DB/nonDB.  Probably map
    # the same way that the DOM classes will map.
    def wrapDOMObj(self, node):
        """
        Return the appropriate manageable class wrapped around the Node.
        We never create Nodes ourselves, only wrap existing ones.
        Wrapped node can be single DOM object, a non-DOM object, or a
        container that contains only non-DOM objects - DOM objects in
        containters aren't wrapped.
        """
        from xml.dom import Node
        import types
        if node == None:
            return None
        elif isinstance(node, types.InstanceType) \
             and node.__class__.__name__ == "ChildNodeList": # XXX impl detail
            return TransPubNodeList(node)
        elif isinstance(node, types.InstanceType) \
             and node.__class__.__name__ == "AttributeMap": # XXX impl detail
            return TransPubNamedNodeMap(node)
        elif not hasattr(node, "nodeType"):
            return node                     # not DOM, don't wrap.
        elif node.nodeType == Node.ELEMENT_NODE:
            return TransPubElement(node)
        elif node.nodeType == Node.ATTRIBUTE_NODE:
            return TransPubAttr(node)
        elif node.nodeType == Node.TEXT_NODE:
            return TransPubText(node)
        elif node.nodeType == Node.CDATA_SECTION_NODE:
            return TransPubCDATASection(node)
        elif node.nodeType == Node.ENTITY_REFERENCE_NODE:
            return TransPubEntityReference(node)
        elif node.nodeType == Node.ENTITY_NODE:
            return TransPubEntity(node)
        elif node.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
            return TransPubProcessingInstruction(node)
        elif node.nodeType == Node.COMMENT_NODE:
            return TransPubComment(node)
        elif node.nodeType == Node.DOCUMENT_NODE:
            return TransPubDocument(node)
        elif node.nodeType == Node.DOCUMENT_TYPE_NODE:
            return TransPubDocumentType(node)
        elif node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            return TransPubDocumentFragment(node)
        elif node.nodeType == Node.NOTATION_NODE:
            return TransPubNotation(node)
        else:
            raise TypeError


_TRANS_PUB_DOM_PROXY_FEATURES = (
    ("org.zope.dom.acquisition", None),
    ("org.zope.dom.acquisition", "1.0"),
    )

class TransPubDOMImplementation(DOMProxy.DOMImplementationProxy):
    """
    A DOMImplementation proxy that implements createDocument to produce
    TransPubDocument instances.
    """

    def hasFeature(self, feature, version):
        feature = string.lower(feature)
        if (feature, version) in _TRANS_PUB_DOM_PROXY_FEATURES:
            return 1
        return self._domimplementation.hasFeature(feature, version)
    
    def createDocument(self, namespaceURI, qualifiedName, docType=None):
        DOMDocument = self._createDOMDocument(namespaceURI,
                                              qualifiedName, docType)
        return TransPubDocument(DOMDocument.aq_base) # XXX check aq

theDOMImplementation = TransPubDOMImplementation()

#DOMIO, DOMManageable, DOMPublishable,
class TransPubNode(TransPubWrapper, DOMProxy.NodeProxy, Acquisition.Implicit):
    "The core of the TransPub DOM proxies."
    pass

class TransPubNodeList(TransPubWrapper, DOMProxy.NodeListProxy):    
    "A TransPubWrapper mixer with NodeListProxy."
    pass

class TransPubNamedNodeMap(TransPubWrapper, DOMProxy.NamedNodeMapProxy):
    "A TransPubWrapper mixer with NamedNodeMapProxy."
    pass
    
class TransPubDocumentFragment(DOMProxy.DocumentFragmentProxy, TransPubNode):
    "A TransPubWrapper mixer with DocumentFragmentProxy."
    pass
    
class TransPubElement(DOMProxy.ElementProxy, TransPubNode):
    "A TransPubWrapper mixer with ElementProxy."
    pass

class TransPubCharacterData(DOMProxy.CharacterDataProxy, TransPubNode):
    "A TransPubWrapper mixer with CharacterDataProxy."
    pass

class TransPubCDATASection(DOMProxy.CDATASectionProxy, TransPubNode):
    "A TransPubWrapper mixer with CDATASectionProxy."
    pass

class TransPubText(TextProxy, DOMProxy.TransPubCharacterData):
    "A TransPubWrapper mixer with TextProxy."
    pass

class TransPubComment(CommentProxy, DOMProxy.TransPubCharacterData):
    "A TransPubWrapper mixer with CommentProxy."
    pass

class TransPubProcessingInstruction(DOMProxy.ProcessingInstructionProxy,
                                    TransPubNode):
    "A TransPubWrapper mixer with ProcessingInstructionProxy."
    pass

class TransPubAttr(DOMProxy.AttrProxy, TransPubNode):
    "A TransPubWrapper mixer with AttrProxy."
    pass

class TransPubDocument(DOMProxy.DocumentProxy, TransPubNode):
    """
    A TransPubWrapper mixer with DocumentProxy.
    Provides and protects the implementation attribute.
    """
    
    implementation = theDOMImplementation

    #block set of implementation, since we don't proxy it the same
    def __setattr__(self, name, value):
        if name == "implementation":
            raise xml.dom.NoModificationAllowedErr()
        # wacky ExtensionClass inheritance
        TransPubDocument.inheritedAttribute('__setattr__')(self, name, value)

# DOM extended interfaces

class TransPubEntityReference(DOMProxy.EntityReferenceProxy, TransPubNode):
    "A TransPubWrapper mixer with EntityReferenceProxy."
    pass

class TransPubEntity(DOMProxy.EntityProxy, TransPubNode):
    "A TransPubWrapper mixer with EntityProxy."
    pass

class TransPubNotation(DOMProxy.NotationProxy, TransPubNode):
    "A TransPubWrapper mixer with NotationProxy."
    pass

class TransPubDocumentType(DOMProxy.DocumentTypeProxy, TransPubNode):
    "A TransPubWrapper mixer with DocumentTypeProxy."
    pass


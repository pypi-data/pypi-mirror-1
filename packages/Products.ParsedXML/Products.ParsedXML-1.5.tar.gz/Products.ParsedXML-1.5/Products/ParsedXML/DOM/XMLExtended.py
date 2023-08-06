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

"""Acquisition-based implementation of the DOM 'XML' feature classes."""

import Core
import xml.dom

from ComputedAttribute import ComputedAttribute


class CDATASection(Core.Text):
    nodeName = "#cdata-section"
    nodeType = Core.Node.CDATA_SECTION_NODE


class Identified:
    """Mix-in class that supports the publicId and systemId attributes."""

    def _identified_mixin_init(self, publicId, systemId):
        d = self.__dict__
        d['publicId'] = publicId
        d['systemId'] = systemId

    def _get_publicId(self):
        return self.publicId

    def _get_systemId(self):
        return self.systemId


class Entity(Identified, Core.Parentless, Core.Node):
    nodeType = Core.Node.ENTITY_NODE
    _readonly = 1
    _in_tree = 0

    _allowed_child_types = (Core.Node.ELEMENT_NODE,
                            Core.Node.PROCESSING_INSTRUCTION_NODE,
                            Core.Node.COMMENT_NODE,
                            Core.Node.TEXT_NODE,
                            Core.Node.CDATA_SECTION_NODE,
                            Core.Node.ENTITY_REFERENCE_NODE)

    def __init__(self, name, publicId, systemId, notationName):
        self._identified_mixin_init(publicId, systemId)
        d = self.__dict__
        d['nodeName'] = name
        d['notationName'] = notationName

    def _cloneNode(self, deep, mutable, document):
        # force children to not to acquire mutability:
        return Core.Node._cloneNode(self, deep, 0, document)

    def _get_notationName(self):
        return self.notationName

    # DOM Level 3 (Working Draft, 01 Sep 2000)
    # I expect some or all of these will become read-only before the
    # recommendation is finished.

    actualEncoding = None
    encoding = None
    version = None

    def _get_actualEncoding(self):
        return self.actualEncoding
    def _set_actualEncoding(self, value):
        self.__dict__['actualEncoding'] = value

    def _get_encoding(self):
        return self.encoding
    def _set_encoding(self, value):
        self.__dict__['value'] = value

    def _get_version(self):
        return self.version
    def _set_version(self, value):
        self.__dict__['version'] = value


class EntityReference(Core.Node):
    nodeType = Core.Node.ENTITY_REFERENCE_NODE
    _readonly = 1

    _allowed_child_types = (Core.Node.ELEMENT_NODE,
                            Core.Node.PROCESSING_INSTRUCTION_NODE,
                            Core.Node.COMMENT_NODE,
                            Core.Node.TEXT_NODE,
                            Core.Node.CDATA_SECTION_NODE,
                            Core.Node.ENTITY_REFERENCE_NODE)

    def __init__(self, name):
        self.__dict__['_in_tree'] = 0
        self.__dict__['nodeName'] = name


class Notation(Identified, Core.Childless, Core.Parentless, Core.Node):
    nodeType = Core.Node.NOTATION_NODE
    _readonly = 1

    def __init__(self, name, publicId, systemId):
        self._identified_mixin_init(publicId, systemId)
        d = self.__dict__
        d['_in_tree'] = 0
        d['nodeName'] = name

    def _cloneNode(self, deep, mutable, document):
        # force children to not to acquire mutability:
        return Core.Node._cloneNode(self, deep, 0, document)

    # DOM Level 3 (working draft, 5 June 2001)

    def _get_textContent(self):
        return ''
    textContent = ''


class ProcessingInstruction(Core.Childless, Core.Node):
    nodeType = Core.Node.PROCESSING_INSTRUCTION_NODE

    def __init__(self, target, data):
        d = self.__dict__
        d['_in_tree'] = 0
        d['nodeName'] = target
        d['target'] = target
        d['nodeValue'] = data
        d['data'] = data

    def _get_data(self):
        return self.data

    def _set_data(self, data):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        d = self.__dict__
        if d['data'] != data:
            d['data'] = data
            d['nodeValue'] = data
            self._changed()

    _set_nodeValue = _set_data

    def _get_target(self):
        return self.target
    target = ComputedAttribute(_get_target, 1)

    # DOM Level 3 (working draft, 5 June 2001)

    def _get_textContent(self):
        return self.nodeValue
    textContent = ComputedAttribute(_get_textContent, 1)


class DocumentType(Identified, Core.Childless, Core.Node):
    nodeType = Core.Node.DOCUMENT_TYPE_NODE
    nodeValue = None
    internalSubset = None

    def __init__(self, qualifiedName, publicId, systemId):
        self._identified_mixin_init(publicId, systemId)
        d = self.__dict__
        d['name'] = qualifiedName
        d['nodeName'] = qualifiedName
        d['_entities'] = []
        d['_notations'] = []
        d['_in_tree'] = 0

    def _get_internalSubset(self):
        return self.internalSubset

    def _get_name(self):
        return self.name

    _get_nodeName = _get_name

    def _set_nodeValue(self, data):
        return

    def _get_entities(self):
        return OwnedEntityMap(self, '_entities')
    entities = ComputedAttribute(_get_entities, 1)

    def _get_notations(self):
        return OwnedEntityMap(self, '_notations')
    notations = ComputedAttribute(_get_notations, 1)

    def isSupported(self, feature, version):
        doc = self.ownerDocument
        if doc:
            impl = doc.implementation
        else:
            impl = Core.theDOMImplementation
        return impl.hasFeature(feature, version)

    # DOM Level 3 (working draft, 5 June 2001)

    def _get_textContent(self):
        return ''
    textContent = ''


class OwnedEntityMap(Core.MapFromParent):
    """
    NamedNodeMap that works on the entity or notation structure
    of a DocumentType.
    """

    def __init__(self, parent, listName):
        Core.MapFromParent.__init__(self, parent)
        self.__dict__['_parentListName'] = listName
        
    def _item_helper(self, itemSource):
        "used by item; create an Attribute from the item and return it"
        # XXX is ownerDocument ok with this?
        #itemSource.__dict__['ownerDocument'] = self._parent
        return itemSource.__of__(self._parent)

    def _nameMatcher(self, itemSource, name):
        return itemSource.nodeName == name

    def _nsMatcher(self, itemSource, namespaceURI, localName):
        return (itemSource.namespaceURI == namespaceURI
                and itemSource.localName == localName)

    def _set_named_item(self, name, matcher, node):
        raise xml.dom.NoModificationAllowedErr()

    def _delFromParentList(self, entities, i):
        raise xml.dom.NoModificationAllowedErr()

    def _addToParentList(self, entities, node):
        raise xml.dom.NoModificationAllowedErr()

    def _key_helper(self, itemSource):
        "Given an item source, return an appropriate key for our mapping"
        if itemSource.prefix:
            return "%s:%s" % (itemSource.prefix,
                              itemSource.localName)
        else:
            return itemSource.localName


# no longer needed
del ComputedAttribute

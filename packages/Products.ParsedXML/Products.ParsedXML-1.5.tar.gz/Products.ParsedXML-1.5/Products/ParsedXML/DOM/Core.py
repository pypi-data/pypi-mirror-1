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

# Performance hacks:
#
#   -  Do not test node objects for truth; use an identity comparison
#      with None instead.  This avoids all attribute lookups and
#      requires exactly two dictionary lookups (module globals and
#      builtins).
#
#   -  There is no Node.__init__(); it doesn't do much for most
#      classes anyway.  This avoids a small performance penalty.

import string
_string = string
del string

import Acquisition
_Acquisition = Acquisition

def _reparent(ob, parent):
    ob.aq_inner.aq_parent = parent
    ob.aq_parent = parent
    if parent is None and ob._in_tree:
        ob.__dict__['_in_tree'] = 0

def _parent_of(ob, aq_inner=_Acquisition.aq_inner,
               aq_parent=_Acquisition.aq_parent):
    return aq_parent(aq_inner(ob))

_aq_base = _Acquisition.aq_base

del Acquisition

from ComputedAttribute import ComputedAttribute

import xml.dom


# legal qualified name pattern, from PyXML xml/dom/Document.py
# see http://www.w3.org/TR/REC-xml-names/#NT-QName
# we don't enforce namespace usage if using namespaces, which basically
# means that we don't disallow a leading ':'
# XXX there's more to the world than ascii a-z
# FIXME: should allow combining characters: fix when Python gets Unicode

try:
    import sre  # Note that Python 1.5.2's re module chokes.  Require sre.
except ImportError:
    def _ok_qualified_name(s, bad_first=(_string.digits + '.-'),
                           good=(_string.letters +
                                 _string.digits + '.-_:')):
        if len(s) < 1:
            return None
        if s[0] in bad_first:
            return None
        for c in s:
            if c not in good:
                return None
        return 1  # Indicates "passed".
else:
    _ok_qualified_name = sre.compile('[a-zA-Z_:][\w\.\-_:]*\Z', sre.UNICODE).match
    del sre

_TupleType = type(())

try:
    unicode
except NameError:
    _StringTypes = (type(''),)
else:
    # can't use u'' syntax due to Python 1.5.2 compatibility requirement
    _StringTypes = (type(''), type(unicode('')))


# http://www.w3.org/TR/1999/REC-xml-names-19990114/#ns-qualnames
def _check_qualified_name(name, uri='ok'):
    "test name for well-formedness"
    if _ok_qualified_name(name) is not None:
        if ":" in name:
            parts = _string.split(name, ":")
            if len(parts) != 2:
                raise xml.dom.NamespaceErr("malformed qualified name")
            if not (parts[0] and parts[1]):
                raise xml.dom.NamespaceErr("malformed qualified name")
            if not uri:
                raise xml.dom.NamespaceErr("no namespace URI for prefix")
        return 1
    else:
        raise xml.dom.InvalidCharacterErr()

# Common namespaces:
XML_NS = "http://www.w3.org/XML/1998/namespace"
XMLNS_NS = "http://www.w3.org/2000/xmlns/"

def _check_reserved_prefixes(prefix, namespaceURI):
    """
    Helper function to centralize the enforcement of reserved prefixes.
    Raises the appropriate NamespaceErr if the prefix is reserved but
    the namespaceURI doesn't match it.
    """
    if prefix == "xml" and namespaceURI != XML_NS:
        raise xml.dom.NamespaceErr(
            "illegal use of the 'xml' prefix")
    if prefix == "xmlns" and namespaceURI != XMLNS_NS:
        raise xml.dom.NamespaceErr(
            "illegal use of the 'xmlns' prefix")


# These are indexes into the list that is used to represent an Attr node.
_ATTR_NS = 0
_ATTR_NAME = 1
_ATTR_LOCALNAME = 2
_ATTR_PREFIX = 3
_ATTR_VALUE = 4
_ATTR_SPECIFIED = 5

# These are used for schema-derived information, and are not used for
# specified attributes.
_ATTR_TYPE = 6
_ATTR_REQUIRED = 7

_SUPPORTED_FEATURES = (
    ("core", None),
    ("xml", None),
    ("traversal", None),
    #("load", None),

    # According to DOM Erratum Core-14, the empty string should be
    # accepted as equivalent to null for hasFeature().
    ("core", ""),
    ("xml", ""),
    ("traversal", ""),
    #("load", ""),

    ("core", "1.0"),
    ("xml", "1.0"),

    ("core", "2.0"),
    ("xml", "2.0"),
    ("traversal", "2.0"),

    #("load", "3.0"),
    )


class _Dummy(_Acquisition.Explicit):
    pass


class DOMImplementation:
    def hasFeature(self, feature, version):
        feature = (_string.lower(feature), version)
        return feature in _SUPPORTED_FEATURES

    def createDocumentType(self, qualifiedName, publicId, systemId):
        _check_qualified_name(qualifiedName)
        import XMLExtended
        doctype = XMLExtended.DocumentType(qualifiedName, publicId, systemId)
        doctype = doctype.__of__(_Dummy())
        _reparent(doctype, None)
        return doctype

    def createDocument(self, namespaceURI, qualifiedName, docType=None):
        return Document(docType, namespaceURI, qualifiedName)

    # DOM Level 3 Core (working draft, 5 Jun 2001)

    def getAs(self, feature):
        return self

    # DOM Level 3 Load/Save (working draft, 9 Feb 2001)

    def createDOMBuilder(self):
        import LoadSave
        return LoadSave.DOMBuilder()

theDOMImplementation = DOMImplementation()


class AttributeControl:
    """Base class that provides reasonable get/set behavior for DOM
    classes."""

    _readonly = 0

    def __setattr__(self, name, value):
        setter = getattr(self, '_set_' + name, None)
        if setter is None:
            getter = getattr(self, '_get_' + name, None)
            if getter:
                raise xml.dom.NoModificationAllowedErr(
                    "read-only attribute: " + `name`)
            else:
                raise AttributeError, "no such attribute: " + `name`
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr(
                "cannot set attribute on read-only node")
        setter(value)


class Node(AttributeControl, _Acquisition.Explicit):
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

    # DOM Level 3 Core (working draft, 5 Jun 2001)
    # enum DocumentOrder
    DOCUMENT_ORDER_PRECEDING = 1
    DOCUMENT_ORDER_FOLLOWING = 2
    DOCUMENT_ORDER_SAME = 5
    DOCUMENT_ORDER_UNORDERED = 6

    # enum TreePosition
    TREE_POSITION_PRECEDING = 1
    TREE_POSITION_FOLLOWING = 2
    TREE_POSITION_ANCESTOR = 3
    TREE_POSITION_DESCENDANT = 4
    TREE_POSITION_SAME = 5
    TREE_POSITION_UNORDERED = 6

    attributes = None

    _children = ()
    _in_tree = 1
    _v_sibling_map = None

    namespaceURI = None
    prefix = localName = None
    nodeValue = None

    def _check_if_ancestor(self, node):
        "Helper function that raises if node is self or an ancestor of self."
        n = self
        node = _aq_base(node)        
        if _aq_base(n) is node:
            raise xml.dom.HierarchyRequestErr()
        if node._children:
            while n is not None:
                n = n.parentNode
                if _aq_base(n) is node:
                    raise xml.dom.HierarchyRequestErr()

    def __cmp__(self, other):
        # This doesn't seem to be getting used; a problem with
        # acquisition?  Jim thinks this may be an old bug that may
        # be resurfacing.  ;-(
        return cmp(id(_aq_base(self)), id(_aq_base(other)))

    def __hash__(self):
        return hash(id(_aq_base(self)))

    def __repr__(self):
        name = self.nodeName or "#"
        type = self.__class__.__name__
        if name[0] == "#":
            name = ""
        else:
            name = " " + `name`
        return "<%s%s at 0x%x>" % (
            type, name, id(_aq_base(self)))

    def _changed(self):
        # Mark the tree as changed this way since nodes can be
        # modified while they're not part of the tree (say, after
        # being removed but before being added somewhere else; the
        # real marking of the tree occurs when the node is re-inserted
        # into the tree).
        try:
            self.aq_acquire('__changed__')(1)
        except AttributeError:
            pass

    def _get_attributes(self):
        return

    def _get_childNodes(self):
        return ChildNodeList(self)
    childNodes = ComputedAttribute(_get_childNodes, 1)

    def _get_firstChild(self):
        if self._children:
            return self._children[0].__of__(self)
    firstChild = ComputedAttribute(_get_firstChild, 1)

    def _get_lastChild(self):
        if self._children:
            return self._children[-1].__of__(self)
    lastChild = ComputedAttribute(_get_lastChild, 1)

    def _get_localName(self):
        return self.localName

    def _get_namespaceURI(self):
        return self.namespaceURI

    def _get_nodeValue(self):
        return self.nodeValue

    def _get_nextSibling(self):
        node = self._getSiblingInfo()[1]
        if node is not None:
            return node.__of__(self.parentNode)
    nextSibling = ComputedAttribute(_get_nextSibling, 1)

    def _get_previousSibling(self):
        node = self._getSiblingInfo()[0]
        if node is not None:
            return node.__of__(self.parentNode)
    previousSibling = ComputedAttribute(_get_previousSibling, 1)

    def _getSiblingInfo(self):
        """
        Return a list containing the previous and next sibling of this node.
        If the sibling map doesn't exist on the parent yet, create it.
        """
        # Acquire the parent.
        if not self._in_tree:
            return [None, None]
        parent = _parent_of(self)
        if parent is None:
            return [None, None]

        # This implementation doesn't scale, but should amortize well
        # if .previousSibling and .nextSibling are actually used
        # much.  Is that enough?  This could be made lazier, but at
        # the expense of readability.
        #
        # The parent stores the sibling map for its children.
        sibmap = parent._v_sibling_map
        if sibmap is None:
            # There is no sibling map, create it.
            sibmap = {}
            parent.__dict__['_v_sibling_map'] = sibmap
        try:
            return sibmap[_aq_base(self)]
        except KeyError:
            # The sibling map hasn't been filled, fill it.
            # The *unwrapped* node is the key, the values are the
            # *wrapped* previous and next siblings.
            prev = None
            siblings = parent._children
            for i in range(len(siblings)):
                node = siblings[i]
                try:
                    next = siblings[i+1]
                except IndexError:
                    next = None
                sibmap[node] = [prev, next]
                prev = node
            return sibmap[_aq_base(self)]

    def _get_nodeName(self):
        return self.nodeName

    def _get_nodeType(self):
        return self.nodeType

    nodeValue = None

    def _get_ownerDocument(self):
        # We leverage Acquisition to get this from the
        # enclosing document.
        try:
            return self.aq_acquire('_acquireDocument')()
        except:
            return
    ownerDocument = ComputedAttribute(_get_ownerDocument, 1)

    def _get_parentNode(self):
        # Acquire the parent.
        if self._in_tree:
            return _parent_of(self)
    parentNode = ComputedAttribute(_get_parentNode, 1)

    def _check_prefix(self, value):
        "check prefix for wellformedness and validity"
        if ":" in value:
            raise xml.dom.NamespaceErr("':' not allowed in prefix")
        _check_qualified_name(value)
        if value is not None and not self.namespaceURI:
            raise xml.dom.NamespaceErr(
                "can't set prefix on a node without a namespace URI")
        if value == "xmlns":
            raise xml.dom.NamespaceErr(
                "can't use 'xmlns' as prefix")
        _check_reserved_prefixes(value, self.namespaceURI)
        if not self.namespaceURI:
            raise xml.dom.NamespaceErr(
                "no prefix allowed on nodes with no namespace URI")

    def _get_prefix(self):
        return self.prefix

    def _set_prefix(self, value):
        return

    def appendChild(self, newChild):
        if self._readonly or (
            newChild.parentNode and newChild.parentNode._readonly):
            raise xml.dom.NoModificationAllowedErr()
        if self.isSameNode(newChild):
            raise xml.dom.HierarchyRequestErr()
        # checking newChild._children here can avoid a lot of calls when
        # building a new tree
        if newChild._children:
            self._check_if_ancestor(newChild)

        children = self._children
        sibmap = self._v_sibling_map
        child = _aq_base(newChild)

        # Setup chidren if we don't have any, don't do this for Attr nodes.
        if not children and isinstance(children, _TupleType):
            self.__dict__['_children'] = children = []

        if child.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            if not child._children:
                return newChild
            for node in child._children:
                if node.nodeType not in self._allowed_child_types:
                    raise xml.dom.HierarchyRequestErr()
            for node in child._children:
                children.append(node)
            del child.__dict__['_children']
            if child.__dict__.has_key('_v_sibling_map'):
                del child.__dict__['_v_sibling_map']
            if self.__dict__.has_key('_v_sibling_map'):
                del self.__dict__['_v_sibling_map']
            self._changed()
            return newChild

        if child.nodeType not in self._allowed_child_types:
            raise xml.dom.HierarchyRequestErr()

        thisdoc = self.ownerDocument or self
        if not thisdoc.isSameNode(newChild.ownerDocument):
            raise xml.dom.WrongDocumentErr()

        # Save the unwrapped child
        children.append(child)

        # Reparent the child
        parent = newChild.parentNode
        if parent is not None:
            parent.removeChild(newChild)
        _reparent(newChild, self)
        if child.__dict__.has_key('_in_tree'):
            del child.__dict__['_in_tree']

        # delete the sibling map, it will be recreated next use        
        if self.__dict__.has_key('_v_sibling_map'):
            del self.__dict__['_v_sibling_map']

        # Notify our containing database object that we have changed
        self._changed()

        return newChild

    def insertBefore(self, newChild, refChild):
        if refChild is None:
            return self.appendChild(newChild)
        if self._readonly or (
            newChild.parentNode and newChild.parentNode._readonly):
            raise xml.dom.NoModificationAllowedErr()
        if self.isSameNode(newChild):
            raise xml.dom.HierarchyRequestErr()
        if self.nodeType == Node.DOCUMENT_NODE:
            if (newChild.ownerDocument is not None
                and not self.isSameNode(newChild.ownerDocument)):
                raise xml.dom.WrongDocumentErr()
        else:
            thisdoc = self.ownerDocument
            thatdoc = newChild.ownerDocument
            if thatdoc is None:
                if thisdoc.isSameNode(newChild):
                    raise xml.dom.HierarchyRequestErr()
            elif not thisdoc.isSameNode(thatdoc):
                raise xml.dom.WrongDocumentErr()
        self._check_if_ancestor(newChild)
        if newChild.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            # This is destructive of the fragment, but I think that's ok.
            # Note that the call to tuple() is required, or a more tedious
            # loop construct would have to be used.
            for child in tuple(newChild._children):
                self.insertBefore(child.__of__(newChild), refChild)
            return newChild
        if newChild.nodeType not in self._allowed_child_types:
            raise xml.dom.HierarchyRequestErr()
        children = self._children
        # setup children if we don't have any; don't do this for Attr nodes
        if not children and isinstance(children, _TupleType):
            self.__dict__['_children'] = children = []
        if newChild.isSameNode(refChild):
            return newChild
        if newChild.parentNode:
            newChild.parentNode.removeChild(newChild)
        
        ref = _aq_base(refChild)
        try:
            i = children.index(ref)
        except ValueError:
            raise xml.dom.NotFoundErr()

        _reparent(newChild, self)
        new = _aq_base(newChild)
        if new.__dict__.has_key('_in_tree'):
            del new.__dict__['_in_tree']
        children.insert(i, new)
        self._changed()
        sibmap = self._v_sibling_map
        if sibmap:
            del self.__dict__['_v_sibling_map']
            #prev, next = sibmap[ref]
            #if prev:
            #    sibmap[prev][1] = new
            #sibmap[new] = [prev, ref]
            #sibmap[ref][0] = new
        return newChild

    def removeChild(self, oldChild):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        child = _aq_base(oldChild)
        if self._children:
            children = self._children
            try:
                i = children.index(child)
            except ValueError:
                raise xml.dom.NotFoundErr()
            del children[i]
            sibmap = self._v_sibling_map
            if sibmap:
                del self.__dict__['_v_sibling_map']
                #prev, next = sibmap[child]
                #if prev:
                #    sibmap[prev][1] = next
                #if next:
                #    sibmap[next][0] = prev
                #del sibmap[child]
            self._changed()
        else:
            raise xml.dom.NotFoundErr()

        child.__dict__['_in_tree'] = 0
        return oldChild

    def replaceChild(self, newChild, oldChild):
        if self._readonly or (
            newChild.parentNode and newChild.parentNode._readonly):
            raise xml.dom.NoModificationAllowedErr()
        if self.isSameNode(newChild):
            raise xml.dom.HierarchyRequestErr()
        if self.nodeType == Node.DOCUMENT_NODE:
            if newChild.ownerDocument \
               and not self.isSameNode(newChild.ownerDocument):
                raise xml.dom.WrongDocumentErr()
        elif self.ownerDocument and newChild.ownerDocument \
           and not self.ownerDocument.isSameNode(newChild.ownerDocument):
            raise xml.dom.WrongDocumentErr()
        # Check for HierarchyRequestErr here so that we can fail
        # before mutating the currrent node:
        if newChild.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            children = newChild._children
            for child in children:
                if child.nodeType not in self._allowed_child_types:
                    raise xml.dom.HierarchyRequestErr()
        elif newChild.nodeType not in self._allowed_child_types:
            raise xml.dom.HierarchyRequestErr()
        self._check_if_ancestor(newChild)
        next = oldChild.nextSibling
        self.removeChild(oldChild)
        if next:
            if newChild.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
                nodes = newChild._children
                while nodes:
                    node = nodes[0].__of__(newChild.parentNode)
                    self.insertBefore(node, next)
            else:
                self.insertBefore(newChild, next)
        else:
            if newChild.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
                nodes = newChild._children
                while nodes:
                    node = nodes[0].__of__(newChild.parentNode)
                    self.appendChild(node)
            else:
                self.appendChild(newChild)
        return oldChild

    def _mergeChildList(self, children):
        """helper function for normalize.  Merge the text nodes in children
        in place according to normalize, normalizing element children as well,
        but doesn't do all of the child list housekeeping.  Returns true
        if changes were made.
        Works for element child lists and attr child lists."""
        changed = 0
        i = 0
        L = []
        for child in children:
            if child.nodeType == Node.TEXT_NODE:
                if child.data == "":
                    # drop this child
                    child.__dict__['_in_tree'] = 0
                    changed = 1
                elif L and L[-1].nodeType == child.nodeType:
                    # merge this child with previous sibling
                    data = L[-1].data + child.data
                    d = L[-1].__dict__
                    d['data'] = d['nodeValue'] = data
                    child.__dict__['_in_tree'] = 0
                    changed = 1
                else:
                    L.append(child)
            elif (child.nodeType == Node.ELEMENT_NODE
                  and child._children):
                child.normalize()
                L.append(child)
            else:
                L.append(child)
        if changed:
            children[:] = L
        return changed

    def normalize(self):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        aChanged = 0
        d = self.__dict__
        if d.has_key('_attributes'):
            attributes = self._attributes
            for attr in attributes:
                attrVal = attributes[0][_ATTR_VALUE]
                if type(attrVal) in _StringTypes:
                    continue
                if len(attrVal) == 1:
                    child = attrVal[0]
                    if child.nodeType == Node.TEXT_NODE and not child.data:
                        del child
                        aChanged = 1
                else:
                    aChanged = self._mergeChildList(attrVal) or aChanged
        children = self._children
        if not children:
            return
        if len(children) == 1:
            child = children[0]
            if child.nodeType == Node.TEXT_NODE and not child.data:
                self.removeChild(child.__of__(self))
            elif (child.nodeType == Node.ELEMENT_NODE
                  and child._children):
                child.__of__(self).normalize()
            return
        cChanged = self._mergeChildList(children)
        if cChanged:
            if d.has_key('_v_sibling_map'):
                # this is now invalid; let it be recreated on demand
                del d['_v_sibling_map']
        if cChanged or aChanged:
            self._changed()

    def hasAttributes(self):
        return 0

    def hasChildNodes(self):
        return self._children and 1 or 0

    def isSupported(self, feature, version):
        if self.ownerDocument:
            impl = self.ownerDocument.implementation
        else:
            impl = theDOMImplementation
        return impl.hasFeature(feature, version)

    def cloneNode(self, deep):
        node = _aq_base(self)
        clone = node._cloneNode(deep and 1 or 0,
                                mutable=1, document=self.ownerDocument)
        clone.__dict__['_in_tree'] = 0
        clone = clone.__of__(self)
        return clone

    def _cloneNode(self, deep, mutable, document):
        # self is *not* an acquisition wrapper!
        clone = self.__class__.__basicnew__()
        d = clone.__dict__
        d.update(self.__dict__)
        if deep:
            if self._children:
                # make a recursive clone:
                d['_children'] = L = []
                for child in self._children:
                    L.append(child._cloneNode(deep, mutable, document))
        elif d.has_key('_children'):
            del d['_children']
        if d.has_key('_v_sibling_map'):
            del d['_v_sibling_map']
        if mutable and d.has_key('_readonly'):
            del d['_readonly']
        return clone

    # DOM Level 3 (Working Draft, 5 Jun 2001)

    def _get_baseURI(self):
        node = self
        d = node.__dict__
        while not d.has_key('baseURI'):
            node = self.parentNode
            if node is None:
                return
            d = node.__dict__
        return d['baseURI']
    baseURI = ComputedAttribute(_get_baseURI, 1)

    def getAs(self, feature):
        return self

    def isSameNode(self, other):
        # This is useful since cmp() (hence ==, !=) don't seem to work
        # with acquisition.
        return (_aq_base(self) is _aq_base(other))

    def lookupNamespacePrefix(self, namespaceURI):
        node = self
        while node is not None:
            ns_map = getattr(self, '_ns_uri_prefixes', None)
            if ns_map and ns_map.has_key(namespaceURI):
                return ns_map[namespaceURI][0]
            node = node.parentNode

    def lookupNamespaceURI(self, prefix):
        node = self
        while node is not None:
            ns_map = getattr(self, '_ns_prefix_uri', None)
            if ns_map and ns_map.has_key(prefix):
                return ns_map[prefix]
            node = node.parentNode


class Parentless:
    """Node mixin that doesn't have a parent node."""

    parentNode = None
    nextSibling = None
    previousSibling = None

    def _get_parentNode(self):
        return

    def _get_previousSibling(self):
        return

    def _get_nextSibling(self):
        return

    def _getSiblingInfo(self):
        return [None, None]


class Childless:
    """Node mixin that doesn't allow child nodes.

    This ensures safety when used as a base class for node types that
    should never have children of their own, and allows slightly
    faster response for some methods.
    """

    _allowed_child_types = ()

    def _get_firstChild(self):
        return
    firstChild = None

    def _get_lastChild(self):
        return
    lastChild = None

    def appendChild(self, newChild):
        raise xml.dom.HierarchyRequestErr()

    def insertBefore(self, newChild, oldChild):
        raise xml.dom.HierarchyRequestErr()

    def removeChild(self, oldChild):
        raise xml.dom.NotFoundErr()

    def replaceChild(self, newChild, oldChild):
        # This could reasonably raise NotFoundErr as well.
        raise xml.dom.HierarchyRequestErr()

    def hasChildNodes(self):
        return 0

    def normalize(self):
        return


class TextualContent:
    """Mixin class defining the recursive support for textContent
    needed for some types of container nodes.
    """
    # DOM Level 3 (working draft, 5 June 2001)

    def _get_textContent(self):
        L = []
        for node in self.childNodes:
            nodeType = node.nodeType
            if (  nodeType == Node.COMMENT_NODE
                  or nodeType == Node.PROCESSING_INSTRUCTION_NODE):
                continue
            if nodeType == Node.TEXT_NODE:
                text = node.data
            else:
                text = node._get_textContent()
            L.append(text)
        if L:
            return _string.join(L, '')
        else:
            return ''
    textContent = ComputedAttribute(_get_textContent, 1)


class Document(Parentless, TextualContent, Node):
    nodeName = "#document"
    nodeType = Node.DOCUMENT_NODE

    _allowed_child_types = (Node.ELEMENT_NODE,
                            Node.COMMENT_NODE,
                            Node.PROCESSING_INSTRUCTION_NODE)

    _doctype = None
    _in_tree = 0
    implementation = theDOMImplementation

    def __init__(self, doctype, namespaceURI, qualifiedName):
        _check_qualified_name(qualifiedName, namespaceURI)
        if namespaceURI:
            e = Element(namespaceURI, qualifiedName, element_id=0)
        else:
            e = Element(None, qualifiedName, element_id=0)
        del e.__dict__['_in_tree']
        if doctype:
            if doctype._in_tree:
                raise xml.dom.WrongDocumentErr()
            doctype = _aq_base(doctype)
            self.__dict__['_doctype'] = doctype
            del doctype.__dict__['_in_tree']
            L = [doctype, e]
        else:
            L = [e]
        self.__dict__['_children'] = L
        self.__dict__['_attr_info'] = {}
        self.__dict__['_element_count'] = 1
        
    def _set_nodeValue(self, data):
        return None

    def _get_doctype(self):
        if self._doctype is None:
            return
        else:
            return self._doctype.__of__(self)
    doctype = ComputedAttribute(_get_doctype)

    def _get_implementation(self):
        return self.implementation

    def _get_documentElement(self):
        for node in self._children:
            if node.nodeType == Node.ELEMENT_NODE:
                return node.__of__(self)
    documentElement = ComputedAttribute(_get_documentElement)

    ownerDocument = None
    def _get_ownerDocument(self):
        return

    def _acquireDocument(self):
        # This method gets acquired by descendents that want their
        # owner; the result is an unwrapped Document node.
        return self

    # child insertion methods:
    # check for adding 2nd element node; other checks are elsewhere

    # helper method for 2nd element node detection
    def _hasDocumentElement(self):
        for node in self._children:
            if node.nodeType == Node.ELEMENT_NODE:
                return 1

    def appendChild(self, newChild):
        if newChild.nodeType == Node.DOCUMENT_TYPE_NODE:
            raise xml.dom.HierarchyRequestErr(
                "cannot change document type via tree manipulation")
        if (newChild.nodeType == Node.ELEMENT_NODE and self._children
            and self._hasDocumentElement()):
            raise xml.dom.HierarchyRequestErr()
        return Node.appendChild(self, newChild)

    def insertBefore(self, newChild, refChild):
        if newChild.nodeType == Node.DOCUMENT_TYPE_NODE:
            raise xml.dom.HierarchyRequestErr(
                "cannot change document type via tree manipulation")
        if (newChild.nodeType == Node.ELEMENT_NODE and self._children
            and self._hasDocumentElement()):
            raise xml.dom.HierarchyRequestErr()
        return Node.insertBefore(self, newChild, refChild)

    def removeChild(self, oldChild):
        if oldChild.nodeType == Node.DOCUMENT_TYPE_NODE:
            raise xml.dom.NoModificationAllowedErr(
                "cannot change document type via tree manipulation")
        return Node.removeChild(self, oldChild)

    def replaceChild(self, newChild, oldChild):
        if (newChild.nodeType == Node.ELEMENT_NODE and self._children
            and oldChild.nodeType != Node.ELEMENT_NODE
            and self._hasDocumentElement()):
            raise xml.dom.HierarchyRequestErr()
        if (newChild.nodeType == Node.DOCUMENT_TYPE_NODE
            or oldChild.nodeType == Node.DOCUMENT_TYPE_NODE):
            raise xml.dom.HierarchyRequestErr(
                "cannot change document type via tree manipulation")
        return Node.replaceChild(self, newChild, oldChild)        

    # unknown acquisition environment, no computedAttribute unwrapping
    # so we must redefine these methods
    def _get_childNodes(self):
        return ChildNodeList(self)
    childNodes = ComputedAttribute(_get_childNodes)

    def _get_firstChild(self):
        if self._children:
            return self._children[0].__of__(self)
    firstChild = ComputedAttribute(_get_firstChild)

    def _get_lastChild(self):
        if self._children:
            return self._children[-1].__of__(self)
    lastChild = ComputedAttribute(_get_lastChild)

    def createAttribute(self, name):
        _check_qualified_name(name)
        return Attr([None, name, None, None, "", 1], self).__of__(self)

    def createAttributeNS(self, namespaceURI, qualifiedName):
        _check_qualified_name(qualifiedName, namespaceURI)
        names = _string.split(qualifiedName, ":", 1)
        localName = names[-1]
        if len(names) > 1:
            prefix = names[0]
            _check_reserved_prefixes(prefix, namespaceURI)
        else:
            prefix = None
        item = [namespaceURI, qualifiedName, localName, prefix, "", 1]
        return Attr(item, self).__of__(self)

    def createCDATASection(self, data):
        import XMLExtended
        return XMLExtended.CDATASection(data).__of__(self)

    def createComment(self, data):
        return Comment(data).__of__(self)

    def createDocumentFragment(self):
        return DocumentFragment(self).__of__(self)

    def createElement(self, tagName):
        _check_qualified_name(tagName)
        e = Element(None, tagName, element_id=self._element_count).__of__(self)
        self.__dict__['_element_count'] = self._element_count + 1
        if self._attr_info.has_key(tagName):
            e.__dict__['_attr_info'] = self._attr_info[tagName]
        self._changed()
        return e

    def createElementNS(self, namespaceURI, qualifiedName, stuff=None):
        _check_qualified_name(qualifiedName, namespaceURI)
        if ":" in qualifiedName and not namespaceURI:
            raise xml.dom.NamespaceErr(
                "tag name with prefix has no namespace URI")
        e = Element(namespaceURI, qualifiedName, stuff,
                    element_id=self._element_count).__of__(self)
        self.__dict__['_element_count'] = self._element_count + 1
        if self._attr_info.has_key(qualifiedName):
            e.__dict__['_attr_info'] = self._attr_info[qualifiedName]
        self._changed()
        return e

    def createEntityReference(self, name):
        if not _ok_qualified_name(name):
            raise xml.dom.InvalidCharacterErr()
        import XMLExtended
        return XMLExtended.EntityReference(name).__of__(self)

    def createProcessingInstruction(self, target, data):
        if not _ok_qualified_name(target):
            raise xml.dom.InvalidCharacterErr()
        if _string.lower(target) == "xml":
            raise xml.dom.InvalidCharacterErr(
                "'%s' not allowed as a processing instruction target"
                % target)
        import XMLExtended
        return XMLExtended.ProcessingInstruction(target, data).__of__(self)

    def createTextNode(self, data):
        return Text(data).__of__(self)

    def getElementById(self, elementId):
        # This performs a depth-first search of the tree for every request
        # (if any ID attributes are defined); this is necessary in order
        # to create the proper chain of acquisition wrappers.
        #
        info = self._compute_id_map()
        if not info:
            return
        queue = [self.documentElement]
        while queue:
            elem = queue.pop(0)
            if info.has_key(elem.tagName):
                attrs = info[elem.tagName]
                for name in attrs:
                    if elem.getAttribute(name) == elementId:
                        return elem
            if elem.hasChildNodes():
                childNodes = elem.childNodes
                L = []
                for node in childNodes:
                    if node.nodeType == Node.ELEMENT_NODE:
                        L.append(node)
                queue[:0] = L

    def _compute_id_map(self):
        # Returns a mapping from tagName to a list of attribute names
        # that bear IDs.  The computed value is cached on the instance;
        # if this is used during a transaction that modifies the document
        # the structure will be saved as an "accidental" side effect.
        # Since the DOM does not support changing the content model, this
        # is acceptable.
        try:
            return self._id_info
        except AttributeError:
            self.__dict__['_id_info'] = info = {}
            for tagName, L in self._attr_info.items():
                for item in L:
                    if item[_ATTR_TYPE] == "ID":
                        if info.has_key(tagName):
                            info[tagName].append(item[_ATTR_NAME])
                        else:
                            info[tagName] = [item[_ATTR_NAME]]
            return info

    def getElementsByTagName(self, tagName):
        nodeList = SimpleNodeList()
        _getElementsByTagNameHelper(self, tagName, nodeList._data)
        return nodeList

    def getElementsByTagNameNS(self, namespaceURI, localName):
        nodeList = SimpleNodeList()
        _getElementsByTagNameNSHelper(
            self, namespaceURI, localName, nodeList._data)
        return nodeList

    def isSupported(self, feature, version):
        return self.implementation.hasFeature(feature, version)

    def importNode(self, importedNode, deep):
        if importedNode.nodeType in (
            Node.DOCUMENT_NODE, Node.DOCUMENT_TYPE_NODE):
            raise xml.dom.NotSupportedErr(
                "can't import this kind of node")
        doc = importedNode.ownerDocument
        if doc.implementation == self.implementation:
            # same implementation, so we're in good shape
            node = _aq_base(importedNode)
            clone = node._cloneNode(deep and 1 or 0, mutable=1, document=self)
            clone.__dict__['_in_tree'] = 0
            clone = clone.__of__(self)
            if hasattr(clone, '_set_owner_document'):
                clone._set_owner_document(self)
            return clone
        raise xml.dom.NotSupportedErr(
            "can't import from a different DOM implementation")

    # DOM Level 2 Traversal

    def createNodeIterator(self, root, whatToShow, filter,
                           entityReferenceExpansion):
        import Traversal
        return Traversal.NodeIterator(root, whatToShow, filter,
                                      entityReferenceExpansion)

    def createTreeWalker(self, root, whatToShow, filter,
                         entityReferenceExpansion):
        import Traversal
        return Traversal.TreeWalker(root, whatToShow, filter,
                                    entityReferenceExpansion)

    # DOM Level 3 (Working Draft, 5 Jun 2001)
    # I expect some or all of these will become read-only before the
    # recommendation is finished.
    actualEncoding = None
    encoding = None
    standalone = 0
    strictErrorChecking = 0
    version = None

    # Override the inherited handler for textContent since the
    # acquisition context is different.
    textContent = ComputedAttribute(TextualContent._get_textContent)

    def _get_actualEncoding(self):
        return self.actualEncoding
    def _set_actualEncoding(self, value):
        self.__dict__['actualEncoding'] = value
        self._changed()

    def _get_encoding(self):
        return self.encoding
    def _set_encoding(self, value):
        self.__dict__['encoding'] = value
        self._changed()

    def _get_standalone(self):
        return self.standalone
    def _set_standalone(self, value):
        self.__dict__['standalone'] = value and 1 or 0
        self._changed()

    def _get_strictErrorChecking(self):
        return self.strictErrorChecking
    def _set_strictErrorChecking(self, value):
        self.__dict__['strictErrorChecking'] = value and 1 or 0
        self._changed()

    def _get_version(self):
        return self.version
    def _set_version(self, value):
        self.__dict__['version'] = value
        self._changed()

    def normalizeNS(self):
        pass

    def setBaseURI(self, baseURI):
        # we really need something like urlparse.isabs()!
        if ':' not in baseURI:
            raise xml.dom.SyntaxErr("baseURI is not an absolute URI")
        self.__dict__['baseURI'] = baseURI
        self._changed()


def _getElementsByTagNameHelper(parent, name, list):
    for node in parent._children:
        if node.nodeType == Node.ELEMENT_NODE:
            if (name == "*" or node.tagName == name):
                list.append(node.__of__(parent))
            _getElementsByTagNameHelper(node.__of__(parent), name, list)

def _getElementsByTagNameNSHelper(parent, nsURI, localName, list):
    for node in parent._children:
        if node.nodeType == Node.ELEMENT_NODE:
            if ((localName == "*" or node.localName == localName) and
                (nsURI == "*" or node.namespaceURI == nsURI)):
                list.append(node.__of__(parent))
            _getElementsByTagNameNSHelper(node.__of__(parent),
                                          nsURI, localName, list)


class DocumentFragment(Parentless, TextualContent, Node):
    nodeName = "#document-fragment"
    nodeType = Node.DOCUMENT_FRAGMENT_NODE
    parentNode = None

    _in_tree = 0

    _allowed_child_types = (Node.ELEMENT_NODE,
                            Node.TEXT_NODE,
                            Node.PROCESSING_INSTRUCTION_NODE,
                            Node.COMMENT_NODE,
                            Node.CDATA_SECTION_NODE,
                            Node.ENTITY_REFERENCE_NODE)

    def __init__(self, owner):
        self.__dict__['ownerDocument'] = owner

    def _set_nodeValue(self, data):
        return None

    def _get_ownerDocument(self):
        return self.ownerDocument

    def _get_parentNode(self):
        return

    def _set_owner_document(self, doc):
        self.__dict__['ownerDocument'] = doc


def _split_qname(namespaceURI, qualifiedName):
    if ":" in qualifiedName:
        prefix, localName = _string.split(qualifiedName, ':', 1)
        if prefix == "xml" and namespaceURI != XML_NS:
            raise xml.dom.NamespaceErr(
                "illegal use of the 'xml' prefix")
        if prefix == "xmlns" and namespaceURI != XMLNS_NS:
            raise xml.dom.NamespaceErr(
                "illegal use of the 'xmlns' prefix")
        return prefix, localName
    else:
        return None, qualifiedName


# Element _attribute members can be shared with Attr nodes; see comment
# at the Attr class.
class Element(TextualContent, Node):
    nodeType = Node.ELEMENT_NODE

    _allowed_child_types = (Node.ELEMENT_NODE,
                            Node.TEXT_NODE,
                            Node.COMMENT_NODE,
                            Node.PROCESSING_INSTRUCTION_NODE,
                            Node.CDATA_SECTION_NODE,
                            Node.ENTITY_REFERENCE_NODE)

    _attributes = ()
    _attr_info = ()

    def __init__(self, namespaceURI, qualifiedName, stuff=None, element_id=0):
        d = self.__dict__
        d['_in_tree'] = 0
        d['_element_id'] = element_id
        d['nodeName'] = qualifiedName
        d['tagName'] = qualifiedName
        if stuff:
            d['namespaceURI'] = namespaceURI
            d['prefix'] = stuff[0]
            d['localName'] = stuff[1]
        elif namespaceURI:
            d['namespaceURI'] = namespaceURI
            prefix, localName = _split_qname(namespaceURI, qualifiedName)
            d['prefix'] = prefix
            d['localName'] = localName

    def _cloneNode(self, deep, mutable, document):
        clone = Node._cloneNode(self, deep, mutable, document)
        d = clone.__dict__
        # create element_id for cloned element
        d['_element_id'] = document._element_count
        document.__dict__['_element_count'] = document._element_count + 1
        # we need to notify changes as we change element_count
        self._changed()
        
        info = document._attr_info.get(self.tagName)
        if info:
            d['_attr_info'] = info
        elif clone._attr_info:
            del d['_attr_info']
            
        if d.has_key('_attributes'):
            d['_attributes'] = attrs = map(list, self._attributes)
            for i in range(len(attrs) - 1, -1, -1):
                item = attrs[i]
                if not item[_ATTR_SPECIFIED]:
                    del attrs[i]
        return clone

    def _set_nodeValue(self, data):
        return None

    def _set_prefix(self, value):
        self._check_prefix(value)
        d = self.__dict__
        d['prefix'] = value
        s = "%s:%s" % (value, self.localName)
        d['nodeName'] = s
        # Do this here to avoid paying for a method call
        d['tagName'] = s

    def _get_tagName(self):
        return self.tagName

    tagName = ComputedAttribute(_get_tagName, 1)

    # not DOM, but convenience elementId accessor. Each element node
    # has a document-unique element_id
    def _get_elementId(self):
        return self._element_id

    elementId = ComputedAttribute(_get_elementId, 1)
    
    def getElementsByTagName(self, tagName):
        nodeList = SimpleNodeList()
        _getElementsByTagNameHelper(self, tagName, nodeList._data)
        return nodeList

    def getElementsByTagNameNS(self, namespaceURI, localName):
        nodeList = SimpleNodeList()
        _getElementsByTagNameNSHelper(
            self, namespaceURI, localName, nodeList._data)
        return nodeList

    def _get_attributes(self):
        return AttributeMap(self)
    attributes = ComputedAttribute(_get_attributes, 1)

    def hasAttributes(self):
        return ((self._attributes or self._attr_info) and 1 or 0)

    def getAttribute(self, name):
        for item in self._attributes:
            if name == item[_ATTR_NAME]:
                if type(item[_ATTR_VALUE]) in _StringTypes:
                    # value is a string
                    return item[_ATTR_VALUE]
                # value is a subtree
                return _attr_get_value(item[_ATTR_VALUE])
        for item in self._attr_info:
            if name == item[_ATTR_NAME]:
                # will always be a string in the current implementation
                return item[_ATTR_VALUE]
        return ""

    def getAttributeNode(self, name):
        for item in self._attributes:
            if name == item[_ATTR_NAME]:
                doc = self.ownerDocument
                return Attr(item, doc, self).__of__(self)
        for item in self._attr_info:
            if name == item[_ATTR_NAME]:
                item = item[:]
                if self._attributes:
                    self._attributes.append(item)
                else:
                    self.__dict__['_attributes'] = [item]
                return Attr(item, self.ownerDocument, self).__of__(self)

    def getAttributeNS(self, namespaceURI, localName):
        for item in self._attributes:
            if (  namespaceURI == item[_ATTR_NS]
                  and localName == item[_ATTR_LOCALNAME]):
                if type(item[_ATTR_VALUE]) in _StringTypes:
                    # value is a string
                    return item[_ATTR_VALUE]
                # value is a subtree
                return _attr_get_value(item[_ATTR_VALUE])
        for item in self._attr_info:
            if (  namespaceURI == item[_ATTR_NS]
                  and localName == item[_ATTR_LOCALNAME]):
                # will always be a string in the current implementation
                return item[_ATTR_VALUE]
        return ""

    def getAttributeNodeNS(self, namespaceURI, localName):
        for item in self._attributes:
            if (  namespaceURI == item[_ATTR_NS]
                  and localName == item[_ATTR_LOCALNAME]):
                return Attr(item, self.ownerDocument, self).__of__(self)
        for item in self._attr_info:
            if (  namespaceURI == item[_ATTR_NS]
                  and localName == item[_ATTR_LOCALNAME]):
                item = item[:]
                if self._attributes:
                    self._attributes.append(item)
                else:
                    self.__dict__['_attributes'] = [item]
                return Attr(item, self.ownerDocument, self).__of__(self)

    def hasAttribute(self, name):
        for item in self._attributes:
            if name == item[_ATTR_NAME]:
                return 1
        for item in self._attr_info:
            if name == item[_ATTR_NAME]:
                return 1
        return 0

    def hasAttributeNS(self, namespaceURI, localName):
        for item in self._attributes:
            if (  namespaceURI == item[_ATTR_NS]
                  and localName == item[_ATTR_LOCALNAME]):
                return 1
        for item in self._attr_info:
            if (  namespaceURI == item[_ATTR_NS]
                  and localName == item[_ATTR_LOCALNAME]):
                return 1
        return 0

    def removeAttribute(self, name):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        for i in range(len(self._attributes)):
            item = self._attributes[i]
            if item[_ATTR_NAME] == name:
                break
        else:
            return
        if not self._attributes:
            self.__dict__['_attributes'] = []
        del self._attributes[i]
        if item[_ATTR_SPECIFIED]:
            self._changed()

    def removeAttributeNS(self, namespaceURI, localName):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        for i in range(len(self._attributes)):
            item = self._attributes[i]
            if (item[_ATTR_NS] == namespaceURI
                and item[_ATTR_LOCALNAME] == localName):
                if not self._attributes:
                    self.__dict__['_attributes'] = []
                del self._attributes[i]
                self._changed()
                return

    def removeAttributeNode(self, oldAttr):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        item = oldAttr._item
        if item in self._attributes:
            self._attributes.remove(item)
            oldAttr._set_owner_element(None)
            if item[_ATTR_SPECIFIED]:
                self._changed()
            return oldAttr
        else:
            raise xml.dom.NotFoundErr()

    # Because we don't _changed on any existing attr nodes, all attr nodes
    # must have the same persistent parent as their ownerElement
    def setAttribute(self, name, value):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        if not _ok_qualified_name(name):
            raise xml.dom.InvalidCharacterErr()
        if type(value) not in _StringTypes:
            raise TypeError, "attribute value must be a string"
        if self._attributes:
            for item in self._attributes:
                if (  name == item[_ATTR_NAME]
                      and not item[_ATTR_NS]):
                    if type(item[_ATTR_VALUE]) in _StringTypes:
                        # value is a string
                        if item[_ATTR_VALUE] != value:
                            item[_ATTR_VALUE] = value
                            self._changed()
                    else:
                        # value is a list of children, there's an Attr node
                        # for this attr which shares this list.
                        if _attr_get_value(item[_ATTR_VALUE]) != value:
                            _attr_set_value(item, value)
                            self._changed()
                    return
        # attr hasn't been found
        if not self._attributes:
            self.__dict__['_attributes'] = []
        # should look up namespaceURI here...
        self._attributes.append([None, name, None, None, value, 1])
        self._changed()

    # Because we don't _changed on any existing attr nodes, all attr nodes
    # must have the same persistent parent as their ownerElement
    def setAttributeNS(self, namespaceURI, qualifiedName, value):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        _check_qualified_name(qualifiedName, namespaceURI)
        if ":" in qualifiedName:
            prefix, localName = _string.split(qualifiedName, ":", 1)
            _check_reserved_prefixes(prefix, namespaceURI)
        elif namespaceURI:
            prefix = None
            localName = qualifiedName
        else:
            prefix = None
            localName = qualifiedName
        if self._attributes:
            # replace existing attribute rather than add new one
            for item in self._attributes:
                if (  namespaceURI == item[_ATTR_NS]
                      and localName == item[_ATTR_LOCALNAME]):
                    if type(item[_ATTR_VALUE]) in _StringTypes:
                        # value is a string
                        if (  item[_ATTR_VALUE] != value
                              or item[_ATTR_PREFIX] != prefix):
                            item[_ATTR_VALUE] = value
                            item[_ATTR_PREFIX] = prefix
                            item[_ATTR_NAME] = "%s:%s" % (
                                prefix, item[_ATTR_LOCALNAME])
                            self._changed()
                    else:
                        # value is a list of children, there's an Attr node
                        # for this attr which shares this list.
                        if (  _attr_get_value(item[_ATTR_VALUE]) != value
                              or item[_ATTR_PREFIX] != prefix):
                            _attr_set_value(item, value)
                            item[_ATTR_PREFIX] = prefix
                            item[_ATTR_NAME] = "%s:%s" % (
                                prefix, item[_ATTR_LOCALNAME])
                            self._changed()
                    return
        if not self._attributes:
            self.__dict__['_attributes'] = []
        self._attributes.append(
            [namespaceURI, qualifiedName, localName, prefix, value, 1])
        self._changed()

    def setAttributeNode(self, newAttr):
        return self._set_attribute_node(
            newAttr.name, _attr_item_match_name, newAttr)

    def setAttributeNodeNS(self, newAttr):
        name = (newAttr.namespaceURI, newAttr.localName)
        return self._set_attribute_node(
            name, _attr_item_match_ns, newAttr)

    def _set_attribute_node(self, name, matcher, newAttr):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        if newAttr.ownerElement:
            raise xml.dom.InuseAttributeErr()
        if newAttr.nodeType != Node.ATTRIBUTE_NODE:
            raise xml.dom.HierarchyRequestErr(
                "attributes must have nodeType xml.dom.Node.ATTRIBUTE_NODE")
        if not self.ownerDocument.isSameNode(newAttr.ownerDocument):
            raise xml.dom.WrongDocumentErr()
        oldAttr = None
        if not self._attributes:
            self.__dict__['_attributes'] = []
        for i in range(len(self._attributes)):
            item = self._attributes[i]
            if matcher(item, name):
                # replace existing node # XXX set ownerElement for other nodes
                oldAttr = Attr(item, self.ownerDocument).__of__(self)
                self._attributes[i] = newAttr._item
                break
        if oldAttr is None:
            self._attributes.append(newAttr._item)
        newAttr._set_owner_element(self)
        self._changed()
        return oldAttr


class ChildNodeList:
    """NodeList implementation that provides the children of a single node.

    This is returned by Node.childNodes and Node._get_childNodes().
    The list operations supported by this object can be used to mutate
    the document contents.

    """
    def __init__(self, parent):
        self.__dict__['_parent'] = parent

    def __getstate__(self):
        raise RuntimeError, "ChildNodeList instances cannot be stored"

    def item(self, i):
        try:
            return self[i]
        except IndexError:
            return

    def __getitem__(self, i):
        return self._parent._children[i].__of__(self._parent)

    def __setitem__(self, i, newChild):
        p = self._parent
        oldChild = p._children[i].__of__(p)
        p.replaceChild(newChild, oldChild)

    def __delitem__(self, i):
        oldChild = self._parent._children[i].__of__(self._parent)
        self._parent.removeChild(oldChild)

    def _get_length(self):
        return len(self._parent._children)
    __len__ = _get_length

    def __getattr__(self, name):
        if name == "length":
            return len(self._parent._children)
        raise AttributeError, name

    def __setattr__(self, name, value):
        if name == "length":
            raise xml.dom.NoModificationAllowedErr()
        else:
            raise TypeError, "NodeList has only read-only attributes"

    def __nonzero__(self):
        return self._parent._children and 1 or 0

    def count(self, value):
        value = _aq_base(value)
        for node in self._parent._children:
            if node is value:
                return 1
        return 0

    def index(self, value):
        children = self._parent._children
        value = _aq_base(value)
        for i in range(len(children)):
            if value is children[i]:
                return i
        raise ValueError, "NodeList.index(x): x not in sequence"


class SimpleNodeList:
    """NodeList implementation that contains pre-wrapped nodes.

    This is returned by the getElementsByTagName() and
    getElementsByTagNameNS() methods of Document and Element.
    It cannot be used to mutate the document contents.

    """
    def __init__(self, list=None):
        if list is None:
            list = []
        self.__dict__['_data'] = list

    def __getstate__(self):
        raise RuntimeError, "SimpleNodeList instances cannot be stored"

    #
    #  NodeList interface
    #

    def __getattr__(self, name):
        if name == "length":
            return len(self._data)
        raise AttributeError, name

    def __setattr__(self, name, value):
        if name == "length":
            raise xml.dom.NoModificationAllowedErr()
        self.__dict__[name] = value

    def _get_length(self):
        return len(self._data)

    def item(self, i):
        if 0 <= i < len(self._data):
            return self._data[i]

    #
    #  Read-only sequence interface
    #

    def __contains__(self, obj):
        base = _aq_base(obj)
        for node in self._data:
            if _aq_base(node) is base:
                return 1
        return 0

    def __getitem__(self, i):
        return self._data[i]

    def __getslice__(self, i, j):
        return SimpleNodeList(self._data[i:j])

    def __len__(self):
        return len(self._data)

    def __nonzero__(self):
        return self._data and 1 or 0

    def count(self, value):
        value = _aq_base(value)
        for node in self._data:
            if _aq_base(node) is value:
                return 1
        return 0

    def index(self, value):
        value = _aq_base(value)
        for i in range(len(self._data)):
            base = _aq_base(self._data[i])
            if value is base:
                return i
        raise ValueError, "NodeList.index(x): x not in sequence"


class CharacterData(Childless, Node):
    def __init__(self, data):
        d = self.__dict__
        d['_in_tree'] = 0
        d['data'] = data
        d['nodeValue'] = data

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

    def _get_length(self):
        return len(self.data)
    length = ComputedAttribute(_get_length, 1)

    def __len__(self):
        return len(self.data)

    def appendData(self, arg):
        if arg:
            data = self.data + arg
            d = self.__dict__
            d['data'] = data
            d['nodeValue'] = data
            self._changed()

    def deleteData(self, offset, count):
        if count < 0 or offset < 0 or offset > len(self.data):
            raise xml.dom.IndexSizeErr()
        if count:
            data = self.data[:offset] + self.data[offset+count:]
            self.__dict__['data'] = data
            self.__dict__['nodeValue'] = data
            self._changed()

    def insertData(self, offset, arg):
        if offset < 0 or offset > len(self.data):
            raise xml.dom.IndexSizeErr()
        if arg:
            data = self.data
            data = _string.join((data[:offset], arg, data[offset:]), '')
            self.__dict__['data'] = data
            self.__dict__['nodeValue'] = data
            self._changed()

    def replaceData(self, offset, count, arg):
        if count < 0 or offset < 0 or offset > len(self.data):
            raise xml.dom.IndexSizeErr()
        if count or arg:
            data = self.data
            data = _string.join((data[:offset], arg, data[offset+count:]), '')
            self.__dict__['data'] = data
            self.__dict__['nodeValue'] = data
            self._changed()

    def substringData(self, offset, count):
        if count < 0 or offset < 0 or offset > len(self.data):
            raise xml.dom.IndexSizeErr()
        return self.data[offset:offset+count]

    # DOM Level 3 (working draft, 5 June 2001)

    def _get_textContent(self):
        return self.nodeValue
    textContent = ComputedAttribute(_get_textContent, 1)


class Text(CharacterData):
    nodeName = "#text"
    nodeType = Node.TEXT_NODE

    def splitText(self, offset):
        if offset < 0 or offset > len(self.data):
            raise xml.dom.IndexSizeErr()
        parent = self.parentNode
        newText = Text(self.data[offset:])
        data = self.data[:offset]
        self.__dict__['data'] = self.__dict__['nodeValue'] = data
        if parent is not None:
            newText = newText.__of__(parent)
            sibmap = parent._v_sibling_map
            if sibmap:
                del self.__dict__['_v_sibling_map']
                #prev, next = sibmap[_aq_base(self)]
                #if next is not None:
                #    next = next.__of__(parent)
            else:
                next = self.nextSibling
            if next is None:
                parent.appendChild(newText)
            else:
                parent.insertBefore(newText, next.__of__(parent))
        self._changed()
        return newText

    # DOM Level 3 (working draft 01 Sep 2000)
    isWhitespaceInElementContent = 0
    def _get_isWhitespaceInElementContent(self):
        return self.isWhitespaceInElementContent


class Comment(CharacterData):
    nodeName = "#comment"
    nodeType = Node.COMMENT_NODE


# Attr nodes can share their _children with the attribute structure of
# their ownerElements, so this list reference must never be changed - don't
# replace _children, instead add and remove list members.  Same for _item
# members, which are shared with the ownerElement and other Attr ndoes.
#
# We expect that the usual access of attrs is via the element string methods
# getAttribute* and setAttribute, so usually attr values are stored as strings
# in the element.  When getAttributeNode is called, we turn the string into a
# list with a single text node, the attr node shares this reference.  Similarly
# for setAttributeNode.  We could stay with the string in many cases at the
# cost of complexity.
class Attr(Parentless, Node):
    nodeType = Node.ATTRIBUTE_NODE

    _in_tree = 0

    _allowed_child_types = (Node.TEXT_NODE,
                            Node.ENTITY_REFERENCE_NODE)

    def __init__(self, item, ownerDocument, ownerElement=None):
        d = self.__dict__
        # attributes that must be shared with the ownerElement's representation
        if type(item[_ATTR_VALUE]) in _StringTypes:
            # turn string representation into list of children
            itemNode = Text(item[_ATTR_VALUE])
            del itemNode.__dict__['_in_tree']
            item[_ATTR_VALUE] = [itemNode]
        d['_children'] = item[_ATTR_VALUE]
        d['_item'] = item
        # attributes that aren't shared with the ownerElement
        d['ownerDocument'] = ownerDocument
        if item[_ATTR_NS]:
            d['namespaceURI'] = item[_ATTR_NS]
            d['localName'] = item[_ATTR_LOCALNAME]
        # ownerElement arg is for readonlyness, not the OwnerElement attribute
        if ownerElement is not None and ownerElement._readonly:
            d['_readonly'] = 1 # XXX must be shared in case of removal?
        d['specified'] = item[_ATTR_SPECIFIED]

    def __getstate__(self):
        raise RuntimeError("Attr nodes cannot be pickled")

    def __cmp__(self, other):
        if (other.nodeType == Node.ATTRIBUTE_NODE
            and self._item is other._item):
            return 0
        else:
            return cmp(id(_aq_base(self)), id(_aq_base(other)))

    def __repr__(self):
        return "<Attr '%s' at 0x%x; identity=0x%x>" % (
            self.name, id(_aq_base(self)), id(self._item))

    def _cloneNode(self, deep, mutable, document):
        # self is *not* an acquisition wrapper!
        clone = self.__class__.__basicnew__()
        d = clone.__dict__
        d.update(self.__dict__)
        d['_item'] = item = list(self._item)
        item[_ATTR_SPECIFIED] = 1
        d['specified'] = 1
        if d.has_key('_readonly'):
            del d['_readonly']
        # clone the children
        d['_children'] = L = []
        for child in self._children:
            newChild = child._cloneNode(1, mutable, document)
            if newChild.__dict__.has_key('_in_tree'):
                del newChild.__dict__['_in_tree']
            L.append(newChild)
        return clone

    #nodeName, name, prefix must be shared between attr nodes and
    #element storage, because we can change the prefix with either interface.

    _get_name = Node._get_nodeName

    def _get_nodeName(self):
        return self._item[_ATTR_NAME]        
    nodeName = ComputedAttribute(_get_nodeName, 1)

    def _get_name(self):
        return self._item[_ATTR_NAME]        
    name = ComputedAttribute(_get_name, 1)

    def _get_prefix(self):
        return self._item[_ATTR_PREFIX]
    prefix = ComputedAttribute(_get_prefix, 1)

    # we aren't checking to see if this attr was created with a lvl2 method;
    # if it wasn't, setting the prefix will make the name funny -
    # but that's undefined behavior anyway.
    def _set_prefix(self, value):
        self._check_prefix(value)
        d = self.__dict__
        self._item[_ATTR_PREFIX] = value
        if value:
            name =  "%s:%s" % (value, self._item[_ATTR_LOCALNAME])
        else:
            name = self._item[_ATTR_LOCALNAME]
        self._item[_ATTR_NAME] = name
        if not self.specified:
            self.__dict__['specified'] = 1
            self._item[_ATTR_SPECIFIED] = 1
            self._changed()

    def _set_owner_element(self, owner):
        # set ownerElement with acquisition XXX same aq bug as parent usage
        _reparent(self, owner) 
        if owner is not None:
            self.__dict__['ownerDocument'] = owner.ownerDocument

    def _set_owner_document(self, doc):
        self.__dict__['ownerDocument'] = doc

    def _get_ownerDocument(self):
        return self.ownerDocument

    def _get_ownerElement(self):
        # Acquire the owner.
        parent = _parent_of(self)
        if parent and parent.isSameNode(self.ownerDocument):
            return None                 # we use this for unowned attrs
        return parent
    ownerElement = ComputedAttribute(_get_ownerElement, 1)

    def _get_value(self):
        return _attr_get_value(self._children)
    value = ComputedAttribute(_get_value)

    _get_nodeValue = _get_value
    nodeValue = value

    def _set_value(self, data):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        _attr_set_value(self._item, data)        

    _set_nodeValue = _set_value

    childNodes = ComputedAttribute(Node._get_childNodes)

    # DOM Level 3 (Working Draft, 01 Sep 2000)

    def _get_specified(self):
        return self.specified

    def _get_textContent(self):
        return self._item[ATTR_VALUE]
    textContent = ComputedAttribute(_get_textContent)

    def isSameNode(self, other):
        return (other is not None
                and other.nodeType == Node.ATTRIBUTE_NODE
                and self._item is other._item)


class MapFromParent(AttributeControl):
    """
    Baseclass for a NamedNodeMap that works by extracting information
    from a parent.
    Must be subclassed to determine what we're looking for and returning.
    """

    def __init__(self, parent):
        self.__dict__['_parent'] = parent
        # subclass must set _parentListName

    def _getParentList(self):
        "return the parent's list used to make this map"
        return getattr(self._parent, self._parentListName)

    def __getstate__(self):
        raise RuntimeError, "NamedNodeMap type instances cannot be stored"

    def _get_length(self):
        return len(self._getParentList())
    __len__ = _get_length

    def __getattr__(self, name):
        if name == "length":
            return self._get_length()
        raise AttributeError, name

    def __setattr__(self, name, value):
        if name == "length":
            raise xml.dom.NoModificationAllowedErr()
        AttributeControl.__setattr__(self, name, value)

    def get(self, name, default=None):
        node = self.getNamedItem(name)
        if node is None:
            return default
        else:
            return node

    def item(self, i):
        try:
            itemSource = self._getParentList()[i]
        except IndexError:
            return
        else:
            return self._item_helper(itemSource)

    # subclass must define _item_helper

    def getNamedItem(self, name):
        for item in self._getParentList():
            if self._nameMatcher(item, name):
                return self._item_helper(item)

    def getNamedItemNS(self, namespaceURI, localName):
        for item in self._getParentList():
            if self._nsMatcher(item, (namespaceURI, localName)):
                return self._item_helper(item)

    def __getitem__(self, name):
        node = self.getNamedItem(name)
        if node is None:
            raise KeyError, name
        return node

    # subclass must define _set_named_item, _nameMatcher, nsMatcher

    def setNamedItem(self, node):
        return self._set_named_item(node.nodeName, self._nameMatcher, node)

    def setNamedItemNS(self, node):
        nameinfo = (node.namespaceURI, node.localName)
        return self._set_named_item(nameinfo, self._nsMatcher, node)

    def __setitem__(self, name, node):
        if self._parent._readonly or self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        assert name == node.nodeName
        self.setNamedItem(node)

    # subclass must define _key_helper, _delFromParentList

    def removeNamedItem(self, name):
        return self._remove_named_item(name, self._nameMatcher)

    def removeNamedItemNS(self, namespaceURI, localName):
        return self._remove_named_item((namespaceURI, localName),
                                       self._nsMatcher)

    def _remove_named_item(self, name, matcher):
        #
        # The workhorse of item removal; this removes whatever
        # item the 'matcher' test determines matches.  'name' is
        # passed to the matcher but is not used otherwise.
        #
        if self._parent._readonly or self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        pList = self._getParentList()
        for i in range(len(pList)):
            item = pList[i]
            if matcher(item, name):
                break
        else:
            raise xml.dom.NotFoundErr()
        self._delFromParentList(pList, i)        
        node = self._item_helper(item)
        node._set_owner_element(None)
        return node

    def __delitem__(self, name):
        if self._parent._readonly or self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        pList = self._getParentList()
        for i in range(len(pList)):
            item = pList[i]
            s = self._key_helper(item)
            if s == name:
                self._delFromParentList(pList, i)
                return
        raise KeyError, name

    def has_key(self, name):
        for item in self._getParentList():
            if self._key_helper(item) == name:
                return 1
        return 0

    def items(self):
        L = []
        for item in self._getParentList():
            L.append((self._key_helper(item), self._item_helper(item)))
        return L

    def keys(self):
        L = []
        for item in self._getParentList():
            L.append(self._key_helper(item))
        return L

    def values(self):
        L = []
        for item in self._getParentList():
            L.append(self._item_helper(item))
        return L



class AttributeMap(MapFromParent):
    """NamedNodeMap that works on the attribute structure.

    This doesn't do anything about the namespace declarations.
    """

    _parentListName = '_attributes'

    def __init__(self, parent):
        d = self.__dict__
        d['_attr_info'] = parent._attr_info
        d['_parent'] = parent
        d['_nameMatcher'] = _attr_item_match_name
        d['_nsMatcher'] = _attr_item_match_ns

    def _get_length(self):
        d = {}
        for item in self._parent._attributes:
            if item[_ATTR_NS]:
                key = item[_ATTR_NS], item[_ATTR_LOCALNAME]
            else:
                key = item[_ATTR_NAME]
            d[key] = 1
        for item in self._attr_info:
            if item[_ATTR_NS]:
                key = item[_ATTR_NS], item[_ATTR_LOCALNAME]
            else:
                key = item[_ATTR_NAME]
            d[key] = 1
        return len(d)
    __len__ = _get_length

    def item(self, i):
        node = MapFromParent.item(self, i)
        if node is None and self._attr_info:
            d = {}
            for item in self._parent._attributes:
                if item[_ATTR_NS]:
                    key = item[_ATTR_NS], item[_ATTR_LOCALNAME]
                else:
                    key = item[_ATTR_NAME]
                d[key] = 1
            j = len(d)
            for item in self._attr_info:
                name = item[_ATTR_NAME]
                if d.has_key(name):
                    pass
                else:
                    if j == i:
                        item = list(item)
                        if self._parent._attributes:
                            self._parent._attributes.append(item)
                        else:
                            self._parent.__dict__['_attributes'] = [item]
                        node = Attr(
                            item, self._parent.ownerDocument, self._parent)
                        node = node.__of__(self._parent)
                        break
                    j = j + 1
        return node

    def _item_helper(self, itemSource):
        "used by item; create an Attribute from the item and return it"
        node = Attr(itemSource, self._parent.ownerDocument, self._parent)
        return node.__of__(self._parent)

    def _set_named_item(self, nameinfo, matcher, node):
        "utility function for setNamedItem"
        if self._parent._readonly or self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        if node.nodeType != Node.ATTRIBUTE_NODE:
            raise xml.dom.HierarchyRequestErr()
        if not self._parent.ownerDocument.isSameNode(node.ownerDocument):
            raise xml.dom.WrongDocumentErr()
        if node.ownerElement:
            if node.ownerElement.isSameNode(self._parent):
                # This is already our node; no extra work needed, and no
                # change to the storage object.
                return node
            raise xml.dom.InuseAttributeErr()
        attributes = self._getParentList()
        if not attributes:
            self._parent.__dict__['_attributes'] = [node._item]
            node._set_owner_element(self._parent)
            return node
        oldNode = None
        for i in range(len(attributes)):
            item = attributes[i]
            if matcher(item, nameinfo):
                oldNode = item
                attributes[i] = node._item
                break
        if oldNode is None:
            self._addToParentList(attributes, node)
            node._set_owner_element(self._parent) 
        return oldNode

    def _delFromParentList(self, attrs, i):
        "workhorse for __delitem__; remove ith item from attrs"
        del attrs[i] #XXX ownerElement needs to be updated in other refs
        self._parent._changed()

    def _addToParentList(self, attrs, node):
        if self._parent._attributes:
            self._parent._attributes.append(node._item)
        else:
            self._parent.__dict__['_attributes'] = [node._item]
        self._parent._changed()

    def _key_helper(self, itemSource):
        "given an item source, return an appropriate key for our mapping"
        return itemSource[_ATTR_NAME]


# Utility functions for Attrs, used by more than the Attr class.

def _attr_item_match_name(item, name,
                          _ATTR_NAME=_ATTR_NAME):
    "utility function for AttributeMap; return true if name matches item"
    return item[_ATTR_NAME] == name

def _attr_item_match_ns(item, (namespaceURI, localName),
                        _ATTR_NS=_ATTR_NS, _ATTR_LOCALNAME=_ATTR_LOCALNAME):
    "utility function for AttributeMap; return true if name matches item"    
    return (item[_ATTR_LOCALNAME] == localName
            and item[_ATTR_NS] == namespaceURI)

def _attr_get_value(nodes):
    "utility function to get attr value; concatenate values of list of nodes"
    L = []
    for node in nodes:
        L.append(node.nodeValue)
    return _string.join(filter(None, L), '')

def _attr_set_value(item, value):
    "utility function to safely set shared value of attr item"
    newChild = Text(value)
    del newChild.__dict__['_in_tree']
    while item[_ATTR_VALUE]:
        item[_ATTR_VALUE].pop()
    item[_ATTR_VALUE].append(newChild)


# no longer needed
del ComputedAttribute

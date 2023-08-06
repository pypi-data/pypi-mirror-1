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

"""Facility to use the Expat parser to load a ParsedXML.DOM instance
from a string or file."""

# Warning!
#
# This module is tightly bound to the implementation details of the
# Parsed XML DOM and can't be used with other DOM implementations.  This
# is due, in part, to a lack of appropriate methods in the DOM (there is
# no way to create Entity and Notation nodes via the DOM Level 2
# interface), and for performance.  The later is the cause of some fairly
# cryptic code.
#
# Performance hacks:
#
#   -  .character_data_handler() has an extra case in which continuing
#      data is appended to an existing Text node; this can be a
#      substantial speedup since Expat seems to break data at every
#      newline.
#
#   -  Determining that a node exists is done using an identity comparison
#      with None rather than a truth test; this avoids searching for and
#      calling any methods on the node object if it exists.  (A rather
#      nice speedup is achieved this way as well!)

import string

import Core
import XMLExtended

from xml.parsers import expat


class Options:
    """Features object that has variables set for each DOMBuilder feature.

    The DOMBuilder class uses an instance of this class to pass settings to
    the ExpatBuilder class.
    """

    # Note that the DOMBuilder class in LoadSave constrains which of these
    # values can be set using the DOM Level 3 LoadSave feature.

    namespaces = 1
    namespace_declarations = 1
    validation = 0
    external_general_entities = 1
    external_parameter_entities = 1
    validate_if_cm = 0
    create_entity_ref_nodes = 1
    entity_nodes = 1
    white_space_in_element_content = 1
    cdata_nodes = 1
    comments = 1
    charset_overrides_xml_encoding = 1

    errorHandler = None
    filter = None


class ExpatBuilder:
    """Document builder that uses Expat to build a ParsedXML.DOM document
    instance."""

    def __init__(self, options=None):
        if options is None:
            options = Options()
        self._options = options
        self._parser = None
        self.reset()

    try:
        {}.setdefault
    except AttributeError:
        def _intern(self, s):
            try:
                return self._interns[s]
            except KeyError:
                self._interns[s] = s
                return s
    else:
        def _intern(self, s):
            return self._interns.setdefault(s, s)

    def createParser(self):
        """Create a new parser object."""
        return expat.ParserCreate()

    def getParser(self):
        """Return the parser object, creating a new one if needed."""
        if not self._parser:
            self._parser = self.createParser()
            self.install(self._parser)
        return self._parser

    def reset(self):
        """Free all data structures used during DOM construction."""
        self.document = None
        self._cdata = 0
        self._standalone = -1
        self._version = None
        self._encoding = None
        self._doctype_args = None
        self._entities = []
        self._notations = []
        self._pre_doc_events = []
        self._attr_info = {}
        self._elem_info = {}
        self._interns = {}

    def install(self, parser):
        """Install the callbacks needed to build the DOM into the parser."""
        # This creates circular references!
        parser.StartDoctypeDeclHandler = self.start_doctype_decl_handler
        parser.StartElementHandler = self.start_element_handler
        parser.EndElementHandler = self.end_element_handler
        parser.ProcessingInstructionHandler = self.pi_handler
        parser.CharacterDataHandler = self.character_data_handler
        parser.EntityDeclHandler = self.entity_decl_handler
        parser.NotationDeclHandler = self.notation_decl_handler
        parser.CommentHandler = self.comment_handler
        parser.StartCdataSectionHandler = self.start_cdata_section_handler
        parser.EndCdataSectionHandler = self.end_cdata_section_handler
        parser.ExternalEntityRefHandler = self.external_entity_ref_handler
        parser.ordered_attributes = 1
        parser.specified_attributes = 1
        parser.XmlDeclHandler = self.xml_decl_handler
        parser.ElementDeclHandler = self.element_decl_handler
        parser.AttlistDeclHandler = self.attlist_decl_handler

    def parseFile(self, file):
        """Parse a document from a file object, returning the document
        node."""
        parser = self.getParser()
        first_buffer = 1
        strip_newline = 0
        while 1:
            buffer = file.read(16*1024)
            if not buffer:
                break
            if strip_newline:
                if buffer[0] == "\n":
                    buffer = buffer[1:]
                strip_newline = 0
            if buffer and buffer[-1] == "\r":
                strip_newline = 1
            buffer = _normalize_lines(buffer)
            parser.Parse(buffer, 0)
            if first_buffer and self.document:
                if self.document.doctype:
                    self._setup_subset(buffer)
                first_buffer = 0
        parser.Parse("", 1)
        doc = self.document
        self.reset()
        self._parser = None
        return doc

    def parseString(self, string):
        """Parse a document from a string, returning the document node."""
        string = _normalize_lines(string)
        parser = self.getParser()
        parser.Parse(string, 1)
        self._setup_subset(string)
        doc = self.document
        self.reset()
        self._parser = None
        return doc

    def _setup_subset(self, buffer):
        """Load the internal subset if there might be one."""
        if self.document.doctype:
            extractor = InternalSubsetExtractor()
            extractor.parseString(buffer)
            subset = extractor.getSubset()
            if subset is not None:
                d = self.document.doctype.__dict__
                d['internalSubset'] = subset

    def start_doctype_decl_handler(self, doctypeName, systemId, publicId,
                                   has_internal_subset):
        self._pre_doc_events.append(("doctype",))
        self._doctype_args = (self._intern(doctypeName), publicId, systemId)

    def pi_handler(self, target, data):
        target = self._intern(target)
        if self.document is None:
            self._pre_doc_events.append(("pi", target, data))
        else:
            node = self.document.createProcessingInstruction(target, data)
            self.curNode.appendChild(node)

    def character_data_handler(self, data):
        if self._cdata:
            if (self._cdata_continue
                and (self.curNode._children[-1].nodeType
                     == Core.Node.CDATA_SECTION_NODE)):
                d = self.curNode._children[-1].__dict__
                data = d['data'] + data
                d['data'] = d['nodeValue'] = data
                return
            node = self.document.createCDATASection(data)
            self._cdata_continue = 1
        elif (self.curNode._children
              and self.curNode._children[-1].nodeType == Core.Node.TEXT_NODE):
            node = self.curNode._children[-1]
            data = node.data + data
            d = node.__dict__
            d['data'] = d['nodeValue'] = data
            return
        else:
            node = self.document.createTextNode(data)
        self.curNode.appendChild(node)

    def entity_decl_handler(self, entityName, is_parameter_entity, value,
                            base, systemId, publicId, notationName):
        if is_parameter_entity:
            # we don't care about parameter entities for the DOM
            return
        if not self._options.entity_nodes:
            return
        entityName = self._intern(entityName)
        notationName = self._intern(notationName)
        node = XMLExtended.Entity(entityName, publicId, systemId, notationName)
        if value is not None:
            # internal entity
            child = Core.Text(value)
            # must still get to parent, even if entity isn't _in_tree
            child.__dict__['_in_tree'] = 1
            child.__dict__['_readonly'] = 1
            node.__dict__['_children'] = [child]
        self._entities.append(node)

    def notation_decl_handler(self, notationName, base, systemId, publicId):
        notationName = self._intern(notationName)
        node = XMLExtended.Notation(notationName, publicId, systemId)
        self._notations.append(node)

    def comment_handler(self, data):
        if self._options.comments:
            if self.document is None:
                self._pre_doc_events.append(("comment", data))
            else:
                node = self.document.createComment(data)
                self.curNode.appendChild(node)

    def start_cdata_section_handler(self):
        if self._options.cdata_nodes:
            self._cdata = 1
            self._cdata_continue = 0

    def end_cdata_section_handler(self):
        self._cdata = 0
        self._cdata_continue = 0

    def external_entity_ref_handler(self, context, base, systemId, publicId):
        return 1

    def start_element_handler(self, name, attributes):
        name = self._intern(name)
        if self.document is None:
            doctype = self._create_doctype()
            doc = Core.theDOMImplementation.createDocument(
                None, name, doctype)
            if self._standalone >= 0:
                doc.standalone = self._standalone
            doc.encoding = self._encoding
            doc.version = self._version
            doc.__dict__['_elem_info'] = self._elem_info
            doc.__dict__['_attr_info'] = self._attr_info
            self.document = doc
            self._include_early_events()
            node = doc.documentElement
            # chicken & egg: if this isn't inserted here, the document
            # element doesn't get the information about the defined
            # attributes for its element type
            if self._attr_info.has_key(name):
                node.__dict__['_attr_info'] = self._attr_info[name]
        else:
            node = self.document.createElement(name)
            self.curNode.appendChild(node)
        self.curNode = node

        if attributes:
            L = []
            for i in range(0, len(attributes), 2):
                L.append([None, self._intern(attributes[i]),
                          None, None, attributes[i+1], 1])
            node.__dict__['_attributes'] = L

    def end_element_handler(self, name):
        curNode = self.curNode
        assert curNode.tagName == name, "element stack messed up!"
        self.curNode = self.curNode.parentNode
        self._handle_white_text_nodes(curNode)
        if self._options.filter:
            self._options.filter.endElement(curNode)

    def _handle_white_text_nodes(self, node):
        info = self._elem_info.get(node.tagName)
        if not info:
            return
        type = info[0]
        if type in (expat.model.XML_CTYPE_ANY,
                    expat.model.XML_CTYPE_MIXED):
            return
        #
        # We have element type information; look for text nodes which
        # contain only whitespace.
        #
        L = []
        for child in node.childNodes:
            if (  child.nodeType == Core.Node.TEXT_NODE
                  and not string.strip(child.data)):
                L.append(child)
        #
        # Depending on the options, either mark the nodes as ignorable
        # whitespace or remove them from the tree.
        #
        for child in L:
            if self._options.white_space_in_element_content:
                child.__dict__['isWhitespaceInElementContent'] = 1
            else:
                node.removeChild(child)

    def element_decl_handler(self, name, model):
        self._elem_info[self._intern(name)] = model

    def attlist_decl_handler(self, elem, name, type, default, required):
        elem = self._intern(elem)
        name = self._intern(name)
        type = self._intern(type)
        if self._attr_info.has_key(elem):
            L = self._attr_info[elem]
        else:
            L = []
            self._attr_info[elem] = L
        L.append([None, name, None, None, default, 0, type, required])

    def xml_decl_handler(self, version, encoding, standalone):
        self._version = version
        self._encoding = encoding
        self._standalone = standalone

    def _create_doctype(self):
        if not self._doctype_args:
            return
        doctype = apply(Core.theDOMImplementation.createDocumentType,
                        self._doctype_args)
        doctype._entities[:] = self._entities
        self._entities = doctype._entities
        doctype._notations[:] = self._notations
        self._notations = doctype._notations
        return doctype

    def _include_early_events(self):
        doc = self.document
        if self._doctype_args:
            docelem = doc.doctype
        else:
            docelem = doc.documentElement
        for event in self._pre_doc_events:
            t = event[0]
            if t == "comment":
                node = doc.createComment(event[1])
            elif t == "doctype":
                # marker; switch to before docelem
                docelem = doc.documentElement
                continue
            elif t == "pi":
                node = doc.createProcessingInstruction(event[1], event[2])
            else:
                raise RuntimeError, "unexpected early event type: " + `t`
            doc.insertBefore(node, docelem)


def _normalize_lines(s):
    """Return a copy of 's' with line-endings normalized according to
    XML 1.0 section 2.11."""
    s = string.replace(s, "\r\n", "\n")
    return string.replace(s, "\r", "\n")


# framework document used by the fragment builder.
# Takes a string for the doctype, subset string, and namespace attrs string.

_FRAGMENT_BUILDER_INTERNAL_SYSTEM_ID = \
    "http://xml.zope.org/entities/fragment-builder/internal"

_FRAGMENT_BUILDER_TEMPLATE = (
    '''\
<!DOCTYPE wrapper
  %%s [
  <!ENTITY fragment-builder-internal
    SYSTEM "%s">
%%s
]>
<wrapper %%s
>&fragment-builder-internal;</wrapper>'''
    % _FRAGMENT_BUILDER_INTERNAL_SYSTEM_ID)


class FragmentBuilder(ExpatBuilder):
    """Builder which constructs document fragments given XML source
    text and a context node.

    The context node is expected to provide information about the
    namespace declarations which are in scope at the start of the
    fragment.
    """

    def __init__(self, context, options=None):
        if context.nodeType == Core.Node.DOCUMENT_NODE:
            self.originalDocument = context
            self.context = context
        else:
            self.originalDocument = context.ownerDocument
            self.context = context
        ExpatBuilder.__init__(self, options)

    def reset(self):
        ExpatBuilder.reset(self)
        self.fragment = None

    def parseFile(self, file):
        """Parse a document fragment from a file object, returning the
        fragment node."""
        return self.parseString(file.read())

    def parseString(self, string):
        """Parse a document fragment from a string, returning the
        fragment node."""
        self._source = string
        parser = self.getParser()
        doctype = self.originalDocument.doctype
        ident = ""
        if doctype:
            subset = doctype.internalSubset or self._getDeclarations()
            if doctype.publicId:
                ident = ('PUBLIC "%s" "%s"'
                         % (doctype.publicId, doctype.systemId))
            elif doctype.systemId:
                ident = 'SYSTEM "%s"' % doctype.systemId
        else:
            subset = ""
        nsattrs = self._getNSattrs() # get ns decls from node's ancestors
        document = _FRAGMENT_BUILDER_TEMPLATE % (ident, subset, nsattrs)
        try:
            parser.Parse(document, 1)
        except:
            self.reset()
            raise
        fragment = self.fragment
        self.reset()
##         self._parser = None
        return fragment

    def _getDeclarations(self):
        """Re-create the internal subset from the DocumentType node.

        This is only needed if we don't already have the
        internalSubset as a string.
        """
        doctype = self.originalDocument.doctype
        s = ""
        if doctype:
            for i in range(doctype.notations.length):
                notation = doctype.notations.item(i)
                if s:
                    s = s + "\n  "
                s = "%s<!NOTATION %s" % (s, notation.nodeName)
                if notation.publicId:
                    s = '%s PUBLIC "%s"\n             "%s">' \
                        % (s, notation.publicId, notation.systemId)
                else:
                    s = '%s SYSTEM "%s">' % (s, notation.systemId)
            for i in range(doctype.entities.length):
                entity = doctype.entities.item(i)
                if s:
                    s = s + "\n  "
                s = "%s<!ENTITY %s" % (s, entity.nodeName)
                if entity.publicId:
                    s = '%s PUBLIC "%s"\n             "%s"' \
                        % (s, entity.publicId, entity.systemId)
                elif entity.systemId:
                    s = '%s SYSTEM "%s"' % (s, entity.systemId)
                else:
                    s = '%s "%s"' % (s, entity.firstChild.data)
                if entity.notationName:
                    s = "%s NOTATION %s" % (s, entity.notationName)
                s = s + ">"
        return s

    def _getNSattrs(self):
        return ""

    def external_entity_ref_handler(self, context, base, systemId, publicId):
        if systemId == _FRAGMENT_BUILDER_INTERNAL_SYSTEM_ID:
            # this entref is the one that we made to put the subtree
            # in; all of our given input is parsed in here.
            old_document = self.document
            old_cur_node = self.curNode
            self._save_namespace_decls()
            parser = self._parser.ExternalEntityParserCreate(context)
            self._restore_namespace_decls()
            # put the real document back, parse into the fragment to return
            self.document = self.originalDocument
            self.fragment = self.document.createDocumentFragment()
            self.curNode = self.fragment
            try:
                parser.Parse(self._source, 1)
            finally:
                self.curNode = old_cur_node
                self.document = old_document
                self._source = None
            return -1
        else:
            return ExpatBuilder.external_entity_ref_handler(
                self, context, base, systemId, publicId)

    def _save_namespace_decls(self):
        pass

    def _restore_namespace_decls(self):
        pass


class Namespaces:
    """Mix-in class for builders; adds support for namespaces."""

    def _initNamespaces(self):
        #
        # These first two dictionaries are used to track internal
        # namespace state, and contain all "current" declarations.
        #
        # URI -> [prefix, prefix, prefix...]
        #
        # The last prefix in list is most recently declared; there's
        # no way to be sure we're using the right one if more than one
        # has been defined for a particular URI.
        self._nsmap = {
            Core.XML_NS: ["xml"],
            Core.XMLNS_NS: ["xmlns"],
            }
        # prefix -> URI
        self._prefixmap = {
            "xml": [Core.XML_NS],
            "xmlns": [Core.XMLNS_NS],
            }
        #
        # These dictionaries are used to store the namespace
        # declaractions made on a single element; they are used to add
        # the attributes of the same name to the DOM structure.  When
        # added to the DOM, they are replaced with new, empty
        # dictionaries on the Builder object.
        #
        self._ns_prefix_uri = {}
        self._ns_uri_prefixes = {}
        # list of (prefix, uri) ns declarations.  Namespace attrs are
        # constructed from this and added to the element's attrs.
        self._ns_ordered_prefixes = []

    def createParser(self):
        """Create a new namespace-handling parser."""
        return expat.ParserCreate(namespace_separator=" ")

    def install(self, parser):
        """Insert the namespace-handlers onto the parser."""
        ExpatBuilder.install(self, parser)
        parser.StartNamespaceDeclHandler = self.start_namespace_decl_handler
        parser.EndNamespaceDeclHandler = self.end_namespace_decl_handler

    def start_namespace_decl_handler(self, prefix, uri):
        "push this namespace declaration on our storage"
        #
        # These are what we use internally:
        #
        prefix = self._intern(prefix)
        uri = self._intern(uri)
        L = self._nsmap.get(uri)
        if L is None:
            self._nsmap[uri] = L = []
        L.append(prefix)
        L = self._prefixmap.get(prefix)
        if L is None:
            self._prefixmap[prefix] = L = []
        L.append(uri)
        #
        # These are used to provide namespace declaration info to the DOM:
        #
        self._ns_prefix_uri[prefix] = uri
        L = self._ns_uri_prefixes.get(uri)
        if not L:
            self._ns_uri_prefixes[uri] = L = []
        L.append(prefix)
        self._ns_ordered_prefixes.append((prefix, uri))

    def end_namespace_decl_handler(self, prefix):
        "pop the latest namespace declaration."
        uri = self._prefixmap[prefix].pop()
        self._nsmap[uri].pop()

    def _save_namespace_decls(self):
        """Save the stored namespace decls and reset the new ones.
        This lets us launch another parser and have its namespace declarations
        not affect future elements.  Must be called outside of any start/end
        namespace_decl_handler calls."""
        self._oldnsmap = self._nsmap
        self._oldprefixmap = self._prefixmap
        self._oldns_prefix_uri = self._ns_prefix_uri
        self._oldns_uri_prefixes = self._ns_uri_prefixes
        self._oldns_ordered_prefixes = self._ns_ordered_prefixes
        self._initNamespaces()

    def _restore_namespace_decls(self):
        "Restore the namespace decls from _save_namespace_decls."
        self._nsmap = self._oldnsmap
        self._prefixmap = self._oldprefixmap
        self._ns_prefix_uri = self._oldns_prefix_uri
        self._ns_uri_prefixes = self._oldns_uri_prefixes
        self._ns_ordered_prefixes = self._oldns_ordered_prefixes

    def start_element_handler(self, name, attributes):
        if ' ' in name:
            uri, localname = string.split(name, ' ')
            localname = self._intern(localname)
            uri = self._intern(uri)
            prefix = self._intern(self._nsmap[uri][-1])
            if prefix:
                qname = "%s:%s" % (prefix, localname)
            else:
                qname = localname
        else:
            uri = None
            qname = name
            localname = prefix = None
        qname = self._intern(qname)
        if self.document is None:
            doctype = self._create_doctype()
            doc = Core.theDOMImplementation.createDocument(
                uri, qname, doctype)
            if self._standalone >= 0:
                doc.standalone = self._standalone
            doc.encoding = self._encoding
            doc.version = self._version
            doc.__dict__['_elem_info'] = self._elem_info
            doc.__dict__['_attr_info'] = self._attr_info
            self.document = doc
            self._include_early_events()
            node = doc.documentElement
            # chicken & egg: if this isn't inserted here, the document
            # element doesn't get the information about the defined
            # attributes for its element type
            if self._attr_info.has_key(qname):
                node.__dict__['_attr_info'] = self._attr_info[qname]
        else:
            node = self.document.createElementNS(
                uri, qname, (prefix, localname))
            self.curNode.appendChild(node)
        self.curNode = node

        L = [] # [[namespaceURI, qualifiedName, localName, prefix,
               #   value, specified]]
        if self._ns_ordered_prefixes and self._options.namespace_declarations:
            for prefix, uri in self._ns_ordered_prefixes:
                if prefix:
                    attrPrefix = "xmlns"
                    tagName = self._intern('%s:%s' % (attrPrefix, prefix))
                else:
                    attrPrefix = tagName = "xmlns"
                L.append([Core.XMLNS_NS, tagName, self._intern(prefix),
                          attrPrefix, uri, 1])
        if attributes:
            # This uses the most-recently declared prefix, not necessarily
            # the right one.
            for i in range(0, len(attributes), 2):
                aname = attributes[i]
                value = attributes[i+1]
                if ' ' in aname:
                    uri, localname = string.split(aname, ' ')
                    localname = self._intern(localname)
                    prefix = self._intern(self._nsmap[uri][-1])
                    uri = self._intern(uri)
                    if prefix:
                        qualifiedname = self._intern(
                            '%s:%s' % (prefix, localname))
                    else:
                        qualifiedname = localname
                    L.append([uri, qualifiedname, localname, prefix, value, 1])
                else:
                    name = self._intern(aname)
                    L.append([None, name, name, None, value, 1])
        if L:
            node.__dict__['_attributes'] = L

        if self._ns_prefix_uri:
            # insert this stuff on the element:
            d = node.__dict__
            d['_ns_prefix_uri'] = self._ns_prefix_uri
            d['_ns_uri_prefixes'] = self._ns_uri_prefixes
            # reset for the next:
            self._ns_prefix_uri = {}
            self._ns_uri_prefixes = {}
            self._ns_ordered_prefixes = []

    def end_element_handler(self, name):
        if ' ' in name:
            uri, localname = string.split(name, ' ')
            assert (self.curNode.namespaceURI == uri
                    and self.curNode.localName == localname), \
                    "element stack messed up! (namespace)"
        else:
            assert self.curNode.nodeName == name, \
                   "element stack messed up - bad nodeName"
            assert self.curNode.namespaceURI is None, \
                   "element stack messed up - bad namespaceURI"
        self._handle_white_text_nodes(self.curNode)
        self.curNode = self.curNode.parentNode


class ExpatBuilderNS(Namespaces, ExpatBuilder):
    """Document builder that supports namespaces."""

    def reset(self):
        ExpatBuilder.reset(self)
        self._initNamespaces()


class FragmentBuilderNS(Namespaces, FragmentBuilder):
    """Fragment builder that supports namespaces."""

    def reset(self):
        FragmentBuilder.reset(self)
        self._initNamespaces()

    def _getNSattrs(self):
        """Return string of namespace attributes from this element and
        ancestors."""
        attrs = ""
        context = self.context
        L = []
        while context:
            if hasattr(context, '_ns_prefix_uri'):
                for prefix, uri in context._ns_prefix_uri.items():
                    # add every new NS decl from context to L and attrs string
                    if prefix in L:
                        continue
                    L.append(prefix)
                    if prefix:
                        declname = "xmlns:" + prefix
                    else:
                        declname = "xmlns"
                    if attrs:
                        attrs = "%s\n    %s='%s'" % (attrs, declname, uri)
                    else:
                        attrs = " %s='%s'" % (declname, uri)
            context = context.parentNode
        return attrs


class ParseEscape(Exception):
    """Exception raised to short-circuit parsing in InternalSubsetExtractor."""
    pass

class InternalSubsetExtractor(ExpatBuilder):
    """XML processor which can rip out the internal document type subset."""

    def getSubset(self):
        """Return the internal subset as a string."""
        subset = self.subset
        while subset and subset[0] != "[":
            del subset[0]
        if subset:
            x = subset.index("]")
            return string.join(subset[1:x], "")
        else:
            return None

    def parseFile(self, file):
        try:
            ExpatBuilder.parseFile(self, file)
        except ParseEscape:
            pass

    def parseString(self, string):
        try:
            ExpatBuilder.parseString(self, string)
        except ParseEscape:
            pass

    def install(self, parser):
        parser.StartDoctypeDeclHandler = self.start_doctype_decl_handler
        parser.EndDoctypeDeclHandler = self.end_doctype_decl_handler
        parser.StartElementHandler = self.start_element_handler

    def start_doctype_decl_handler(self, *args):
        self.subset = []
        self.getParser().DefaultHandler = self.default_handler

    def end_doctype_decl_handler(self):
        self.getParser().DefaultHandler = None
        raise ParseEscape()

    def start_element_handler(self, name, attrs):
        raise ParseEscape()

    def default_handler(self, s):
        self.subset.append(s)


def parse(file, namespaces=1):
    """Parse a document, returning the resulting Document node.

    'file' may be either a file name or an open file object.
    """
    if namespaces:
        builder = ExpatBuilderNS()
    else:
        builder = ExpatBuilder()

    if isinstance(file, type('')):
        fp = open(file, 'rb')
        result = builder.parseFile(fp)
        fp.close()
    else:
        result = builder.parseFile(file)
    return result


def parseFragment(file, context, namespaces=1):
    """Parse a fragment of a document, given the context from which it was
    originally extracted.  context should be the parent of the node(s) which
    are in the fragment.

    'file' may be either a file name or an open file object.
    """
    if namespaces:
        builder = FragmentBuilderNS(context)
    else:
        builder = FragmentBuilder(context)

    if isinstance(file, type('')):
        fp = open(file, 'rb')
        result = builder.parseFile(fp)
        fp.close()
    else:
        result = builder.parseFile(file)
    return result


def makeBuilder(options):
    """Create a builder based on an Options object."""
    if options.namespaces:
        return ExpatBuilderNS(options)
    else:
        return ExpatBuilder(options)

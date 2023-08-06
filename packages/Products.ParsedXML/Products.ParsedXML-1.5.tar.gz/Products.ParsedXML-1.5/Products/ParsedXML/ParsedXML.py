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
Zope Product creation for Parsed XML.
"""

from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Role import RoleManager
from Persistence import Persistent
from Acquisition import Implicit
from OFS.Cache import Cacheable
import Globals
from Globals import DTMLFile
from ManageableDOM import ManageableDocument, DOMManageable, \
     theDOMImplementation, parserr
from StringIO import StringIO
from xml.parsers import expat
import DOM, ExtraDOM
import helpers
from types import StringType
from NodePath import registry

MARKER = []  # dummy default object for cache return

contentTypes = ['text/html', 'application/html', 'text/xml']
    
class ParsedXML(SimpleItem, ManageableDocument, Cacheable):
    "The Parsed XML top object, and the persistent head of the tree."
     
    meta_type = 'Parsed XML'

    security = ClassSecurityInfo()
    
    manage_options = (DOMManageable.manage_options +
                      RoleManager.manage_options +
                      Cacheable.manage_options)

    security.setPermissionDefault('Edit ParsedXML', ['Manager'])

    security.declareProtected('Edit ParsedXML',
                              'manage_editForm')
    manage_editForm = DTMLFile('dtml/persEdit', globals(),
                               __name__='manage_editForm')

    icon = 'misc_/ParsedXML/pxml.gif'

    def __init__(self, id, XMLstring = None, namespaces = 1,
                 contentType = "text/xml"):
        "Initialize a Parsed XML object"
        self.id = id
        self._persistentDoc = self # used by transient proxies
        self.noNamespaces = not namespaces
        if contentType not in contentTypes:
            import string
            raise RuntimeError, (
                "Bad content type %s; valid types are %s"
                % (str(contentType), string.join(contentTypes)))
        self.contentType = contentType
        self.initFromDOMDocument(createDOMDocument(XMLstring, namespaces))
        if XMLstring:
            self._lenCache = len(XMLstring)
        else:
            self._lenCache = len(str(self))
        self._lenCorrect = 1

    security.declarePrivate('initFromDOMDocument')
    def initFromDOMDocument(self, DOMdoc):
        "Initialize a Parsed XML from a DOM Document"
        # inherit from ManageableDocument
        ParsedXML.inheritedAttribute('__init__')(self, DOMdoc, self)

    def manage_afterAdd(self, object, container):
        """Store the container that we're being added to.  This is used
        to traverse back to the persistent document."""
        self._container = container

    #
    # methods that deal with persistence
    #

    # DOM nodes use __changed__ because its acquirable
    # Setting _p_changed is equivalent.
    def __changed__(self, *args):
        """Override the acquired __changed__ method used by the non-DB
        DOM nodes, update length cache, and mark this object as dirty."""
        if getattr(self, '_v_lenCorrect', None):
            self._lenCorrect = 1
        else:
            self._lenCorrect = 0
        self.ZCacheable_invalidate()            
        self._p_changed = 1

    # wrap DOMIO to provide cacheing
    security.declareProtected('View management screens', 'index_html')
    def index_html(self, REQUEST = None, RESPONSE = None):
        "Returns publishable source according to content type"
        if RESPONSE:
            RESPONSE.setHeader('Content-type', self.contentType)
        data = self.ZCacheable_get(default = MARKER)
        if data is not MARKER:
            return data
        # inherit from DOMIO
        data = ParsedXML.inheritedAttribute('index_html')(self,
                                                          REQUEST, RESPONSE)
        self.ZCacheable_set(data)
        return data

    security.declareProtected('View management screens', 'get_size')
    def get_size(self):
        "Length of the XML string representing this node in characters."
        if not getattr(self, '_lenCorrect', 0):
            self._lenCache = len(str(self))
            self._lenCorrect = 1
        return self._lenCache

    # methods that override ZDOM methods that are incorrect
    #

    security.declareProtected('Access contents information',
                              'getElementsByTagName')
    def getElementsByTagName(self, tagName):
        return self.__getattr__("getElementsByTagName")(tagName)

    security.declareProtected('Access contents information',
                              'hasChildNodes')
    def hasChildNodes(self):
        return self.__getattr__("hasChildNodes")()

    # 
    # methods that override SimpleItem; sigh, multiple inheritance.
    #
    security.declareProtected('Access contents information', 'objectValues')
    def objectValues(self, spec=None):
        """
        Returns a list of actual subobjects of the current object.
        If 'spec' is specified, returns only objects whose meta_type
        match 'spec'.
        """
        return ManageableDocument.objectValues(self, spec)

    security.declareProtected('Access contents information', 'objectIds')
    def objectIds(self, spec=None):
        """
        Returns a list of subobject ids of the current object.
        If 'spec' is specified, returns objects whose meta_type
        matches 'spec'.
        """
        return ManageableDocument.objectIds(self, spec)
    
    security.declareProtected('Access contents information', 'objectItems')
    def objectItems(self, spec=None):
        """
        Returns a list of (id, subobject) tuples of the current object.
        If 'spec' is specified, returns only objects whose meta_type match
        'spec'
        """
        return ManageableDocument.objectItems(self, spec)
    
    security.declareProtected('Access contents information', 'tpValues')   
    def tpValues(self):
        "Return a list of immediate subobjects.  Used by the dtml-tree tag."
        return ManageableDocument.tpValues(self)

    # override ManageableDocument's method; we can't persist new DOM node by
    # hanging off of parents
    security.declareProtected('Edit ParsedXML', 'parseXML')
    def parseXML(self, file):
        "parse file as XML, replace DOM node with resulting tree, return self"
        namespaces = not self.noNamespaces
        node = ExtraDOM.parseFile(self.getDOMObj(), file, namespaces)
        self.initFromDOMDocument(node)
        self.__changed__(1)
        return self

    security.declareProtected('Access contents information',
                              'getDOM')
    def getDOM(self):
        """Get the Document node of the DOM tree.
        """
        return self

    security.declareProtected('Access contents information',
                              'getNodePath')
    def getNodePath(self, scheme_name, node):
        """Create the node path for a particular node in the tree.
        """
        # if we're asking for node of this document itself
        if node is self:
            return 'scheme_name'
        # otherwise ask for nodepath of node
        return node.getNodePath(scheme_name)

    security.declareProtected('Access contents information',
                              'resolveNodePath')
    def resolveNodePath(self, path):
        """Resolve node path from top of the tree to node.
        """
        # start resolving from the document node
        doc = self._persistentDoc._earlyAqChain()
        # FIXME: could use raw DOM instead of management wrappers
        return registry.resolve_path(doc, path)
        
    def __getitem__(self, s):
        """Handle node paths.
        """
        # backwards compatibility -- handle classic 0/1/2 paths
        try:
            return self.childNodes[int(s)].__of__(self)
        except ValueError:
            pass
        
        # start resolving from the document node
        doc = self._persistentDoc._earlyAqChain()
        # FIXME: could use raw DOM instead of management wrappers
        result = registry.resolve_path(doc, s)
        # FIXME: does this convince ZPublisher to show NotFound?
        if result is None:
            raise KeyError, "Could not resolve node path."
        return result

Globals.InitializeClass(ParsedXML)

def createDOMDocument(XMLstring = None, namespaces = 1):
    "Helper function to create a DOM document, without any proxy wrappers."
    if XMLstring:
        XMLstring=StringIO(XMLstring)
        # more efficient to not use ExtraDOM here
        return DOM.ExpatBuilder.parse(XMLstring, namespaces)
    # we use DOM.theDOMImplementation, not ManageableDOMs, for efficiency
    return DOM.theDOMImplementation.createDocument(
        None, "mydocument", None)

def manage_addParsedXML(context, id, title='', file='',
                        useNamespaces=1, contentType="text/xml",
                        REQUEST=None):
    "Add a Parsed XML instance with optional file content."
    
    if not file or not isinstance(file, StringType):
        file ='<?xml version = "1.0"?><emptydocumentElement/>'
    try:
        ob = ParsedXML(id, file, useNamespaces, contentType)
    except expat.error, e:
        if REQUEST is not None:
            err = "%s%s" % (parserr, '<font color="red">%s</font>'
                            % getattr(e, 'args', ''))
            return Globals.MessageDialog(
                title= 'XML Parsing Error',
                message = err,
                action='manage_main')
        raise
    ob.title = str(title)
    context._setObject(id, ob)
    helpers.add_and_edit(context, id, REQUEST, 'manage_editForm')

manage_addParsedXMLForm = DTMLFile('dtml/documentAdd', globals(),
                                   __name__='manage_addParsedXMLForm')

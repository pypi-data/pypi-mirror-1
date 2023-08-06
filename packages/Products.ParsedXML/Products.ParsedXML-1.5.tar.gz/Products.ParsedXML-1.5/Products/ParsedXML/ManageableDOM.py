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
Zope management support for DOM classes.
"""
from AccessControl import ClassSecurityInfo

import Globals
import Acquisition
from Acquisition import aq_parent, aq_base
import App.Management
from OFS.Traversable import Traversable
from DateTime import DateTime # for manage_edit cookie expire
import marshal # for ftp
from Globals import DTMLFile
import DOMProxy
import DOM
import ExtraDOM
import string
from xml.parsers import expat
import xml.dom
import types
from StringIO import StringIO
from NodePath import registry

try:  			# Zope 2.8 style transactions
    import transaction
except ImportError:  	# Old-style transactions
    # BBB: for Zope 2.7
    class TransactionMan:
        def begin(self):                get_transaction().begin()
        def commit(self, sub=False):    get_transaction().commit(sub)
        def abort(self, sub=False):     get_transaction().abort(sub)
        def get(self):                  return get_transaction()
    transaction = TransactionMan()

parserr=('Sorry, an XML parsing error occurred.  Check '
         'your XML document for well-formedness and try '
         'to upload it again after modification.<br><br>')

# 
# Management mixin classes
#
   
class DOMTraversable(Traversable):
    "Mixin class for DOM classes to provide Zope traversability."

    security = ClassSecurityInfo()

    security.declarePublic('getPhysicalPath')
    def getPhysicalPath(self):
        """Returns a path that can be used to access this object again
        later."""
        # first get path to persistent document
        doc = self._persistentDoc._earlyAqChain()
        path = doc.getPhysicalPath()
        # then get path to node and attach it to that path steps
        nodepath = registry.create_path(doc, self, 'child')
        if nodepath:
            return path + (nodepath,)
        else:
            return path
        
    security.declarePublic('getNodePath')
    def getNodePath(self, scheme_name):
        """Create a node path for this node.
        FIXME: this has the same name but other signature as the
        one in ParsedXML for document.
        """
        return registry.create_path(self._persistentDoc._earlyAqChain(),
                                    self, scheme_name)
    
    # sequence interface, for backwards compatibility.
    # normally the document's __getitem__ takes care of this
    def __getitem__(self, key):
        return self.childNodes[int(key)].__of__(self)

    # other helpers
    def _earlyAqChain(self):
        """Return the earliest ref to self in self's aq_chain.  Helper function
        for getPhysicalPath."""
        chain = self.aq_chain
        chain.reverse()
        for parent in chain:
            if parent == self:
                return parent
        return self

Globals.InitializeClass(DOMTraversable)

class DOMPublishable(DOMTraversable):
    "Mixin class for DOM classes to provide Zope publishability."
    # tree tag methods
    
    def tpURL(self):
        """
        Return a string used for an URL relative to parent.  Used by
        the dtml-tree tag.
        """
        i = 0
        node = self.getDOMObj().previousSibling
        while node:
            i = i + 1
            node = node.previousSibling
        return str(i)

    def tpValues(self):
        "Return a list of immediate subobjects.  Used by the dtml-tree tag."
        retList = [] # dtml-tree wants to own this
        for i in self.childNodes:
            retList.append(i)
        return retList

    def tpId(self):
        "Return a value to be used as an id in tree state."
        return self.tpURL()

    # partial ObjectManagerItem interface

    def getId(self):
        "Return the id of the object as a string."
        base = aq_base(self)
        name=getattr(base, 'id', None)
        if name is not None:
            return name
        return self.tpURL()

    # I don't want to add PrincipiaSearchSource, because it'd be expensive
    # to trigger printing every node in a document.  Look into this when
    # we have a better caching plan.        

    # Partial ObjectManager interface.  Nodes are *not* ObjectManagers,
    # these are for other Zope tools to be useful.

    def objectValues(self, spec=None):
        """
        Returns a list of actual subobjects of the current object.
        If 'spec' is specified, returns only objects whose meta_type
        match 'spec'.
        """
        if spec is not None:
            if isinstance(spec, type('s')):
                spec=[spec]
            set=[]
            for ob in self.childNodes:
                if ob['meta_type'] in spec:
                    set.append(ob)
            return set
        return list(self.childNodes)
    
    def objectIds(self, spec=None):
        """
        Returns a list of subobject ids of the current object.
        If 'spec' is specified, returns objects whose meta_type
        matches 'spec'.
        """
        return map(lambda i: i.getId(), self.objectValues(spec))

    def objectItems(self, spec=None):
        """
        Returns a list of (id, subobject) tuples of the current object.
        If 'spec' is specified, returns only objects whose meta_type match
        'spec'
        """
        r=[]
        a=r.append
        for ob in self.objectValues(spec): a((ob.getId(), ob))
        return r

    # FTP interface
    
    def manage_FTPget(self):
        """Returns the source content of an object. For example, the
        source text of a Document, or the data of a file."""
        return self.__str__()        

class DOMIO:
    "Mixin class for DOM classes to provide parsing, writing."
    
    def writeStream(self, stream=None, encoding=None, prettyPrint=0):
        "Write the XML representation of this object to stream."
        # work thru DOM object to avoid making proxy nodes
        return ExtraDOM.writeStream(self.getDOMObj(), stream, encoding,
                                    prettyPrint=prettyPrint)
    
    def __str__(self):
        "Return the XML representation of this object."
        return self.writeStream().getvalue()

    # This is a workaround for newer browser behavior, and will probably
    # break older browsers.  Recent browsers put '<' in the textarea when the
    # source is '&lt;", and when the form is sent they send '<', and so on.
    # This quotes the relevent refs; when the textarea is sent back the
    # browser unquotes them, so the end result is WYSIWYG.  Yuck!
    # If a browser doesn't do this __str__ should be used.
    def textareaStr(self, prettyPrint=0):
        """Return the XML representation of this object in a format safe for
        a textarea, with certain entity references quoted."""
        # FIXME
        # perhaps we should output text in the encoding the document
        # was saved in, but this is too complicated for now, so we just
        # output UTF-8. Unfortunately this is not very pretty in the browser
        # unless you set it to display in UTF-8.
        outStr = self.writeStream(
            encoding=None, prettyPrint=prettyPrint).getvalue().encode('UTF-8')
        outStr = string.replace(outStr, '&amp;', '&amp;amp;')        
        outStr = string.replace(outStr, '&lt;', '&amp;lt;')
        outStr = string.replace(outStr, '&gt;', '&amp;gt;')
        outStr = string.replace(outStr, '<', '&lt;')
        outStr = string.replace(outStr, '>', '&gt;') 
        return outStr

    def index_html(self, REQUEST=None, RESPONSE=None):
        "Returns publishable source according to content type"
        # set content type header for raw XML if necessary
        if RESPONSE:
            if self._persistentDoc:
                contentType = self._persistentDoc.contentType
            else:
                contentType = 'text/xml'
            contentType = contentType + ';charset=utf-8'
            RESPONSE.setHeader('Content-Type', contentType)
        return self.writeStream(None).getvalue()

    # Parsing a node removes self & subtree from document; users of other
    # refs to subnodes have to take care to notice this.
    def parseXML(self, file):
        """Parse file as XML, replace myself with the resulting tree,
        return node replacing self."""
        doc = self._persistentDoc
        namespaces = not (doc and doc.noNamespaces) # default true
        node = ExtraDOM.parseFile(self.getDOMObj(), file, namespaces)
        if self.nodeType == xml.dom.Node.DOCUMENT_NODE:
            errorStr = ("Parsing at the document node must be done on the "
                        "persistent proxy node, which can't be found for some "
                        "reason.\n"
                        "Traverse to the persistent node and try there.")
            raise RuntimeError, errorStr
        else:
            return doc.wrapDOMObj(node) # proxy and node not part of tree


class DOMManageable(DOMIO, DOMPublishable, App.Management.Tabs):
    "Mixin class for DOM classes to provide Zope management interfaces."

    security = ClassSecurityInfo()
    security.setPermissionDefault('View DOM hierarchy', ['Manager'])    
    
    # the UI of ParsedXML is UTF-8
    management_page_charset = 'UTF-8'

    security.declareProtected('View management screens',
                              'manage_editForm')
    manage_editForm = Globals.DTMLFile('dtml/transEdit', globals(),
                                       __name__='manage_editForm')
    security.declareProtected('View DOM hierarchy',
                              'manage_DOMTree')
    manage_DOMTree = Globals.DTMLFile('dtml/DOMTree', globals(),
                                      __name__='manage_DOMTree')
    
    manage_options = (
        {'label':'Edit', 'action':'manage_editForm',
         'help': ('ParsedXML', 'ParsedXML_Edit.stx')},
        {'label':'DOM', 'action':'manage_DOMTree',
         'help': ('ParsedXML', 'ParsedXML_DOM.stx')},
        {'label':'Raw', 'action':'index_html'})
    
    def makeErrorOutput(self, data, offset, lineno):
        """return a HTML-renderable output of data with a text pointer
        to the position at offset, lineno"""
        # make pointer
        pointerLine = ('<font color="red">' +
                       '-' * (offset - 1) + '^' + '\n\n' +
                       '</font>')
        # add rest of data
        # the parser saw a normalized version; normalize data
        data = string.replace(data, "\r\n", "\n")
        data = string.replace(data, "\r", "\n")
        # make reconstruced data rep with break at error
        dataA = ''
        dataB = ''
        # add earlier data
        for line in range(lineno - 1):
            dataA = dataA + data[0:string.index(data, '\n') + 1]
            data = data[string.index(data, '\n') + 1:]
        dataA = dataA + data[0:offset] + '\n\n'
        # add later data
        dataB = dataB + ' ' * (offset)
        dataB = dataB + data[offset:] + '\n'
        # strip brackets, format
        dataA = string.replace(dataA, "<", "&lt;")
        dataA = string.replace(dataA, ">", "&gt;")
        dataB = string.replace(dataB, "<", "&lt;")
        dataB = string.replace(dataB, ">", "&gt;")
        dataOut = ('<div align=left><br><br><pre>' +
                   dataA + pointerLine + dataB +
                   '</pre><br><br></div>')
        return dataOut
    
    # dict to help notice, handle size change request in manage_editForm
    _size_changes={
        'Bigger': (5,5),
        'Smaller': (-5,-5),
        'Narrower': (0,-5),
        'Wider': (0,5),
        'Taller': (5,0),
        'Shorter': (-5,0),
        }

    # helper function to set size cookies and return edit form
    def _er(self, data, title, contentType,
            SUBMIT, dtpref_cols, dtpref_rows, REQUEST):
        dr,dc = self._size_changes[SUBMIT]
        rows=max(1,string.atoi(dtpref_rows)+dr)
        cols=max(40,string.atoi(dtpref_cols)+dc)
        e=(DateTime('GMT') + 365).rfc822()
        resp=REQUEST['RESPONSE']
        resp.setCookie('dtpref_rows',str(rows),path='/',expires=e)
        resp.setCookie('dtpref_cols',str(cols),path='/',expires=e)
        return self.manage_editForm(self, REQUEST,
                                dtpref_cols = cols, dtpref_rows = rows)

    security.declareProtected('Edit ParsedXML', 'manage_edit')
    def manage_edit(self, data, title = '', contentType = None,
                    useNamespaces = 1,
                    SUBMIT = 'Change',
                    dtpref_cols = '50', dtpref_rows = '20', REQUEST = None):
        """
        If SUBMIT is a size pref variable, handle a textarea size change.
        Otherwise parse the given text and handle the result.
        """
        # just get back to the dtml if we're changing size
        if self._size_changes.has_key(SUBMIT):
            return self._er(data, title, contentType,
                            SUBMIT, dtpref_cols, dtpref_rows, REQUEST)
        # if we are pretty printing, just redraw the form
        if SUBMIT == 'PrettyPrint':
            return self.manage_editForm(
                self, REQUEST,
                textareaStr2=self.textareaStr(prettyPrint=1))
                                        
        if (hasattr(self, 'nodeType')
            and self.nodeType == xml.dom.Node.DOCUMENT_NODE):
            #if we're the main doc
            self.title = str(title)
            if contentType:
                self.contentType = str(contentType)
            self.noNamespaces = not useNamespaces        
        
        f = StringIO(data)
        try:
            newNode = self.parseXML(f) # self not in doc if this succeeds
        except expat.error, e:
            transaction.abort()
            if REQUEST:
                dataOut = self.makeErrorOutput(data, e.offset, e.lineno)
                err = "%s%s%s" % (parserr, '<font color="red">%s</font>'
                                % getattr(e, 'args', ''), dataOut)
                return Globals.MessageDialog(
                    title = 'XML Parsing Error',
                    message = err,
                    action = 'manage_editForm')
            raise
        if REQUEST:
            message = "Saved changes."
            # wish I knew why we have to set textareaStr for the form
            return newNode.manage_editForm(self, REQUEST,
                                           textareaStr=newNode.textareaStr(),
                                           management_view="Edit",
                                           manage_tabs_message=message)

    security.declareProtected('Edit ParsedXML', 'manage_upload')
    def manage_upload(self, file, REQUEST=None):
        "Parse the given file and handle the result."
        try:
            newNode = self.parseXML(file)
        except expat.error, e:
            transaction.abort()
            if REQUEST:
                file.seek(0)
                dataOut = self.makeErrorOutput(file.read(),
                                               e.offset, e.lineno)
                err = "%s%s%s" % (parserr, '<font color="red">%s</font>'
                                % getattr(e, 'args', ''), dataOut)
                return Globals.MessageDialog(
                    title  = 'XML Parsing Error',
                    message = err,
                    action = 'manage_editForm')
            raise
        if REQUEST:
            return newNode.manage_editForm(
                self, REQUEST,
                manage_tabs_message='Saved changes.')

Globals.InitializeClass(DOMManageable)

#
# And finally, classes to mix management and DOM proxies.
#

class ManageableWrapper:
    """
    Mixin class to go alongside ManageableNode classes.
    Provides the wrapDOMObj function to create ManageableNode classes.
    """

    # anything that returns subobjs must grant access to them
    __allow_access_to_unprotected_subobjects__ = 1

    def wrapNamedNodeMap(self, obj):
        if obj is None:
            return None
        parent = aq_parent(self) or self
        return ManageableNamedNodeMap(obj, self._persistentDoc).__of__(parent)

    def wrapNodeList(self, obj):
        parent = aq_parent(self) or self
        return ManageableNodeList(obj, self._persistentDoc).__of__(parent)
    
    def wrapDOMObj(self, node):
        """Return the appropriate manageable class wrapped around the node."""
        if node is None:
            return
        wrapper_type = WRAPPER_TYPES[node._get_nodeType()]
        parent = aq_parent(self) or self
        return wrapper_type(node, self._persistentDoc).__of__(parent)
        
# According to DOM Erratum Core-14, the empty string should be
# accepted as equivalent to null for hasFeature().

_MANAGEABLE_DOM_FEATURES = (
    ("org.zope.dom.persistence", None),
    ("org.zope.dom.persistence", ""),
    ("org.zope.dom.persistence", "1.0"),
    ("org.zope.dom.acquisition", None),
    ("org.zope.dom.acquisition", ""),
    ("org.zope.dom.acquisition", "1.0"),
    )

_MANAGEABLE_DOM_NON_FEATURES = (
    ("load", None),
    ("load", ""),
    ("load", "3.0"),
    )

class ManageableDOMImplementation(DOMProxy.DOMImplementationProxy):
    """A proxy of a DOMImplementation node that defines createDocument
    to return a ManageableDocument.
    """
    
    def hasFeature(self, feature, version):
        feature = string.lower(feature)
        if (feature, version) in _MANAGEABLE_DOM_FEATURES:
            return 1
        if (feature, version) in _MANAGEABLE_DOM_NON_FEATURES:
            return 0
        return DOMProxy.DOMImplementationProxy.hasFeature(self, feature,
                                                          version)

    def createDocumentType(self, qualifiedName, publicId, systemId):
        DOMDocumentType = self._createDOMDocumentType(qualifiedName,
                                                      publicId, systemId)
        return ManageableDocumentType(DOMDocumentType)
    
    def createDocument(self, namespaceURI, qualifiedName, docType=None):
        if docType is not None:
            if docType.ownerDocument is not None:
                raise xml.dom.WrongDocumentErr
            mdocType = docType.getDOMObj()
        else:
            mdocType = None
        DOMDocument = self._createDOMDocument(namespaceURI, qualifiedName,
                                              mdocType)
        return ManageableDocument(DOMDocument, DOMDocument)

theDOMImplementation = ManageableDOMImplementation()

# XXX We're implicitly acquiring so we can get ZopeTime (and probably a
# jillion other things) in our DTML methods.  We should be explicit.
class ManageableNode(ManageableWrapper, DOMProxy.NodeProxy, DOMManageable,
                     Acquisition.Implicit):
    "A wrapper around a DOM Node."

    # this is mainly here to make later inheritance safer
    def __init__(self, node, persistentDocument):
        # inherit from DOMProxy.NodeProxy
        ManageableNode.inheritedAttribute('__init__')(self, node,
                                                      persistentDocument)

class ManageableNodeList(ManageableWrapper, DOMProxy.NodeListProxy,
                         Acquisition.Implicit):
    "A wrapper around a DOM NodeList."
    meta_type = "Manageable NodeList"

    # redefine to get back the [] syntax with acquisition, eh?
    def __getslice__(self, i, j):
        return self.wrapNodeList(self._node.__getslice__(i,j))

    # redefine to get back the [] syntax with acquisition, eh?
    def __getitem__(self, i):
        return self.wrapDOMObj(self._node.__getitem__(i))        

class ManageableNamedNodeMap(ManageableWrapper, DOMProxy.NamedNodeMapProxy,
                             Acquisition.Implicit):
    "A wrapper around a DOM NamedNodeMap."
    meta_type = "Manageable NamedNodeMap"

    # redefine to get back the [] syntax with acquisition, eh?
    def __getitem__(self, i):
        return self.wrapDOMObj(self._node.__getitem__(i))        
    
class ManageableDocumentFragment(ManageableWrapper,
                                 DOMProxy.DocumentFragmentProxy,
                                 ManageableNode):
    "A wrapper around a DOM DocumentFragment."
    meta_type = "Manageable Document Fragment"
    
class ManageableElement(ManageableWrapper, DOMProxy.ElementProxy,
                        ManageableNode):
    "A wrapper around a DOM Element."
    meta_type = "Manageable Element"

class ManageableCharacterData(ManageableWrapper,
                              DOMProxy.CharacterDataProxy, ManageableNode):
    "A wrapper around a DOM CharacterData."
    meta_type = "Manageable Character Data"

class ManageableCDATASection(ManageableWrapper,
                             DOMProxy.CDATASectionProxy, ManageableNode):
    "A wrapper around a DOM CDATASection."
    meta_type = "Manageable CDATASection"

class ManageableText(ManageableWrapper,
                     DOMProxy.TextProxy, ManageableCharacterData):
    "A wrapper around a DOM Text."
    meta_type = "Manageable Text"

class ManageableComment(ManageableWrapper,
                        DOMProxy.CommentProxy, ManageableCharacterData):
    "A wrapper around a DOM Comment."
    meta_type = "Manageable Comment"    

class ManageableProcessingInstruction(ManageableWrapper,
                                      DOMProxy.ProcessingInstructionProxy,
                                      ManageableNode):
    "A wrapper around a DOM ProcessingInstruction."
    meta_type = "Manageable Processing Instruction"    

class ManageableAttr(ManageableWrapper, DOMProxy.AttrProxy, ManageableNode):
    "A wrapper around a DOM Attr."
    meta_type = "Manageable Attr"    

#ManageableDocument is not necessarily a persistent object, even when a
#persistent subclass such as ParsedXML has been instantiated.  Traversing
#up to the document can create a new transient proxy.  Persistent attributes
#must be set on the persistent version.
class ManageableDocument(ManageableWrapper, DOMProxy.DocumentProxy,
                         ManageableNode):
    "A wrapper around a DOM Document."
    meta_type = "Manageable Document"    

    implementation = theDOMImplementation

    def __init__(self, node, persistentDocument):
        ManageableNode.__init__(self, node, persistentDocument)

    def _get_implementation(self):
        return self.implementation
    
    #block set of implementation, since we don't proxy it the same
    def __setattr__(self, name, value):
        if name == "implementation":
            raise xml.dom.NoModificationAllowedErr()
        ManageableDocument.inheritedAttribute('__setattr__')(self, name, value)

# DOM extended interfaces

class ManageableEntityReference(ManageableWrapper,
                                DOMProxy.EntityReferenceProxy,
                                ManageableNode):
    "A wrapper around a DOM EntityReference."
    meta_type = "Manageable Entity Reference"

class ManageableEntity(ManageableWrapper, DOMProxy.EntityProxy,
                       ManageableNode):
    "A wrapper around a DOM Entity."
    meta_type = "Manageable Entity"

class ManageableNotation(ManageableWrapper, DOMProxy.NotationProxy,
                         ManageableNode):
    "A wrapper around a DOM Notation."
    meta_type = "Manageable Notation"

class ManageableDocumentType(ManageableWrapper, DOMProxy.DocumentTypeProxy,
                             ManageableNode):
    "A wrapper around a DOM DocumentType."
    meta_type = "Manageable Document Type"    


Node = xml.dom.Node
WRAPPER_TYPES = {
    Node.ELEMENT_NODE: ManageableElement,
    Node.ATTRIBUTE_NODE: ManageableAttr,
    Node.TEXT_NODE: ManageableText,
    Node.CDATA_SECTION_NODE: ManageableCDATASection,
    Node.ENTITY_REFERENCE_NODE: ManageableEntityReference,
    Node.ENTITY_NODE: ManageableEntity,
    Node.PROCESSING_INSTRUCTION_NODE: ManageableProcessingInstruction,
    Node.COMMENT_NODE: ManageableComment,
    Node.DOCUMENT_NODE: ManageableDocument,
    Node.DOCUMENT_TYPE_NODE: ManageableDocumentType,
    Node.DOCUMENT_FRAGMENT_NODE: ManageableDocumentFragment,
    Node.NOTATION_NODE: ManageableNotation,
    }
del Node

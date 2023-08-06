Parsed XML
==========

.. contents::

What is it?
-----------

Parsed XML allows you to use XML objects in the Zope environment.  You
can create XML documents in Zope and leverage Zope to format, query,
and manipulate XML.

Parsed XML consists of a DOM storage, a builder that uses PyExpat to
parse XML into the DOM, and a management proxy product that provides
Zope management features for a DOM tree. It also includes a system to
create paths to nodes in Zope URLs (NodePath).
 

Features
--------

The Parsed XML product parses XML into a Zopish DOM tree.  The
elements of this tree support persistence, acquisition, etc..  The
document and subnodes are editable and manageable through management
proxy objects, and the underlying DOM tree can be directly manipulated
via DTML, Python, etc..

DOM and ManageableDOM
`````````````````````

We're implementing a lean, mean DOM tree for pure DOM access, and a
tree of proxy shells to handle management and take care of the
conveniences like publishing and security.  The ManageableNodes are
the proxy objects.  These are what you see in the management
interface, and the top object that gets put in the ZODB.  Note that
only the top proxy object is persistent, the others are transient.
The Nodes are pure DOM objects.  From a ManageableNode, the DOM Node
is retrieved with the ``getDOMObj()`` call.


DOM API support
```````````````

The DOM tree created by Zope aims to comply with the DOM level 2
standard. This allows you to access your XML in DTML or External
Methods using a standard and powerful API.

We are currently supporting the DOM level 2 Core and Traversal
specifications.

The DOM tree is not built with the XML-SIG's DOM package, because it
requires significantly different node classes.

DOM attributes are made available according to the Python language
mapping for the IDL interfaces described by the DOM recommendation;
see the `mapping <http://cgi.omg.org/cgi-bin/doc?ptc/00-04-08>`_

URL traversal
`````````````

Parsed XML implements a ``NodePath`` system to create references to
XML nodes (most commonly elements).

Currently, traversal uses an element's index within its parent as an
URL key. For example::
  
      http://server/myDoc/0/2/mymethod
    
This URL traverses from an XML Document object with id ``myDoc`` to
it's first sub-element, to that element's second sub-element to an
acquired method with id ``myMethod``.

DOM methods can also be used in URLs, for example::

      http://server/myDoc/firstChild/nextSibling/mymethod
 
Editing XML with the management interface
`````````````````````````````````````````

XML Documents and subnodes are editable via the management
interface. Documents and subtrees can be replaced by uploading XML
files.

Security
````````

Security is handled at the document level.  DOM attributes and methods
are protected by the "Access contents information" permission.
Subnodes will acquire security settings from the document.

Developing with Parsed XML
--------------------------

We like to think that Parsed XML provides a flexible platform for
using a DOM storage and extending that storage to do interesting
things.  See ``README.DOMProxy`` for an explanation of how we're using
this for Parsed XML.

We've included a comprehensive unit test suite to make testing for DOM
compliance easier.  See ``tests/README`` for details.

  If you want to submit changes to Parsed XML, please use the test
  suite to make sure that your changes don't break anything.

Bugs
----

There are bugs in how multiple node references reflect the hierarchy
above the node:

- A reference to a subnode of a DOM document won't reflect some
  hierarchy changes made on other references to the same node.
 
  If two references to a node are created, and one is then
  reparented, the other reference won't reflect the new parent.
  The parentNode attribute will be incorrect, for example, as well
  as the ownerDocument and ownerElement attributes.

- A reference to a subnode of a DOM document can't be properly stored
  as a persistent attribute of a ZODB object; it will lose hierarchy
  information about its parent as well.

Entity reference handling is not complete:

- Entity references do not have child nodes that mirror the child
  nodes of the referenced entity; they do not have child nodes at all.

- TreeWalker.expandEntityReferences has no effect, because of the
  above bug.

Traversal support for visibility and roots is not complete.


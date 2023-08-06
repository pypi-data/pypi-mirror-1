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

"""Replacement DOM exceptions to be used if the xml.dom package is not
available.
"""

"""
Why does this module exist?

    The Python DOM API defines exceptions that DOM implementations
    should use to allow DOM client code to detect errors that can
    occur during processing.  Since not all client code knows about
    the DOM implementation used, all implementations must use shared
    exceptions.  These are defined in the xml.dom package (in the
    package's __init__.py).  The xml.dom package is provided as part
    of PyXML and Python 2.0.

    Since ParsedXML may be used from Python 1.5.2 without having PyXML
    or a more recent version of Python available, we need to provide
    an alternate implementation.  However, DOM client code that works
    on DOM instances created elsewhere will still expect to get the
    exception classes from xml.dom.  Since the code may be part of
    third-party packages that know nothing of ParsedXML or Zope, we
    need to provide an implementation of xml.dom if it doesn't already
    exist.

So how does this module solve the problem?

    This module defines the required exception objects and constants
    and 'installs' the values in the xml.dom module if they are not
    already present.  Since the xml.dom module may not exist, or may
    pre-date the addition of these exceptions to the standard
    implementation (Python 2.0 or PyXML 0.6.2), the modules xml and
    xml.dom are created by surgically adding them to sys.modules if
    needed, and inserting the required values into an existing xml.dom
    module if needed.

    This works because of the way the module import machinery works in
    Python.  sys.modules is a mapping from module name to module
    object; sys.modules['sys'] evaluates to the sys module object.
    When an import statement is executed, the Python runtime first
    looks in sys.modules to retrieve an already-loaded module.  The
    set of built-in modules and the filesystem are only consulted if
    the module has not already been loaded.  For modules in packages
    (xml.dom), each level of enclosing package is checked before
    attempting to load the module; i.e., xml is checked before
    xml.dom.  This machinery is invoked each time an import is
    attempted.

    When ParsedXML.DOM is imported, it imports this module.  This
    first attempts to load the standard xml.dom package.  If that
    fails (which it is likely to do for Python 1.5.2 without PyXML
    installed), this module is an acceptable implementation of
    xml.dom, but we still need the xml package.  This is created
    artificially using the new.module() function and inserted in
    sys.modules.  Once this is done, this module may be inserted for
    the key 'xml.dom', after which attempts to import xml.dom will
    provide this module.

    If xml.dom is already available, but older than the introduction
    of DOMException and its specializations, the implementations
    defined here are inserted into it, so that it is extended to match
    the more recent version of the interface definition.

What are the limitations of this approach?

    Some versions of PyXML may have defined DOMException without
    defining the subclasses.  The specialized versions of DOMException
    were added in PyXML version 0.6.3 (XXX ??).  Versions which
    contain DOMException but not the specializations will not be
    compatible with this module.  This should not be a substantial
    limitation in the context of Zope.

    There is no way to protect against code that imports xml.dom
    before ParsedXML.DOM has been imported.  Such code will receive an
    ImportError.  Reloading that code after ParsedXML.DOM is imported
    will cause it to work properly.

"""

# These have to be in order:
_CODE_NAMES = [
    "INDEX_SIZE_ERR",
    "DOMSTRING_SIZE_ERR",
    "HIERARCHY_REQUEST_ERR",
    "WRONG_DOCUMENT_ERR",
    "INVALID_CHARACTER_ERR",
    "NO_DATA_ALLOWED_ERR",
    "NO_MODIFICATION_ALLOWED_ERR",
    "NOT_FOUND_ERR",
    "NOT_SUPPORTED_ERR",
    "INUSE_ATTRIBUTE_ERR",
    "INVALID_STATE_ERR",
    "SYNTAX_ERR",
    "INVALID_MODIFICATION_ERR",
    "NAMESPACE_ERR",
    "INVALID_ACCESS_ERR",
    ]

for i in range(len(_CODE_NAMES)):
    globals()[_CODE_NAMES[i]] = i + 1
del i


class DOMException(Exception):
    """Base class for exceptions raised by the DOM."""

    def __init__(self, code, *args):
        self.code = code
        self.args = (code,) + args
        Exception.__init__(self, g_errorMessages[code])
        if self.__class__ is DOMException:
            self.__class__ = g_realExceptions[code]

def _derived_init(self, *args):
    """Initializer method that does not expect a code argument,
    for use in derived classes."""
    if not args:
        args = (self, g_errorMessages[self.code])
    else:
        args = (self,) + args
    apply(Exception.__init__, args)

try:
    from xml.dom import DOMException
except ImportError:
    pass

import string
_EXCEPTION_NAMES = ["DOMException"]
template = """\
class %s(DOMException):
    code = %s
    __init__ = _derived_init
"""


g_realExceptions = {}

for s in _CODE_NAMES:
    words = string.split(string.lower(s), "_")
    ename = string.join(map(string.capitalize, words), "")
    exec template % (ename, s)
    g_realExceptions[globals()[s]] = globals()[ename]
    _EXCEPTION_NAMES.append(ename)

del s, words, ename, string, template


try:
    import xml.dom

except ImportError:
    # We have to define everything, which we've done above.
    # This installs it:
    import sys
    try:
        mod = __import__("xml")
    except ImportError:
        import new
        mod = new.module("xml")
        del new
        sys.modules["xml"] = mod
    import Exceptions
    mod.dom = Exceptions
    sys.modules["xml.dom"] = Exceptions
    del mod, sys
    del Exceptions
    from Core import Node

else:
    # The exception classes may not have been defined, so add any
    # that are needed.
    import Exceptions
    for s in _CODE_NAMES + _EXCEPTION_NAMES:
        if not hasattr(xml.dom, s):
            setattr(xml.dom, s, getattr(Exceptions, s))
    if not hasattr(xml.dom, "Node") or type(xml.dom.Node) is type(Exceptions):
        # We need to provide the Node class so the .nodeType constants
        # are in the right place.
        import Core
        xml.dom.Node = Core.Node
        del Core
    del s, Exceptions

del _CODE_NAMES, _EXCEPTION_NAMES


g_errorMessages = {
    INDEX_SIZE_ERR:
    "Index error accessing NodeList or NamedNodeMap",

    DOMSTRING_SIZE_ERR:
    "DOMString exceeds maximum size.",

    HIERARCHY_REQUEST_ERR:
    "Node manipulation results in invalid parent/child relationship.",

    WRONG_DOCUMENT_ERR: "",
    INVALID_CHARACTER_ERR: "",
    NO_DATA_ALLOWED_ERR: "",

    NO_MODIFICATION_ALLOWED_ERR:
    "Attempt to modify a read-only attribute.",

    NOT_FOUND_ERR: "",

    NOT_SUPPORTED_ERR:
    "DOM feature not supported.",

    INUSE_ATTRIBUTE_ERR:
    "Illegal operation on an attribute while in use by an element.",

    INVALID_STATE_ERR: "",
    SYNTAX_ERR: "",
    INVALID_MODIFICATION_ERR: "",

    NAMESPACE_ERR:
    "Namespace operation results in malformed or invalid name or name declaration.",

    INVALID_ACCESS_ERR: "",
    }


# To be sure that unused alternate implementations of the DOM
# exceptions are not used by accessing this module directly, import
# the "right" versions over those defined here.  They may be the same,
# and they may be from an up-to-date PyXML or Python 2.1 or newer.
# This causes alternate implementations to be discarded if not needed.

from xml.dom import *

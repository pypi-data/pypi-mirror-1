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

import os, sys
  
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ParsedXML')

from domapi import DOMImplementationTestSuite

from xml.dom import ext, implementation
from xml.dom.ext.reader import PyExpat

def DOMParseString(self, xml):
    reader = PyExpat.Reader()
    return reader.fromString(xml)

def test_suite():
    """Return a test suite for the Zope testing framework."""
    return DOMImplementationTestSuite(implementation, DOMParseString)

if __name__ == '__main__':
    framework()

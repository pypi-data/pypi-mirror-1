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

from Products.ParsedXML import ParsedXML
from domapi import DOMImplementationTestSuite

def ParsedXMLParseString(self, xml):
    return ParsedXML.ParsedXML('foo', xml)

def test_suite():
    """Return a test suite for the Zope testing framework."""
    return DOMImplementationTestSuite(ParsedXML.theDOMImplementation, 
        ParsedXMLParseString)

if __name__ == '__main__':
    framework()

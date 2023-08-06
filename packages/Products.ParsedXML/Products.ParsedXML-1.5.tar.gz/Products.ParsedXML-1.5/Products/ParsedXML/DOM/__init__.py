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
"""Digital Creation's light-weight, acquisition-based DOM implementation."""

__version__ = '$Revision: 1.5 $'

# Work around the possible lack of a decent XML package; the
# Exceptions module will masquerade as xml.dom if it needs to.
# See the comments in Exceptions for a full explanation.
#
import Exceptions

from Core import theDOMImplementation

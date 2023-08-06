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

"""Implementation of the DOM Level 3 'Load' feature."""

import Core
import ExpatBuilder

import copy
import string
import xml.dom


__all__ = ["DOMBuilder", "DOMEntityResolver", "DOMInputSource"]


class DOMBuilder(Core.AttributeControl):
    entityResolver = None
    errorHandler = None
    filter = None

    def __init__(self):
        self.__dict__['_options'] = ExpatBuilder.Options()

    def _get_entityResolver(self):
        return self.entityResolver
    def _set_entityResolver(self, entityResolver):
        self.__dict__['entityResolver']

    def _get_errorHandler(self):
        return self.errorHandler
    def _set_errorHandler(self, errorHandler):
        self.__dict__['errorHandler'] = errorHandler

    def _get_filter(self):
        return self.filter
    def _set_filter(self, filter):
        self.__dict__['filter'] = filter

    def setFeature(self, name, state):
        if self.supportsFeature(name):
            try:
                settings = self._settings[(_name_xform(name), state)]
            except KeyError:
                raise xml.dom.NotSupportedErr(
                    "unsupported feature: " + `name`)
            else:
                for name, value in settings:
                    setattr(self._options, name, value)
        else:
            raise xml.dom.NotFoundErr("unknown feature: " + `name`)        

    def supportsFeature(self, name):
        return hasattr(self._options, _name_xform(name))

    def canSetFeature(self, name, state):
        key = (_name_xform(name), state and 1 or 0)
        return self._settings.has_key(key)

    _settings = {
        ("namespaces", 0): [("namespaces", 0)],
        ("namespaces", 1): [("namespaces", 1)],
        ("namespace_declarations", 0): [("namespace_declarations", 0)],
        ("namespace_declarations", 1): [("namespace_declarations", 1)],
        ("validation", 0): [("validation", 0)],
        ("external_general_entities", 0): [("external_general_entities", 0)],
        ("external_general_entities", 1): [("external_general_entities", 1)],
        ("external_parameter_entities", 0): [("external_parameter_entities", 0)],
        ("external_parameter_entities", 1): [("external_parameter_entities", 1)],
        ("validate_if_cm", 0): [("validate_if_cm", 0)],
        ("create_entity_ref_nodes", 0): [("create_entity_ref_nodes", 0)],
        ("create_entity_ref_nodes", 1): [("create_entity_ref_nodes", 1)],
        ("entity_nodes", 0): [("create_entity_ref_nodes", 0),
                              ("entity_nodes", 0)],
        ("entity_nodes", 1): [("entity_nodes", 1)],
        ("white_space_in_element_content", 0):
            [("white_space_in_element_content", 0)],
        ("white_space_in_element_content", 1):
            [("white_space_in_element_content", 1)],
        ("cdata_nodes", 0): [("cdata_nodes", 0)],
        ("cdata_nodes", 1): [("cdata_nodes", 1)],
        ("comments", 0): [("comments", 0)],
        ("comments", 1): [("comments", 1)],
        ("charset_overrides_xml_encoding", 0):
            [("charset_overrides_xml_encoding", 0)],
        ("charset_overrides_xml_encoding", 1):
            [("charset_overrides_xml_encoding", 1)],
    }

    def getFeature(self, name):
        try:
            return getattr(self._options, _name_xform(name))
        except AttributeError:
            raise xml.dom.NotFoundErr()

    def parseURI(self, uri):
        if self.entityResolver:
            input = self.entityResolver.resolveEntity(None, uri)
        else:
            input = DOMEntityResolver().resolveEntity(None, uri)
        return self.parseDOMInputSource(input)

    def parseDOMInputSource(self, input):
        options = copy.copy(self._options)
        options.filter = self.filter
        options.errorHandler = self.errorHandler
        fp = input.byteStream
        if fp is None and options.systemId:
            import urllib
            fp = urllib.urlopen(input.systemId)
        builder = ExpatBuilder.makeBuilder(options)
        return builder.parseFile(fp)


class DOMEntityResolver(Core.DOMImplementation):
    def resolveEntity(self, publicId, systemId):
        source = DOMInputSource()
        source.publicId = publicId
        source.systemId = systemId
        if systemId:
            import urllib
            self.byteStream = urllib.urlopen(systemId)
            # Should parse out the content-type: header to
            # get charset information so that we can set the
            # encoding attribute on the DOMInputSource.
        return source


class DOMInputSource(Core.AttributeControl):
    byteStream = None
    characterStream = None
    encoding = None
    publicId = None
    systemId = None

    def _get_byteStream(self):
        return self.byteStream
    def _set_byteStream(self, byteStream):
        self.__dict__['byteStream'] = byteStream

    def _get_characterStream(self):
        return self.characterStream
    def _set_characterStream(self, characterStream):
        self.__dict__['characterStream'] = characterStream

    def _get_encoding(self):
        return self.encoding
    def _set_encoding(self, encoding):
        self.__dict__['encoding'] = encoding

    def _get_publicId(self):
        return self.publicId
    def _set_publicId(self, publicId):
        self.__dict__['publicId'] = publicId

    def _get_systemId(self):
        return self.systemId
    def _set_systemId(self, systemId):
        self.__dict__['systemId'] = systemId


class DOMBuilderFilter:
    """Element filter which can be used to tailor construction of
    a DOM instance.
    """

    # There's really no need for this class; concrete implementations
    # should just implement the endElement() method as appropriate.

    def endElement(self, element):
        # Why this method is supposed to return anything at all
        # is a mystery; the result doesn't appear to be used.
        return 1


def _name_xform(name):
    return string.replace(string.lower(name), '-', '_')

##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Serializers for Shane's AdaptableStorage

    The properties must be deserialized prior the actual xml.

$Id: AdaptableStorage.py,v 1.2 2004/04/27 13:06:18 faassen Exp $
"""
from types import StringType
from cStringIO import StringIO

from Products.AdaptableStorage.mapper.public import IAspectSerializer,\
    FieldSchema, RowSequenceSchema
from ParsedXML import ParsedXML, createDOMDocument

class ParsedXMLSerializer:
    """Serializer for ParsedXML Documents.

        Only the raw XML is stored in the filesystem.
    """
    
    __implements__ = IAspectSerializer

    schema = FieldSchema('data', 'string')
    attributes = (
           )
        
    def getSchema(self):
        return self.schema

    def canSerialize(self, object):
        return isinstance(object, ParsedXML)
    
    def serialize(self, object, event):
        encoding = 'utf-8'
        data = object.writeStream(encoding=encoding).getvalue().encode(encoding)
        event.ignoreAttributes([ '_node', '_persistentDoc', '_lenCache',
            '_lenCorrect', '_container'])
        return data

    def deserialize(self, object, event, state):
        assert isinstance(state, StringType)
        object._persistentDoc = object
        object._lenCache = 0
        object._lenCorrect = 0
        object.initFromDOMDocument(createDOMDocument(state, 
            not object.noNamespaces))


class ParsedXMLPropertiesSerializer:
    """Serialize parsed xml's properties"""
    
    __implements__ = IAspectSerializer
    
    schema = RowSequenceSchema()
    schema.addField('id', 'string', 1)
    schema.addField('type', 'string')
    schema.addField('data', 'string')

    attributes = {
        'title': str,
        'contentType': str,
        'noNamespaces': int,
     }

    def getSchema(self):
        return self.schema

    def canSerialize(self, object):
        return isinstance(object, ParsedXML)

    def serialize(self, object, event):
        res = []
        for attribute, factory in self.attributes.items():
            if not hasattr(object, attribute):
                continue
            value = getattr(object, attribute)
            t = factory.__name__
            if value is None:
                if factory in (int, long):
                    value = 0
                else: 
                    value = ''
            value = str(value)
            event.ignoreAttribute(attribute)
            res.append((attribute, t, value))
        return res 

    def deserialize(self, object, event, state):
        for attribute, t, value in state:
            factory = self.attributes.get(attribute)
            if factory is None:
                continue
            value = factory(value)
            setattr(object, attribute, value)
            assert getattr(object, attribute) == value


# -*- coding: utf-8 -*-
#-##########################################################################-#
#
# XOo°f - http://www.xooof.org
# A development and XML specification framework for documenting and
# developing the services layer of enterprise business applications.
# From the specifications, it generates WSDL, DocBook, client-side and
# server-side code for Java, C# and Python.
#
# Copyright (C) 2006 Software AG Belgium
#
# This file is part of XOo°f.
#
# XOo°f is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# XOo°f is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#-##########################################################################-#


from xml.sax.handler import feature_namespaces, property_lexical_handler
from xml.dom.minidom import Node

import handlers, domutils
from utils import createInstance, noatts
from translations import _

#FTVField = 1
#FTVLField = 2
#FTGField = 3
#FTGLField = 4
#FTXMLField = 5

class IMetaField:

    #def getFieldType(self):
    #    pass

    def validate(self, value, eb, ctx):
        pass

    def getDefaultValue(self):
        pass

    def toSAX(self, handler, fieldName, fieldValue, nsmgr):
        pass

    def getNsURI(self):
        pass

    def getContentHandler(self, context, handlerToRestore, parentGroup, fieldName, ctx, atts):
        pass

class _MetaNLField:
    ' mixin for non list fields '

    def __init__(self, mandatory):
        self._MetaNLField__mandatory = mandatory

    def checkList(self,isList):
        return not isList

    def validateNLField(self, value, eb, ctx):
        ok = 1
        if self._MetaNLField__mandatory and value is None:
            eb.addError(_('The field is mandatory'), ctx)
            ok = 0
        return ok

    def isMandatory(self):
        return self._MetaNLField__mandatory

class _MetaLField:
    ' mixin for list fields '

    def __init__(self, minOccur = 0, maxOccur = None):
        self._MetaLField__minOccur = minOccur
        self._MetaLField__maxOccur = maxOccur

    def checkList(self,isList):
        return isList

    def getMinOccur(self):
        return self._MetaLField__minOccur

    def getMaxOccur(self):
        return self._MetaLField__maxOccur

    def validateLField(self, coll, eb, ctx):
        ok = 1
        l = len(coll)
        if (l < self._MetaLField__minOccur):
            eb.addError((_('There are not enough items in the list (%d < %d)') % (l, self._MetaLField__minOccur)), ctx)
            ok = 0
        if ((self._MetaLField__maxOccur is not None) and (l > self._MetaLField__maxOccur)):
            eb.addError((_('There are too many items in the list (%d > %d)') % (l, self._MetaLField__maxOccur)), ctx)
            ok = 0
        return ok

class _MetaChoice:

    def __init__(self):
        self.__choices = None

    def addChoiceXML(self,s):
        if self.__choices is None:
            self.__choices = []
        self.__choices.append(self.getTypeInfo().xml2py(s))

    def validateChoices(self,value,eb,ctx):
        if self.__choices is not None:
            if not value in self.__choices:
                eb.addError(_('The value (%s) is not part of the ' \
                            'available choices') % \
                            self.getTypeInfo().py2xml(value),
                            ctx)
        return 1

class MetaVField(IMetaField, _MetaNLField, _MetaChoice):

    SERIALIZE_element = 1
    SERIALIZE_attribute = 2

    #def getFieldType(self):
    #    return FTVField

    def validate(self, value, eb, ctx):
        ok = _MetaNLField.validateNLField(self, value, eb, ctx)
        if value is not None:
            ok = (self.__typeInfo.validate(value, eb, ctx) and ok)
            ok = (self.validateChoices(value, eb, ctx) and ok)
        return ok

    def getDefaultValue(self):
        return self.__defaultValue

    def getNsURI(self):
        return self.__nsURI

    def getContentHandler(self, context, handlerToRestore, parentGroup, fieldName, ctx, atts):
        return handlers.VFieldHandler(context, handlerToRestore, parentGroup, fieldName, ctx, self.__typeInfo)

    def __init__(self, nsURI, typeInfo, mandatory, serialize):
        _MetaNLField.__init__(self, mandatory)
        _MetaChoice.__init__(self)
        self.__nsURI = nsURI
        self.__typeInfo = typeInfo
        self.__defaultValue = None
        self.__serialize = serialize
        if self.__serialize != self.SERIALIZE_element:
            # TBC
            raise RuntimeError, "serialization mode not implemented"

    def getTypeInfo(self):
        return self.__typeInfo

    def setDefaultValueXML(self, xmlValue):
        self.__defaultValue = self.__typeInfo.xml2py(xmlValue)

    def toSAX(self, handler, fieldName, fieldValue, nsmgr):
        if fieldValue is not None:
            name = (self.__nsURI, fieldName)
            qname,newContext = nsmgr.getQNameAutoPush(name,handler)
            handler.startElementNS(name, qname, noatts)
            handler.characters(self.__typeInfo.py2xml(fieldValue))
            handler.endElementNS(name, qname)
            if newContext:
                nsmgr.pop()

class MetaVLField(IMetaField, _MetaLField, _MetaChoice):

    #def getFieldType(self):
    #    return FTVLField

    def validate(self, value, eb, ctx):
        ok = _MetaLField.validateLField(self, value, eb, ctx)
        validate = self.__typeInfo.validate
        i = 0
        for item in value:
            ok = (validate(item, eb, "%s[%d]" % (ctx,i)) and ok)
            ok = (self.validateChoices(item, eb, "%s[%d]" % (ctx,i)) and ok)
            i += 1
        return ok

    def getDefaultValue(self):
        return []

    def getNsURI(self):
        return self.__nsURI

    def getContentHandler(self, context, handlerToRestore, parentGroup, fieldName, ctx, atts):
        return handlers.VLFieldHandler(context, handlerToRestore, parentGroup, fieldName, ctx, self.__nsURI, self.__typeInfo)

    def __init__(self, nsURI, typeInfo, minOccur = 0, maxOccur = None):
        _MetaLField.__init__(self, minOccur, maxOccur)
        _MetaChoice.__init__(self)
        self.__nsURI = nsURI
        self.__typeInfo = typeInfo

    def getTypeInfo(self):
        return self.__typeInfo

    def toSAX(self, handler, fieldName, fieldValue, nsmgr):
        if len(fieldValue):
            name = (self.__nsURI, fieldName + '-list')
            itemName = (self.__nsURI, fieldName)
            qname,newContext = nsmgr.getQNameAutoPush(name,handler)
            itemQName = nsmgr.getQName(itemName)
            handler.startElementNS(name, qname, noatts)
            for itemValue in fieldValue:
                handler.startElementNS(itemName, itemQName, noatts)
                handler.characters(self.__typeInfo.py2xml(itemValue))
                handler.endElementNS(itemName, itemQName)
            handler.endElementNS(name, qname)
            if newContext:
                nsmgr.pop()

class MetaGField(IMetaField, _MetaNLField):

    #def getFieldType(self):
    #    return FTGField

    def validate(self, value, eb, ctx):
        ok = _MetaNLField.validateNLField(self, value, eb, ctx)
        if value is not None:
            if isinstance(value, self.__klass):
                ok = (value._xsValidateNoRaise(eb, ctx) and ok)
            else:
                eb.addError((_('The object must be an instance of class %s') % \
                            self.__klass), ctx)
                ok = 0
        return ok

    def getDefaultValue(self):
        return None

    def __init__(self, nsURI, klass, mandatory):
        _MetaNLField.__init__(self, mandatory)
        self.__nsURI = nsURI
        self.__klass = klass

    def getClass(self):
        return self.__klass

    def toSAX(self, handler, fieldName, fieldValue, nsmgr):
        if fieldValue is not None:
            if not isinstance(fieldValue,self.__klass):
                raise RuntimeError("gfield value %s is not of type %s" % (fieldName,self.__klass))
            fieldValue._xsToSAX(handler, (self.__nsURI, fieldName), nsmgr, self.__klass)

    def getNsURI(self):
        return self.__nsURI

    def getContentHandler(self, context, handlerToRestore, parentGroup, fieldName, ctx, atts):
        # TBC: what is the right nsuri for the type attribute?
        instance = createInstance(self.__klass,atts,context.structFactory)
        return handlers.GFieldHandler(context, handlerToRestore, handlerToRestore, parentGroup, fieldName, ctx, instance)


class MetaGLField(IMetaField, _MetaLField):

    #def getFieldType(self):
    #    return FTGField

    def getDefaultValue(self):
        return []

    def validate(self, value, eb, ctx):
        ok = _MetaLField.validateLField(self, value, eb, ctx)
        i = 0
        for item in value:
            if isinstance(item, self.__klass._itemKlass):
                ok = (item._xsValidateNoRaise(eb, "%s[%d]" % (ctx,i)) and ok)
            else:
                eb.addError((_('The object must be an instance of class %s') % \
                            self.__klass._itemKlass), "%s[%d]" % (ctx,i))
                ok = 0
            i += 1
        return ok

    def __init__(self, nsURI, klass, minOccur = 0, maxOccur = None):
        _MetaLField.__init__(self, minOccur, maxOccur)
        self.__nsURI = nsURI
        self.__klass = klass

    def getClass(self):
        return self.__klass

    def toSAX(self, handler, fieldName, fieldValue, nsmgr):
        if len(fieldValue):
            name = (self.__nsURI, fieldName + '-list')
            itemName = (self.__nsURI, fieldName)
            qname,newContext = nsmgr.getQNameAutoPush(name,handler)
            handler.startElementNS(name, qname, noatts)
            for itemValue in fieldValue:
                if not isinstance(itemValue,self.__klass._itemKlass):
                    raise RuntimeError("An item of glfield %s is not of type %s (got %s)" % (fieldName,self.__klass._itemKlass,type(itemValue)))
                itemValue._xsToSAX(handler, itemName, nsmgr, self.__klass._itemKlass)
            handler.endElementNS(name, qname)
            if newContext:
                nsmgr.pop()

    def getNsURI(self):
        return self.__nsURI

    def getContentHandler(self, context, handlerToRestore, parentGroup, fieldName, ctx, atts):
        return handlers.GLFieldHandler(context, handlerToRestore, handlerToRestore, parentGroup, fieldName, ctx, self.__nsURI, self.__klass())

class MetaXMLField(IMetaField, _MetaNLField, _MetaChoice):

    #def getFieldType(self):
    #    return FTXMLField

    def validate(self, value, eb, ctx):
        ok = _MetaNLField.validateNLField(self, value, eb, ctx)
        if value is not None:
            if value.nodeType != Node.DOCUMENT_FRAGMENT_NODE:
                eb.addError((_('The object must be a DocumentFragment DOM node'),
                             ctx))
                ok = 0
        return ok

    def getDefaultValue(self):
        return None

    def getNsURI(self):
        return self.__nsURI

    def getContentHandler(self, context, handlerToRestore, parentGroup, fieldName, ctx, atts):
        return handlers.XMLFieldHandler(context, handlerToRestore, parentGroup, fieldName, ctx)

    def __init__(self, nsURI, mandatory):
        _MetaNLField.__init__(self, mandatory)
        self.__nsURI = nsURI

    def toSAX(self, handler, fieldName, fieldValue, nsmgr):
        if fieldValue is not None:
            name = (self.__nsURI, fieldName)
            qname,newContext = nsmgr.getQNameAutoPush(name,handler)
            handler.startElementNS(name, qname, noatts)
            domReader = domutils.DOMReader()
            domReader.setFeature(feature_namespaces,1)
            domReader.setContentHandler(handler)
            domReader.setProperty(property_lexical_handler,handler)
            for childNode in fieldValue.childNodes:
                domReader.parse(childNode)
            handler.endElementNS(name, qname)
            if newContext:
                nsmgr.pop()

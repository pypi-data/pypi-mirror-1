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


import warnings

from xml.sax.handler import ContentHandler
from xml.sax.xmlreader import AttributesNSImpl

import xmlstruct, domutils

noatts = AttributesNSImpl({},{})

typeAttName = (domutils.XSI_NAMESPACE,"type")

def makeCtx(ctx, fieldName):
    if ctx:
        return ctx+"."+fieldName
    else:
        return fieldName

class _NsContext:

    def __init__(self,nsUriPfx,nsPfxUri):
        self.nsUriPfx = nsUriPfx
        self.nsPfxUri = nsPfxUri
        self.__tounmap = []
        self.__depth = 0

    def copy(self):
        return _NsContext(self.nsUriPfx.copy(),self.nsPfxUri.copy())

    def setPrefixMapping(self,prefix,uri,handler=None):
        if self.nsPfxUri.has_key(prefix):
            del self.nsUriPfx[self.nsPfxUri[prefix]]
        self.nsPfxUri[prefix] = uri
        self.nsUriPfx[uri] = prefix
        if handler is not None:
            handler.startPrefixMapping(prefix,uri)
            self.__tounmap.append((handler,prefix))

    def endPrefixMappings(self):
        for handler,prefix in self.__tounmap:
            handler.endPrefixMapping(prefix)
        self.__tounmap = []

class NamespacesManager:

    def __init__(self,aNsUriPfx=None):
        nsUriPfx = {
          domutils.XML_NAMESPACE: "xml",
          domutils.XMLNS_NAMESPACE: "xmlns",
          None: None,
        }
        nsPfxUri = {}
        for uri,pfx in nsUriPfx.items():
            nsPfxUri[pfx] = uri
        self.__stack = [_NsContext(nsUriPfx,nsPfxUri)]
        if aNsUriPfx is not None:
            self.push()
            for uri,pfx in aNsUriPfx.items():
                self.setPrefixMapping(pfx,uri)

    def getUri(self,prefix):
        return self.__stack[-1].nsPfxUri[prefix]

    def getPrefix(self,uri):
        return self.__stack[-1].nsUriPfx[uri]

    def getPrefixAutoPush(self,uri,handler=None,prefix=None):
        """Returns (prefix,newContext).

        If newContext is true, then pop must be called later."""
        try:
            return self.getPrefix(uri),0
        except KeyError:
            self.push()
            self.setPrefixMapping(prefix,uri,handler)
            return prefix,1

    def getQName(self,(uri,localName)):
        prefix = self.getPrefix(uri)
        if prefix:
            return prefix+":"+localName
        else:
            return localName

    def getQNameForAttr(self,(uri,localName)):
        if uri is None:
            return localName
        else:
            return self.getQName((uri,localName))

    def getQNameAutoPush(self,(uri,localName),handler=None,prefix=None):
        """Returns (qname,newContext).

        If newContext is true, then pop must be called later."""
        prefix,newContext = self.getPrefixAutoPush(uri,handler,prefix)
        if prefix:
            qname = prefix+":"+localName
        else:
            qname = localName
        return qname,newContext

    def getQNameAtt(self,(uri,localName)):
        if not uri:
            return localName
        else:
            prefix = self.getPrefix(uri)
            if prefix:
                return prefix+":"+localName
            else:
                raise RuntimeError, "attributes qnames must have a prefix unless they are in the empty namespace"

    def getQNameAttAutoPush(self,(uri,localName),handler=None,prefix=None):
        """Returns (qname,newContext).

        If newContext is true, then pop must be called later."""
        if not uri:
            return localName,0
        else:
            prefix,newContext = self.getPrefixAutoPush(uri,handler,prefix)
            if prefix:
                qname = prefix+":"+localName
            else:
                raise RuntimeError, "attributes qnames must have a prefix unless they are in the empty namespace"
            return qname,newContext

    def setPrefixMapping(self,prefix,uri,handler=None):
        self.__stack[-1].setPrefixMapping(prefix,uri,handler)

    def push(self):
        self.__stack.append(self.__stack[-1].copy())

    def pop(self):
        self.__stack[-1].endPrefixMappings()
        del self.__stack[-1]

def createInstance(defaultKlass,atts,structFactory):
    try:
        # TBC: explicit namespace uri for type attribute value
        typeName = (defaultKlass._getMetaStruct()._xsNamespaceURI,atts[typeAttName])
    except KeyError:
        instance = defaultKlass()
    else:
        if structFactory is None:
            warnings.warn("No struct factory to create instance of %s. " \
                          "Reverting to default class %s." % \
                          (typeName,defaultKlass))
            instance = defaultKlass()
        else:
            try:
                instance = structFactory.create(typeName)
            except xmlstruct.XMLStructFactoryError, e:
                warnings.warn("Struct factory can't create " \
                              "instance of %s: %s. " \
                              "Reverting to default class %s." % \
                              (typeName,e,defaultKlass))
                instance = defaultKlass()
            else:
                if not isinstance(instance,defaultKlass):
                    raise RuntimeError("Type indicated in instance is not a subtype of %s" % defaultKlass.__name__)
    return instance

class FromSAXContext:

    def __init__(self,structFactory,reader,eb,nsmgr):
        self.structFactory = structFactory
        self.reader = reader
        self.eb = eb
        self.nsmgr = nsmgr

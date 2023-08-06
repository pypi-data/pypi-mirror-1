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


import string, sys
import xml.dom
from xml.sax.handler import ContentHandler, property_lexical_handler
from xml.sax.saxlib import LexicalHandler

import domutils, utils

class _FieldHandler(ContentHandler, LexicalHandler):

    def __init__(self,nsmgr):
        self.__nsmgr = nsmgr

    def startPrefixMapping(self,prefix,uri):
        self.__nsmgr.push()
        self.__nsmgr.setPrefixMapping(prefix,uri)

    def endPrefixMapping(self,prefix):
        self.__nsmgr.pop()

class VFieldHandler(_FieldHandler):

    def __init__(self,context,handlerToRestore,parentGroup,fieldName,ctx,typeInfo):
        _FieldHandler.__init__(self,context.nsmgr)
        self.__context = context
        self.__handlerToRestore = handlerToRestore
        self.__parentGroup = parentGroup
        self.__fieldName = fieldName
        self.__ctx = ctx
        self.__ignoreDepth = 0
        self.__typeInfo = typeInfo
        self.__content = []

    def characters(self,content):
        #print "V+",content
        if self.__ignoreDepth == 0:
            self.__content.append(content)

    ignorableWhitespace = characters

    def startElementNS(self,name,qname,atts):
        #print "V(",name
        self.__ignoreDepth += 1

    def endElementNS(self,name,qname):
        #print "V)",name
        if self.__ignoreDepth:
            self.__ignoreDepth -= 1
        else:
            #print "Vrestore"
            try:
                value = self.__typeInfo.xml2py(string.join(self.__content,""))
            except:
                self.__context.eb.addError(str(sys.exc_info()[1]),self.__ctx)
            else:
                if self.__fieldName is not None:
                    # parent is struct
                    setattr(self.__parentGroup,self.__fieldName,value)
                else:
                    # parent is list field
                    self.__parentGroup.append(value)
            self.__context.reader.setContentHandler(self.__handlerToRestore)
            self.__context.reader.setProperty(property_lexical_handler, \
                    self.__handlerToRestore)
            self.__context = None

class VLFieldHandler(_FieldHandler):

    def __init__(self,context,handlerToRestore,parentGroup,fieldName,ctx,nsURI,typeInfo):
        _FieldHandler.__init__(self,context.nsmgr)
        self.__context = context
        self.__handlerToRestore = handlerToRestore
        self.__parentGroup = parentGroup
        self.__fieldName = fieldName
        self.__ctx = ctx
        self.__ignoreDepth = 0
        self.__nsURI = nsURI
        self.__typeInfo = typeInfo
        self.__list = []

    def startElementNS(self,name,qname,atts):
        if self.__ignoreDepth == 0:
            if self.__nsURI == name[0]:
                assert(self.__context.reader.getContentHandler() is self)
                assert(self.__context.reader.getProperty(property_lexical_handler) is self)
                h = VFieldHandler(
                        self.__context,
                        self,
                        self.__list,
                        None,
                        "%s[%d]" % (self.__ctx,len(self.__list)),
                        self.__typeInfo)
                self.__context.reader.setContentHandler(h)
                self.__context.reader.setProperty(property_lexical_handler,h)
            else:
                self.__ignoreDepth += 1
        else:
            self.__ignoreDepth += 1

    def endElementNS(self,name,qname):
        if self.__ignoreDepth:
            self.__ignoreDepth -= 1
        else:
            setattr(self.__parentGroup,self.__fieldName,self.__list)
            self.__context.reader.setContentHandler(self.__handlerToRestore)
            self.__context.reader.setProperty(property_lexical_handler, \
                    self.__handlerToRestore)
            self.__context = None

class GFieldHandler(_FieldHandler):

    def __init__(self,context,contentHandlerToRestore,lexicalHandlerToRestore,parentGroup,fieldName,ctx,instance):
        _FieldHandler.__init__(self,context.nsmgr)
        self.__context = context
        self.__contentHandlerToRestore = contentHandlerToRestore
        self.__lexicalHandlerToRestore = lexicalHandlerToRestore
        self.__parentGroup = parentGroup
        self.__fieldName = fieldName
        self.__ctx = ctx
        self.__ignoreDepth = 0
        self.__instance = instance

    def startElementNS(self,name,qname,atts):
        #print "G(",name
        if self.__ignoreDepth == 0:
            fieldName = name[1]
            if fieldName.endswith("-list"):
                fieldName = fieldName[:-5]
                isList = 1
            else:
                isList = 0
            try:
                metaField = self.__instance._getMetaStruct()._dfields[fieldName]
            except KeyError:
                self.__ignoreDepth += 1
            else:
                if metaField.getNsURI() == name[0] and \
                   metaField.checkList(isList):
                    assert(self.__context.reader.getContentHandler() is self)
                    assert(self.__context.reader.getProperty(property_lexical_handler) is self)
                    try:
                        h = metaField.getContentHandler(
                                self.__context,
                                self,
                                self.__instance,
                                fieldName,
                                utils.makeCtx(self.__ctx,fieldName),
                                atts)
                        self.__context.reader.setContentHandler(h)
                        self.__context.reader.setProperty( \
                                property_lexical_handler,h)
                    except:
                        self.__context.eb.addError(str(sys.exc_info()[1]),utils.makeCtx(self.__ctx,fieldName))
                        self.__ignoreDepth += 1
                else:
                    self.__ignoreDepth += 1
        else:
            self.__ignoreDepth += 1

    def endElementNS(self,name,qname):
        #print "G)",name
        if self.__ignoreDepth:
            self.__ignoreDepth -= 1
        else:
            #print "Grestore"
            if self.__parentGroup is not None:
                if self.__fieldName is not None:
                    # parent is struct
                    setattr(self.__parentGroup,
                            self.__fieldName,
                            self.__instance)
                else:
                    # parent is list field
                    self.__parentGroup.append(self.__instance)
            #else: parent is root struct
            self.__context.reader.setContentHandler(self.__contentHandlerToRestore)
            self.__context.reader.setProperty(property_lexical_handler, \
                    self.__lexicalHandlerToRestore)
            self.__context = None

class GLFieldHandler(_FieldHandler):

    def __init__(self,context,contentHandlerToRestore,lexicalHandlerToRestore,parentGroup,fieldName,ctx,nsURI,listInstance):
        _FieldHandler.__init__(self,context.nsmgr)
        self.__context = context
        self.__contentHandlerToRestore = contentHandlerToRestore
        self.__lexicalHandlerToRestore = lexicalHandlerToRestore
        self.__parentGroup = parentGroup
        self.__fieldName = fieldName
        self.__ctx = ctx
        self.__ignoreDepth = 0
        self.__nsURI = nsURI
        self.__listInstance = listInstance

    def startElementNS(self,name,qname,atts):
        if self.__ignoreDepth == 0:
            if self.__nsURI == name[0]:
                # TBC: what is the right nsuri for the type attribute?
                try:
                    instance = utils.createInstance(self.__listInstance._itemKlass,
                                                    atts,
                                                    self.__context.structFactory)
                except:
                    self.__context.eb.addError(str(sys.exc_info()[1]),"%s[%d]" % (self.__ctx,len(self.__listInstance)))
                    self.__ignoreDepth += 1
                else:
                    assert(self.__context.reader.getContentHandler() is self)
                    assert(self.__context.reader.getProperty(property_lexical_handler) is self)
                    h = GFieldHandler(
                            self.__context,
                            self,
                            self,
                            self.__listInstance,
                            None,
                            "%s[%d]" % (self.__ctx,len(self.__listInstance)),
                            instance)
                    self.__context.reader.setContentHandler(h)
                    self.__context.reader.setProperty( \
                            property_lexical_handler,h)
            else:
                self.__ignoreDepth += 1
        else:
            self.__ignoreDepth += 1

    def endElementNS(self,name,qname):
        if self.__ignoreDepth:
            self.__ignoreDepth -= 1
        else:
            if self.__parentGroup is not None:
                setattr(self.__parentGroup,self.__fieldName,self.__listInstance)
            #else: parent is root struct
            self.__context.reader.setContentHandler(self.__contentHandlerToRestore)
            self.__context.reader.setProperty(property_lexical_handler, \
                    self.__lexicalHandlerToRestore)
            self.__context = None

class XMLFieldHandler(_FieldHandler):

    def __init__(self,context,handlerToRestore,parentGroup,fieldName,ctx):
        _FieldHandler.__init__(self,context.nsmgr)
        self.__context = context
        self.__handlerToRestore = handlerToRestore
        self.__parentGroup = parentGroup
        self.__fieldName = fieldName
        self.__ctx = ctx
        # force usage of the 4DOM implementation to avoid
        # pickling issue with the default "minidom" implementation.
        self.__doc = xml.dom.getDOMImplementation("4DOM").createDocument(None,"dummy",None)
        self.__stack = [self.__doc.createDocumentFragment()]
        self.__text = []
        self.__nsattNodes = []

    def _completeText(self):
        if self.__text:
            node = self.__doc.createTextNode(string.join(self.__text,""))
            self.__stack[-1].appendChild(node)
            self.__text = []

    def startPrefixMapping(self,prefix,uri):
        _FieldHandler.startPrefixMapping(self,prefix,uri)
        if prefix:
            qname = "xmlns:"+prefix
        else:
            qname = "xmlns"
        nsattNode = self.__doc.createAttributeNS(domutils.XMLNS_NAMESPACE,qname)
        nsattNode.value = uri
        self.__nsattNodes.append(nsattNode)

    def startElementNS(self,(uri,localName),qname,atts):
        self._completeText()
        node = self.__doc.createElementNS(uri,self.__context.nsmgr.getQName((uri,localName)))
        for attName,attValue in atts.items():
            attNamespaceURI,attLocalName = attName
            if attNamespaceURI != domutils.XMLNS_NAMESPACE:
                attNode = self.__doc.createAttributeNS(attNamespaceURI,self.__context.nsmgr.getQNameForAttr(attName))
                attNode.value = attValue
                node.setAttributeNodeNS(attNode)
        if self.__nsattNodes:
            for nsattNode in self.__nsattNodes:
                node.setAttributeNodeNS(nsattNode)
            self.__nsattNodes = []
        self.__stack[-1].appendChild(node)
        self.__stack.append(node)

    def endElementNS(self,name,qname):
        self._completeText()
        if len(self.__stack) > 1:
            del self.__stack[-1]
        else:
            setattr(self.__parentGroup,self.__fieldName,self.__stack[-1])
            self.__context.reader.setContentHandler(self.__handlerToRestore)
            self.__context.reader.setProperty(property_lexical_handler, \
                    self.__handlerToRestore)
            self.__context = None

    def ignorableWhitespace(self,content):
        self.__text.append(content)

    def characters(self,content):
        self.__text.append(content)

    def processingInstruction(self,target,data):
        self._completeText()
        node = self.__doc.createProcessingInstruction(target,data)
        self.__stack[-1].appendChild(node)

    # LexicalHandler

    def comment(self,data):
        self._completeText()
        node = self.__doc.createComment(data)
        self.__stack[-1].appendChild(node)

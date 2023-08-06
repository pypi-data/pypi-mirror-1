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


import sys
import copy
from types import UnicodeType
from UserList import UserList
from cStringIO import StringIO

import xml.sax
from xml.sax.saxutils import LexicalXMLGenerator
from xml.sax.handler import ContentHandler, feature_namespaces, \
        property_lexical_handler
from xml.sax.saxlib import LexicalHandler
from xml.sax.xmlreader import AttributesNSImpl

import handlers
from errorbag import ErrorBag
import domutils, utils
from translations import _

class XMLStructFactoryError(RuntimeError):
    pass

class IXMLStructFactory:
    """Interface for XMLStruct factories. """

    def create(self,name):
        """Create a struct instance corresponding to a (uri,localname) tuple.

        Name is a (uri,localname) tuple, as passed to startElementNS and
        endElementNS SAX 2.0 ContentHandler methods. If the create method
        fails, it must raise XMLStructFactoryError.
        """
        pass

class XMLStructFactoryComposite(IXMLStructFactory):
    """A IXMLStructFactory that tries several factories in turn."""

    # TBC: This one could be improved if IXMLStructFactory
    #      supports a kind of getSupportedNamespaceURIs() method;
    #      we could then create a dictionary {nsuri -> [struct factories]}

    def __init__(self,factories):
        self.__factories = factories

    def create(self,name):
        errors = []
        for factory in self.__factories:
            try:
                return factory.create(name)
            except XMLStructFactoryError, e:
                errors.append(str(e))
        raise XMLStructFactoryError("\n".join(errors))

class XMLStructError(RuntimeError):

    def __init__(self,eb):
        self.eb = eb

    def __str__(self):
        return str(self.eb)

class IXMLStruct(object):
    """The IXMLStruct interface is implemented by all structs and struct
    collections."""

    #__slots__ = []

    def xsReset(self):
        """Reset all the fields to their default value.

        VFields are reset to None or the default values specified in the struct
        instance. GFields are reset to None. VLFields and GLFields are reset
        to an empty list."""
        pass

    def xsNamespaceURI(self):
        """Obtain the XML namespace URI for the struct instance."""
        pass

    def xsToXML(self, encoding=None, nsContext=None):
        """Convert the struct to an XML string.

        - encoding is the encoding of xml byte string returned
          if no encoding is specified, a unicode string object returned.
        - nsContext is a uri: prefix mapping; for each item in this
          mapping, start/endPrefixMapping events are fired."""
        pass

    def xsToSAX(self, handler, nsContext=None):
        """Generate SAX 2.0 events corresponding to an XML serialization
        of the struct instance.

        Only namespace-aware (startElementNS, endElementNS) events are fired.
        Other events fired are startPrefixMapping, endPrefixMapping and
        characters.

        - handler is the sax 2 content handler to receive the events.
        - nsContext is a uri: prefix mapping; xsToSAX *does not* fire
          start/endPrefixMapping events for prefixes in this mapping,
          instead it assumes that the namespace context is already
          set up for those prefixes."""
        pass

    def xsToDOM(self, ownerDocument=None, nsContext=None):
        """Generate a dom element node corresponding to an XML serialization
        of the struct instance.

        This requires xml.dom.ext.reader.Sax2 from PyXML.

        - nsContext is a uri: prefix mapping; xsToSAX *does not* fire
          start/endPrefixMapping events for prefixes in this mapping,
          instead it assumes that the namespace context is already
          set up for those prefixes."""
        pass

    def xsFromXML(self, xml, ctx="", structFactory=None):
        """Deserialize the struct instance from an XML string.

        If the XML string is not a serialization of the same struct
        class, an exception is raised (TBC: is this right? this is not
        consistent with the VB behaviour; what about java?).
        For this method to be of any practical use, you must know
        that the content of the XML string is a really a serialization of the
        struct instance.

        If unmarshalling errors occur, XMLStructError is raised.
        Other errors can be raised (parse errors for instances)."""
        pass

    def xsFromSAX(self, reader, ctx="", structFactory=None):
        """Deserialize the struct instance from a SAX 2.0 stream.

        This method must be called while the reader is parsing, and when
        the startElementNS for the root element of the struct has been
        received. All the events within the root element, up to and including
        the endElementNS of the rootElement will be "eaten" before the
        current ContentHandler is restored.
        The structFactory argument is used to deserialize polymorphic
        gfield or glfields. If it is not provided, the base class
        is always used.

        If unmarshalling errors occur, XMLStructError is raised."""
        pass

    def xsFromDOM(self, rootElement, ctx="", structFactory=None):
        """Deserialize the struct instance from a DOM tree.

        See also xsFromXML: the same comments apply."""
        pass

    def xsValidate(self, ctx=""):
        """Validate the struct instance against its specification.

        If validation errors are found, an XMLStrucError exception is raised."""
        pass

    def xsClone(self):
        """deep copy"""
        pass

    # TBC: do we need xsInitFrom in python?

class XMLStructHandler(ContentHandler, LexicalHandler):
    """SAX 2.0 handler to deserialize an XMLStruct.

    The first element encountered must correspond to a struct
    that the provided structFactory can create. After parsing,
    the getStruct() method can be used to retrieve the struct,
    and the getErrorBag() method can be used to retrieve the
    errors (the only errors that can be found in the error bag
    are unmarshalling errors, i.e. type errors while converting
    XML values to python values; other errors are considered
    fatal and reported as exceptions)."""

    def __init__(self,structFactory,reader,eb,nsContext,ctx=""):
        self.__structFactory = structFactory
        self.__reader = reader
        self.__eb = eb
        self.__nsmgr = utils.NamespacesManager(nsContext)
        self.__ctx = ctx
        self.__struct = None

    #def getErrorBag(self):
    #    return self.__context.eb

    def getStruct(self):
        return self.__struct

    def startPrefixMapping(self,prefix,uri):
        self.__nsmgr.push()
        self.__nsmgr.setPrefixMapping(prefix,uri)

    def endPrefixMapping(self,prefix):
        self.__nsmgr.pop()

    def startElementNS(self,name,qname,atts):
        self.__struct = self.__structFactory.create(name)
        context = utils.FromSAXContext(self.__structFactory,
                                       self.__reader,
                                       self.__eb,
                                       self.__nsmgr)
        self.__struct._xsFromSAXNoRaise(context,self.__ctx)

class _XMLStructFactoryInstance(IXMLStructFactory):
    """A kind of "identity" struct factory.

    It returns a pre-built instance when asked the first time,
    and then calls the chained factory forever.
    If the name does not correspond to the provided instance,
    an XMLStructFactoryError is raised."""

    def __init__(self,instance,chainedStructFactory):
        self.__firstTime = 1
        self.__instance = instance
        self.__chainedStructFactory = chainedStructFactory

    def create(self,name):
        if self.__firstTime:
            className = name[1]
            if className.endswith("-list"):
                className = className[:-5]+"_C"
            if name[0] == self.__instance.xsNamespaceURI() and \
               className == self.__instance.__class__.__name__:
                self.__firstTime = 0
                return self.__instance
            else:
                raise XMLStructFactoryError, \
                      "Name and/or URI do not match for instance"
        else:
            if self.__chainedStructFactory is not None:
                return self.__chainedStructFactory.create(name)
            else:
                raise XMLStructFactoryError, \
                      "No chained struct factory"

class _XMLStructCommonBase(IXMLStruct):

    #__slots__ = []

    def xsToXML(self, encoding=None, nsContext=None):
        sio = StringIO()
        handler = LexicalXMLGenerator(sio,encoding or "utf-8")
        if nsContext is not None:
            for uri,prefix in nsContext.items():
                handler.startPrefixMapping(prefix,uri)
        self.xsToSAX(handler,nsContext)
        if nsContext is not None:
            for uri,prefix in nsContext.items():
                handler.endPrefixMapping(prefix)
        if encoding:
            # an encoding was requested: return the encoded byte string
            return sio.getvalue()
        else:
            # no encoding was requested: return a unicode string
            return sio.getvalue().decode("utf-8")

    def xsToDOM(self, ownerDocument=None, nsContext=None):
        self.xsToSAX(domutils.makeXmlDomGenerator(ownerDocument),nsContext)
        return handler.getRootNode()

    def xsFromSAX(self, reader, ctx="", structFactory=None):
        eb = ErrorBag()
        context = utils.FromSAXContext(structFactory,
                                       reader,
                                       eb,
                                       utils.NamespacesManager())
        self._xsFromSAXNoRaise(context,ctx)
        if eb.length():
            raise XMLStructError(eb)

    def xsFromXML(self, xmls, ctx="", structFactory=None):
        fromXML(_XMLStructFactoryInstance(self,structFactory),xmls,ctx)

    def xsFromDOM(self, rootElement, ctx="", structFactory=None):
        fromDOM(_XMLStructFactoryInstance(self,structFactory),rootElement,ctx)

    def xsValidate(self, ctx=""):
        eb = ErrorBag()
        self._xsValidateNoRaise(eb, ctx)
        if eb.length():
            raise XMLStructError(eb)

    def xsClone(self):
        return copy.deepcopy(self)

class XMLStructBase(_XMLStructCommonBase):
    """Base class for generated XMLStructs.

    Subclasses must provide a _getMetaStruct class method,
    which in turn must provide the following attributes:
    - _lfields: a list of (fieldName,MetaField),
    - _dfields: a mapping of (fieldName:MetaField),
    - _xsNamespaceURI."""

    #__slots__ = []

    def __init__(self,**args):
        #print args
        self.xsReset()
        _dfields = self._getMetaStruct()._dfields
        for fieldName,fieldValue in args.items():
            if fieldName in _dfields:
                setattr(self,fieldName,fieldValue)
            else:
                raise AttributeError(fieldName)
        #vars(self).update(args)

    def _getMetaFields(self):
        return self._getMetaStruct()._lfields

    def xsReset(self):
        for fieldName,fieldMeta in self._getMetaFields():
            setattr(self,fieldName,fieldMeta.getDefaultValue())

    def xsNamespaceURI(self):
        return self._getMetaStruct()._xsNamespaceURI

    def xsToSAX(self, handler, nsContext=None):
        self._xsToSAX(handler,
                      (self.xsNamespaceURI(),self.__class__.__name__),
                      utils.NamespacesManager(nsContext),
                      self.__class__)

    def _xsToSAX(self, handler, wrapperName, nsContext, baseKlass):
        qname,newContext = nsContext.getQNameAutoPush(wrapperName,handler)
        if self.__class__ != baseKlass:
            # TBC: use the correct prefix for type value
            typeAttQName,newContext2 = nsContext.getQNameAttAutoPush(utils.typeAttName,handler,"xsi")
            atts = AttributesNSImpl({utils.typeAttName: self.__class__.__name__},
                                    {utils.typeAttName: typeAttQName})
        else:
            newContext2 = 0
            atts = utils.noatts
        handler.startElementNS(wrapperName,qname,atts)
        for fieldName,fieldMeta in self._getMetaFields():
            fieldMeta.toSAX(handler,fieldName,getattr(self,fieldName),nsContext)
        handler.endElementNS(wrapperName,qname)
        if newContext2:
            nsContext.pop()
        if newContext:
            nsContext.pop()

    def _xsFromSAXNoRaise(self, context, ctx):
        h = handlers.GFieldHandler(
                context,
                context.reader.getContentHandler(),
                context.reader.getProperty(property_lexical_handler),
                None,
                None,
                ctx,
                self)
        context.reader.setContentHandler(h)
        context.reader.setProperty(property_lexical_handler,h)

    def _xsValidateNoRaise(self, eb, ctx):
        ok = 1
        for fieldName,fieldMeta in self._getMetaFields():
            ok = fieldMeta.validate(
              getattr(self,fieldName),eb,utils.makeCtx(ctx,fieldName)) and ok
        return ok

class XMLStructBase_C(_XMLStructCommonBase,UserList):
    """Base class for generated XMLStruct collections.

    Subclasses must provide an _itemKlass class attribute.
    """

    def __init__(self):
        UserList.__init__(self)

    def xsReset(self):
        self.data = []

    def xsNamespaceURI(self):
        return self._itemKlass._getMetaStruct()._xsNamespaceURI

    def xsToSAX(self, handler, nsContext=None):
        self._xsToSAX(handler,
                      (self.xsNamespaceURI(),self._itemKlass.__name__),
                      utils.NamespacesManager(nsContext),
                      self._itemKlass)

    def _xsToSAX(self, handler, wrapperName, nsContext, baseKlass):
        listWrapperName = (wrapperName[0],wrapperName[1]+"-list")
        qname,newContext = nsContext.getQNameAutoPush(listWrapperName,handler)
        handler.startElementNS(listWrapperName,qname,utils.noatts)
        for item in self.data:
            item._xsToSAX(handler,wrapperName,nsContext,baseKlass)
        handler.endElementNS(listWrapperName,qname)
        if newContext:
            nsContext.pop()

    def _xsFromSAXNoRaise(self, context, ctx):
        h = handlers.GLFieldHandler(
                context,
                context.reader.getContentHandler(),
                context.reader.getProperty(property_lexical_handler),
                None,
                None,
                ctx,
                self.xsNamespaceURI(),
                self)
        context.reader.setContentHandler(h)
        context.reader.setProperty(property_lexical_handler,h)

    def _xsValidateNoRaise(self, eb, ctx):
        ok = 1
        index = 0
        for item in self.data:
            if isinstance(item,self._itemKlass):
                ok = item._xsValidateNoRaise(eb,"%s[%d]" % (ctx,index)) and ok
            else:
                eb.addError((_('The object must be an instance of class %s') % \
                            self._itemKlass), "%s[%d]" % (ctx,index))
                ok = 0
            index += 1
        return ok

def fromSource(structFactory,source,ctx="",reader=None):
    """Create a struct from an xml source, using a struct factory.

    - structFactory must be an IXMLStructFactory instance.
    - source must be a valid source for the parse method of
      xml.sax.xmlreader.XMLReader.
    - ctx is an optional base context (e.g. the name of the object),
      used to indicate context in the error bag
    - reader is a SAX2 parser that must support the namespaces feature
    """
    if reader is None:
        reader = xml.sax.make_parser()
    reader.setFeature(feature_namespaces,1)
    eb = ErrorBag()
    handler = XMLStructHandler(structFactory,reader,eb,None,ctx=ctx)
    reader.setContentHandler(handler)
    reader.setProperty(property_lexical_handler,handler)
    reader.parse(source)
    if eb.length():
        raise XMLStructError(eb)
    return handler.getStruct()

def fromXML(structFactory,xmls,ctx="",reader=None):
    """Create a struct from an xml string, using a struct factory.

       See fromSource for details."""

    if type(xmls) is UnicodeType:
        # this is necessary because StringIO does not support unicode
        xmls = xmls.encode("UTF-8")

    if sys.platform[:4] != "java":
        source = StringIO(xmls)
    else:
        # TBC: this is a workaround for a drv_javasax bug (jython only)
        #      (note that xmlproc works in jython but does not support
        #      setContentHandler while parsing...)
        from org.xml.sax import InputSource
        from java.io import ByteArrayInputStream
        if reader is None:
            reader = xml.sax.make_parser(["xml.sax.drivers2.drv_javasax"])
        source = InputSource(ByteArrayInputStream(xmls))

    return fromSource(structFactory,source,ctx,reader)

def fromDOM(structFactory,rootElement,ctx=""):
    """Create a struct a DOM element node, using a struct factory.

       See fromSource for details."""
    return fromSource(structFactory,rootElement,ctx,domutils.DOMReader())

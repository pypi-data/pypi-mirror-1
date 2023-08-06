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


import base64, re, datetime

import xsdatetime
from xsdatetime import *

from translations import _


#DTBinary = 1
#DTBoolean = 2
#DTCode = 3
#DTDate = 4
#DTDatetime = 5
#DTDecimal = 6
#DTFloat = 7
#DTInt = 8
#DTString = 9
#DTTime = 10

# If set, the XML simple type serializers make
# additional effort to produce a canonical output.
canonical = 0

class ITypeInfo:

    #def getDataType(self):
    #    pass

    def py2xml(self, pyValue):
        pass

    def xml2py(self, xmlValue):
        pass

    def validate(self, value, eb, ctx):
        pass

class _TypeInfo_choices:
    """ Mixin class to handle choices """

    def __init__(self):
        self.__choices = None

    def addChoice(self,xmlValue):
        if self.__choices is None:
            self.__choices = []
        self.__choices.append(self.xml2py(xmlValue))

    def getChoices(self):
        return self.__choices

    def validateChoices(self, value, eb, ctx):
        if self.__choices is not None and not value in self.__choices:
            eb.addError(_("The value %s is not part of the available choices") % value,ctx)
            return 0
        else:
            return 1

class TypeInfo_binary(ITypeInfo):

    #def getDataType(self):
    #    return DTBinary

    def py2xml(self, pyValue):
        if canonical:
            return base64.encodestring(pyValue).replace("\n","")
        else:
            return base64.encodestring(pyValue)

    def xml2py(self, xmlValue):
        return base64.decodestring(xmlValue)

    def validate(self, value, eb, ctx):
        return 1

class TypeInfo_boolean(ITypeInfo):

    #def getDataType(self):
    #    return DTBoolean

    def py2xml(self, pyValue):
        if pyValue:
            return "true"
        else:
            return "false"

    def xml2py(self, xmlValue):
        if xmlValue in ("1","true"):
            return 1
        elif xmlValue in ("0","false"):
            return 0
        else:
            raise RuntimeError, _("Invalid boolean literal (%s)") % xmlValue

    def validate(self, value, eb, ctx):
        return 1

class TypeInfo_code(ITypeInfo):

    #def getDataType(self):
    #    return DTCode

    def py2xml(self, pyValue):
        return pyValue

    def xml2py(self, xmlValue):
        return xmlValue

    def validate(self, value, eb, ctx):
        # TBC: pluggable code validator
        return 1

    # specifics

    def __init__(self,codeName):
        self.__codeName = codeName

    def getCodeName(self):
        return self.__codeName

class TypeInfo_datetime(ITypeInfo):

    #def getDataType(self):
    #    return DTDatetime

    def py2xml(self, pyValue):
        if type(pyValue) is datetime.datetime:
            if pyValue.utcoffset() is None:
                return pyValue.isoformat()+"Z"
            return pyValue.isoformat()
        elif type(pyValue) is MxDateTimeType:
            return MxDateTimeToISO(pyValue)
        else:
            return pyValue.ISO(canonical)

    def xml2py(self, xmlValue):
        return DateTimeFromISO(xmlValue)

    def validate(self, value, eb, ctx):
        return 1

class TypeInfo_date(ITypeInfo):

    #def getDataType(self):
    #    return DTDate

    def py2xml(self, pyValue):
        if type(pyValue) is datetime.date:
            return pyValue.isoformat()
        elif type(pyValue) is MxDateType:
            return MxDateToISO(pyValue)
        else:
            return pyValue.ISO(canonical)

    def xml2py(self, xmlValue):
        return DateFromISO(xmlValue)

    def validate(self, value, eb, ctx):
        return 1

class TypeInfo_time(ITypeInfo):

    #def getDataType(self):
    #    return DTTime

    def py2xml(self, pyValue):
        if type(pyValue) is datetime.time:
            if pyValue.utcoffset() is None:
                return pyValue.isoformat()+"Z"
            return pyValue.isoformat()
        elif type(pyValue) is MxTimeType:
            return MxTimeToISO(pyValue)
        else:
            return pyValue.ISO(canonical)

    def xml2py(self, xmlValue):
        return TimeFromISO(xmlValue)

    def validate(self, value, eb, ctx):
        return 1

class TypeInfo_string(ITypeInfo,_TypeInfo_choices):

    #def getDataType(self):
    #    return DTString

    def py2xml(self, pyValue):
        return pyValue

    def xml2py(self, xmlValue):
        return xmlValue

    def validate(self, value, eb, ctx):
        ok = self.validateChoices(value,eb,ctx)
        if len(value) < self.__minLen:
            eb.addError(_("The string is too short: Len(%s) < %d") % \
                        (value,self.__minLen),
                        ctx)
            ok = 0
        if self.__maxLen is not None and len(value) > self.__maxLen:
            eb.addError(_("The string is too long: Len(%s) > %d") % \
                        (value,self.__maxLen),
                        ctx)
            ok = 0
        if self.__regExp is not None:
            if self.__regExp.match(value) is None:
                eb.addError(_("The string (%s) does not match " \
                            "the expected pattern (%s)") % \
                            (value,self.__regExp.pattern),
                            ctx)
        return ok

    # specifics

    def __init__(self,minLen=1,maxLen=None,xmlRegExp=None):
        _TypeInfo_choices.__init__(self)
        self.__minLen = minLen
        self.__maxLen = maxLen
        if xmlRegExp is not None:
            self.__regExp = re.compile(xmlRegExp)
        else:
            self.__regExp = None

    def getMinLen(self):
        return self.__minLen

    def getMaxLen(self):
        return self.__maxLen

    def getRegExp(self):
        return self.__regExp # compiled

class TypeInfo_int(ITypeInfo,_TypeInfo_choices):

    #def getDataType(self):
    #    return DTInt

    def py2xml(self, pyValue):
        return "%ld" % pyValue

    def xml2py(self, xmlValue):
        return long(xmlValue)

    def validate(self, value, eb, ctx):
        ok = self.validateChoices(value,eb,ctx)
        if self.__minVal is not None and value < self.__minVal:
            eb.addError(_("The value is too small %s < %s") % \
                        (value,self.__minVal),
                        ctx)
            ok = 0
        if self.__maxVal is not None and value > self.__maxVal:
            eb.addError(_("The value is too large %s > %s") % \
                        (value,self.__maxVal),
                        ctx)
            ok = 0
        return ok

    # specifics

    def __init__(self,xmlMinVal=None,xmlMaxVal=None):
        _TypeInfo_choices.__init__(self)
        if xmlMinVal is not None:
            self.__minVal = self.xml2py(xmlMinVal)
        else:
            self.__minVal = None
        if xmlMaxVal is not None:
            self.__maxVal = self.xml2py(xmlMaxVal)
        else:
            self.__maxVal = None

    def getMinVal(self):
        return self.__minVal

    def getMaxVal(self):
        return self.__maxVal

class TypeInfo_decimal(ITypeInfo,_TypeInfo_choices):

    #def getDataType(self):
    #    return DTDecimal

    def py2xml(self, pyValue):
        return self.__format % pyValue

    def xml2py(self, xmlValue):
        if self.__pattern.match(xmlValue) is None:
            raise ValueError, _("invalid decimal literal or too many " \
                              "fraction digits (max %d): %s") % \
                              (self.__fractionDigits,xmlValue)
        return float(xmlValue)

    def validate(self, value, eb, ctx):
        ok = self.validateChoices(value,eb,ctx)
        # TBC: compare within precision
        if self.__minVal is not None and value < self.__minVal:
            eb.addError(_("The value is too small %s < %s") % \
                        (value,self.__minVal),
                        ctx)
            ok = 0
        if self.__maxVal is not None and value > self.__maxVal:
            eb.addError(_("The value is too large %s > %s") % \
                        (value,self.__maxVal),
                        ctx)
            ok = 0
        return ok

    # specifics

    def __init__(self,fractionDigits,xmlMinVal=None,xmlMaxVal=None):
        _TypeInfo_choices.__init__(self)
        self.__format = "%%.%df" % fractionDigits
        self.__fractionDigits = fractionDigits
        if not fractionDigits:
            self.__pattern = re.compile(r"\s*[-+]?[0-9]+\s*$")
        else:
            self.__pattern = re.compile(r"\s*[-+]?[0-9]+(\.[0-9]{1,%d})?\s*$" % fractionDigits)
        if xmlMinVal is not None:
            self.__minVal = self.xml2py(xmlMinVal)
        else:
            self.__minVal = None
        if xmlMaxVal is not None:
            self.__maxVal = self.xml2py(xmlMaxVal)
        else:
            self.__maxVal = None

    def getMinVal(self):
        return self.__minVal

    def getMaxVal(self):
        return self.__maxVal

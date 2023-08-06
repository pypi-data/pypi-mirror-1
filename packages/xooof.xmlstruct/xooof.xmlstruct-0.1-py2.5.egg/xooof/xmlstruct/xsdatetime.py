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


""" XMLStruct classes for date/time handling

    These are built on top of the basic DateTime[Delta] types and
    include rudimentary time zone handling through an offset in
    minutes. It is the applications responsibility to set the offset
    to correct values. The offsets are then used in date calculations.

"""

from mx import DateTime
_DateTime = DateTime
del DateTime
import xsiso

useNativePython=False

class _EmptyClass: pass

MxDateTimeType = type(_DateTime.DateTime(0))

def DateTimeFromMxDateTime(mxDateTime):
    d = DateTime()
    d.data = mxDateTime
    return d

def DateTimeFromISO(isostring):
    if not useNativePython:
        data,offset = xsiso.ParseDateTimeTZ(isostring)
        o = _EmptyClass()
        o.__class__ = DateTime
        o.data = data
        o.offset = offset.minutes
        return o
    else:
        return xsiso.parseDateTime(isostring)


def MxDateTimeToISO(datetime,offset=0):
    if offset == 0:
        return '%04i-%02i-%02iT%02i:%02i:%02iZ' % (
               datetime.year, datetime.month, datetime.day,
               datetime.hour, datetime.minute, datetime.second)
    else:
        tz = offset * _DateTime.oneMinute
        return '%04i-%02i-%02iT%02i:%02i:%02i%+03i:%02i' % (
              datetime.year, datetime.month, datetime.day,
              datetime.hour, datetime.minute, datetime.second,
              tz.hour,tz.minute)

class DateTime:

    def __init__(self,*args):
        self.offset = _DateTime.now().gmtoffset().minutes
        if len(args):
            self.data = apply(_DateTime.DateTime,args)
        else:
            self.data = _DateTime.now()

    def __getattr__(self,what):
        if what != "data":
            return getattr(self.data,what)
        else:
            raise AttributeError("data")

    def __deepcopy__(self,memo=None):
        c = _EmptyClass()
        c.__class__ = self.__class__
        c.data = self.data
        c.offset = self.offset
        return c

    __copy__ = __deepcopy__

    def set_timezone(self,offset):
        self.offset = offset

    def __sub__(self,other):
        if isinstance(other,DateTime):
            if self.offset != other.offset:
                # Be careful about different offsets:
                d = (self.data - self.offset * _DateTime.oneMinute) \
                    - (other.data - other.offset * _DateTime.oneMinute)
            else:
                # Offsets are equal: no adjustment needed
                d = self.data - other.data
            o = _EmptyClass()
            o.__class__ = Interval
            o.data = d
            return o
        elif isinstance(other,Interval):
            d = self.data - other.data
            o = _EmptyClass()
            o.__class__ = DateTime
            o.data = d
            o.offset = self.offset # inherit the offset
            return o
        else:
            raise TypeError,"operation not supported"

    def __add__(self,other):
        if isinstance(other,Time):
            if other.offset != self.offset:
                raise TypeError,"operation not supported because offsets are !="
            d = self.data + other.data
            o = _EmptyClass()
            o.__class__ = DateTime
            o.data = d
            o.offset = self.offset # inherit the offset
            return o
        elif isinstance(other,Interval):
            d = self.data + other.data
            o = _EmptyClass()
            o.__class__ = DateTime
            o.data = d
            o.offset = self.offset # inherit the offset
            return o
        else:
            raise TypeError,"operation not supported"

    def ISO(self,canonical=0):
        datetime = self.data
        offset = self.offset
        if canonical and offset != 0:
            datetime = datetime - offset * _DateTime.oneMinute
            offset = 0
        return MxDateTimeToISO(datetime,offset)

    def __str__(self):
        return self.ISO()

    def __repr__(self):
        return '<DateTime object for "%s" at %x>' % (str(self.data),id(self))

    def _toUTC(self):
        return self.data - self.offset * _DateTime.oneMinute

    def __cmp__(self,other):
        if isinstance(other,DateTime):
            return cmp(self._toUTC(),other._toUTC())
        else:
            return -1

MxDateType = type(_DateTime.DateTime(0))

def DateFromMxDate(mxDate):
    d = Date()
    d.data = mxDateTime
    return d

def DateFromISO(isostring):
    if not useNativePython:
        data = xsiso.ParseDate(isostring)
        o = _EmptyClass()
        o.__class__ = Date
        o.data = data
        o.offset = 0
        return o
    else:
        return xsiso.parseDateTime(isostring).date()

def MxDateToISO(datetime):
    return '%04i-%02i-%02i' % (datetime.year, datetime.month, datetime.day)

class Date(DateTime):

    def ISO(self,canonical=0):
        return MxDateToISO(self.data)

    def __str__(self):
        return self.ISO()

    def __repr__(self):
        return '<Date object for "%s" at %x>' % (str(self.data),id(self))

    def __cmp__(self,other):
        if isinstance(other,DateTime):
            return cmp(self._toUTC(),other._toUTC())
        else:
            return -1

MxTimeType = type(_DateTime.DateTimeDelta(0))

def TimeFromISO(isostring):
    if not useNativePython:
        data,offset = xsiso.ParseTimeTZ(isostring)
        o = _EmptyClass()
        o.__class__ = Time
        o.data = data
        o.offset = offset.minutes
        return o
    else:
        return xsiso.parseTime(isostring)

def MxTimeToISO(datetime,offset=0):
    if offset == 0:
        return '%02i:%02i:%02iZ' % (
               datetime.hour, datetime.minute, datetime.second)
    else:
        tz = offset*_DateTime.oneMinute
        return '%02i:%02i:%02i%+03i:%02i' % (
               datetime.hour, datetime.minute, datetime.second,
               tz.hour,tz.minute)

class Time:

    def __init__(self,*args):
        # the offset is meaningful only in combination with a full date
        self.offset = _DateTime.now().gmtoffset().minutes
        if len(args):
            self.data = apply(_DateTime.TimeDelta,args)
        else:
            self.data = _DateTime.TimeDelta()

    def __getattr__(self,what):
        if what != "data":
            return getattr(self.data,what)
        else:
            raise AttributeError("data")

    def __deepcopy__(self,memo=None):
        c = _EmptyClass()
        c.__class__ = self.__class__
        c.data = self.data
        c.offset = self.offset
        return c

    __copy__ = __deepcopy__

    def __sub__(self,other):
        if isinstance(other,Time):
            if other.offset != self.offset:
                raise TypeError,"operation not supported because offsets are !="
            d = self.data - other.data
            o = _EmptyClass()
            o.__class__ = Interval
            o.data = d
            return o
        elif isinstance(other,Interval):
            d = self.data - other.data
            o = _EmptyClass()
            o.__class__ = Time
            o.data = d
            return o
        else:
            raise TypeError,"operation not supported"

    def __add__(self,other):
        if isinstance(other,Time):
            if other.offset != self.offset:
                raise TypeError,"operation not supported because offsets are !="
            d = self.data + other.data
            o = _EmptyClass()
            o.__class__ = Interval
            o.data = d
            o.offset = self.offset
            return o
        elif isinstance(other,Interval):
            d = self.data + other.data
            o = _EmptyClass()
            o.__class__ = Time
            o.data = d
            o.offset = self.offset
            return o
        else:
            raise TypeError,"operation not supported"

    def ISO(self,canonical=0):
        if canonical and self.offset != 0:
            datetime = self._toUTC()
            offset = 0
        else:
            datetime = self.data
            offset = self.offset
        return MxTimeToISO(datetime,offset)

    def __str__(self):
        return self.ISO()

    def __repr__(self):
        return '<Time object for "%s" at %x>' % (str(self.data),id(self))

    def _toUTC(self):
        r = self.data - self.offset * _DateTime.oneMinute
        if r < 0:
            r += _DateTime.oneDay
        return r

    def __cmp__(self,other):
        if isinstance(other,Time):
            return cmp(self._toUTC(),other._toUTC())
        else:
            return -1

class Interval:

    def __init__(self,*args):
        self.data = apply(_DateTime.DateTimeDelta,args)

    def __getattr__(self,what):
        if what != "data":
            return getattr(self.data,what)
        else:
            raise AttributeError("data")

    def __deepcopy__(self,memo=None):
        c = _EmptyClass()
        c.__class__ = self.__class__
        c.data = self.data
        return c

    __copy__ = __deepcopy__

    def __sub__(self,other):
        if isinstance(other,Interval):
            d = self.data - other.data
            o = _EmptyClass()
            o.__class__ = Interval
            o.data = d
            return o
        else:
            raise TypeError,"operation not supported"

    def __add__(self,other):
        if isinstance(other,Interval):
            d = self.data + other.data
            o = _EmptyClass()
            o.__class__ = Interval
            o.data = d
            return o
        else:
            raise TypeError,"operation not supported"

    def __mul__(self,other):
        value = float(other)
        d = value * self.data
        o = _EmptyClass()
        o.__class__ = Interval
        o.data = d
        return o
    __rmul__ = __mul__

    def __div__(self,other):
        value = float(other)
        d = self.data / value
        o = _EmptyClass()
        o.__class__ = Interval
        o.data = d
        return o

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return '<Interval object for "%s" at %x>' % (str(self.data),id(self))

if __name__ == '__main__':
    d = Date()
    print d, d.offset
    print d.ISO()
    d2 = DateFromISO(d.ISO())
    print d2, d2.offset
    print

    dt = DateTime()
    print dt, dt.offset
    print dt.ISO()
    print dt.ISO(canonical=1)
    dt2 = DateTimeFromISO(dt.ISO())
    print dt2, dt2.offset
    print

    t = Time()
    print t, t.offset
    print t.ISO()
    t2 = TimeFromISO(t.ISO())
    print t2, t2.offset
    print

    print TimeFromISO("10:01:02")
    print DateTimeFromISO("2001-08-27 10:01:02+01:30")

    d = DateTime(2002,1,1)
    t = Time(10,11,12)
    print d,t,d+t

    assert dt == dt
    assert t == t
    assert d == d
    assert dt != None
    assert t != None
    assert d != None

    import cPickle, os
    cPickle.dump([DateTime(),Time(),Interval(1)],open("test.dat","wb"))
    l = cPickle.load(open("test.dat","rb"))
    print l
    print map(lambda e: e.data,l)
    os.remove("test.dat")

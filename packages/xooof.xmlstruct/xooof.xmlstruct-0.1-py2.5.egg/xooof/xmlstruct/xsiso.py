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


from mx.DateTime.ISO import *

from translations import _

import datetime

# This module is highly dependent on the implementation of mx.DateTime.ISO!
# It provides ParseDateTimeTZ and ParseTimeTZ, that are created
# by cloning ParseDateTime and ParseTime and returning the timezone offset
# instead of simply ignoring it.
#
# TBC: suggest this to Marc-Andre Lemburg for inclusion in the ISO submodule.

def ParseDateTimeTZ(isostring,parse_isodatetime=isodatetimeRE.match,

                    strip=string.strip,atoi=string.atoi,atof=string.atof):

    s = strip(isostring)
    date = parse_isodatetime(s)
    if not date:
        raise ValueError,_('wrong format, use YYYY-MM-DD HH:MM:SS')
    year,month,day,hour,minute,second,zone = date.groups()
    year = atoi(year)
    if month is None:
        month = 1
    else:
        month = atoi(month)
    if day is None:
        day = 1
    else:
        day = atoi(day)
    if hour is None:
        hour = 0
    else:
        hour = atoi(hour)
    if minute is None:
        minute = 0
    else:
        minute = atoi(minute)
    if second is None:
        second = 0.0
    else:
        second = atof(second)
    offset = Timezone.utc_offset(zone)
    return DateTime.DateTime(year,month,day,hour,minute,second),offset

def ParseTimeTZ(isostring,parse_isotime=isotimeRE.match,

                strip=string.strip,atoi=string.atoi,atof=string.atof):

    s = strip(isostring)
    time = parse_isotime(s)
    if not time:
        raise ValueError,_('wrong format, use HH:MM:SS')
    hour,minute,second,zone = time.groups()
    hour = atoi(hour)
    minute = atoi(minute)
    if second is not None:
        second = atof(second)
    else:
        second = 0.0
    offset = Timezone.utc_offset(zone)
    return DateTime.TimeDelta(hour,minute,second),offset


date_parser = re.compile(r"""^
    (?P<year>\d{4,4})
    (?:
        -
        (?P<month>\d{1,2})
        (?:
            -
            (?P<day>\d{1,2})
            (?:
                T
                (?P<hour>\d{1,2})
                :
                (?P<minute>\d{1,2})
                (?:
                    :
                    (?P<second>\d{1,2})
                    (?:
                        \.
                        (?P<dec_second>\d+)?
                    )?
                )?
                (?:
                    Z
                    |
                    (?:
                        (?P<tz_sign>[+-])
                        (?P<tz_hour>\d{1,2})
                        :
                        (?P<tz_min>\d{2,2})
                    )
                )?
            )?
        )?
    )?
$""", re.VERBOSE)

time_parser = re.compile(r"""^
                (?P<hour>\d{1,2})
                :
                (?P<minute>\d{1,2})
                (?:
                    :
                    (?P<second>\d{1,2})
                    (?:
                        \.
                        (?P<dec_second>\d+)?
                    )?
                )?
                (?:
                    Z
                    |
                    (?:
                        (?P<tz_sign>[+-])
                        (?P<tz_hour>\d{1,2})
                        :
                        (?P<tz_min>\d{2,2})
                    )
                )?
$""", re.VERBOSE)
def parseDateTime(isostring):
    """ parse a string and return a datetime object. """
    assert isinstance(isostring, basestring)
    r = date_parser.search(isostring)
    try:
        a = r.groupdict('0')
    except:
        raise ValueError,_('wrong format, use YYYY-MM-DD HH:MM:SS')
    dt = datetime.datetime(int(a['year']),
                           int(a['month']) or 1,
                           int(a['day']) or 1,
                           # If not given these will default to 00:00:00.0
                           int(a['hour']),
                           int(a['minute']),
                           int(a['second']),
                           # skip dec_second
                           #int(a['dec_second'])*100000,
                           )
    tz_hours_offset = int(a['tz_hour'])
    tz_mins_offset = int(a['tz_min'])
    if a.get('tz_sign', '+') == "-":
        return dt + datetime.timedelta(hours = tz_hours_offset,
                                       minutes = tz_mins_offset)
    else:
        return dt - datetime.timedelta(hours = tz_hours_offset,
                                       minutes = tz_mins_offset)

def parseTime(isostring):
    """ parse a string and return a time object. """
    assert isinstance(isostring, basestring)
    r = time_parser.search(isostring)
    try:
        a = r.groupdict('0')
    except:
        raise ValueError,_('wrong format, use HH:MM:SS')
    dt = datetime.datetime( 1900,
                           1,
                           1,
                           int(a['hour']),
                           int(a['minute']),
                           int(a['second']),
                           # skip dec_second
                           #int(a['dec_second'])*100000,
                           )
    tz_hours_offset = int(a['tz_hour'])
    tz_mins_offset = int(a['tz_min'])
    if a.get('tz_sign', '+') == "-":
        return (dt + time.timedelta(hours = tz_hours_offset,
                                minutes = tz_mins_offset)).time()
    else:
        return (dt - datetime.timedelta(hours = tz_hours_offset,
                                     minutes = tz_mins_offset)).time()

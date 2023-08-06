#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
Some utilities, fixed for vice.

>>> from vice.zope2.outbound.utils import DT2dt, dt2DT
>>> from DateTime import DateTime
>>> from datetime import datetime

>>> DT = DateTime('1997/3/9 13:45:00 US/Eastern')
>>> dt = DT2dt(DT)
>>> DT_alt = dt2DT(dt)
>>> DT_alt == DT
True

>>> from vice.zope2.outbound.utils import RFC3339
>>> RFC3339(DT)
'1997-03-09T18:45:00Z'

"""

import datetime
from DateTime import DateTime

# Thanks trac
class FixedOffset(datetime.tzinfo):
    """Fixed offset in minutes east from UTC."""
    def __init__(self, offset, name):
        self._offset = datetime.timedelta(minutes=offset)
        self._name = name
    def utcoffset(self, dt):
        return self._offset
    def tzname(self, dt):
        return self._name
    def dst(self, dt):
        return datetime.timedelta(minutes=0)

def dt2DT(date):
    """Convert Python's datetime to Zope's DateTime
    """
    args = (date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond, date.tzinfo)
    timezone = args[7].utcoffset(date)
    secs = timezone.seconds
    days = timezone.days
    hours = secs/3600 + days*24
    mod = "+"
    if hours < 0:
        mod = ""
    timezone = "GMT%s%d" % (mod, hours)
    args = list(args[:6])
    args.append(timezone)
    return DateTime(*args)

def DT2dt(date):
    """Convert Zope's DateTime to Pythons's datetime
    """
    # seconds (parts[6]) is a float, so we map to int
    args = map(int, date.parts()[:6])
    args.append(0)
    args.append(FixedOffset(int(date.tzoffset()/60), date.timezone()))
    return datetime.datetime(*args)

def RFC3339(date):
    """ Get the RFC3339 rep of the date. Expects a zope2 DateTime. """
    try:
        date = date.toZone("UTC")
        date = DT2dt(date)
    except NameError:
        date = datetime(*date.utctimetuple()[:6])
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')
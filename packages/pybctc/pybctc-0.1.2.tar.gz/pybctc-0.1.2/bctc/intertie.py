#~ pybctc is a python package that makes access to British
#~ Columbia[, Canada,] Transmission Corporation (BCTC) electric data
#~ easier.

#~ Copyright (C) 2009, 2010 Keegan Callin

#~ This program is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.

#~ This program is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.

#~ You should have received a copy of the GNU General Public License
#~ along with this program.  If not, see
#~ <http://www.gnu.org/licenses/gpl-3.0.html>.

'''
Tools for parsing intertie flow historical reports posted at
<http://www.bctc.com/transmission_system/actual_flow_data/historical_data.htm> (2010-02-08).
'''

# Standard library imports
import unittest
import os
from datetime import datetime
from datetime import timedelta
import urllib2

# 3rd party libraries
import xlrd
import pytz

# Custom libraries
from bctc import BC_TZ
from bctc._util import dump_to_mkstemp
from bctc._util import open_workbook
from bctc._util import YearBookManager
from bctc._util import BctcDtNormalizer


# Please leave the commented out urls here.  They are old versions of
# BCTC files that contain errors.
#~ URL_1999_TO_2003 = 'http://www.bctc.com/NR/rdonlyres/D31D28D9-23BE-4BB1-A4AB-7B9449FD7EA0/0/Hourly_Tielines_19992003.xls'
#~ URL_1999_TO_2003 = 'http://www.bctc.com/NR/rdonlyres/D31D28D9-23BE-4BB1-A4AB-7B9449FD7EA0/0/9903HourlyTielines.xls'
URL_1999_TO_2003 = 'http://www.bctc.com/NR/rdonlyres/D31D28D9-23BE-4BB1-A4AB-7B9449FD7EA0/0/9903HourlyTielines.xls' # 2010-03-01
URL_2004 = 'http://www.bctc.com/NR/rdonlyres/2C126A86-DA34-4A3C-8C06-0A80A3D76CAF/0/jandec2004tielinedata.xls'
URL_2005 = 'http://www.bctc.com/NR/rdonlyres/7ED7ED16-0977-432F-B9AD-21B664FE1E1A/0/jan05to31dect05hrlytielinedatapostingtowebsite.xls'
#~ URL_2006 = 'http://www.bctc.com/NR/rdonlyres/007F81EC-E339-4EBD-8F93-FAA42F3A1777/0/jan06to31december06hrlytielinedatapostingtowebsite.xls'
URL_2006 = 'http://www.bctc.com/NR/rdonlyres/DEA3BC36-D20A-4DA2-9EFB-353EE5629008/0/2006hrlytielinedata.xls'
URL_2007 = 'http://www.bctc.com/NR/rdonlyres/8AB9D0C8-55D0-4076-83E7-1D9166046D60/0/2007hrlytielinedatapostingtowebsite.xls'
#~ URL_2008 = 'http://www.bctc.com/NR/rdonlyres/71FD3459-2AA3-4A1E-B221-F7C764D01F96/0/2008hrlytielinedata.xls'
#~ URL_2008 = 'http://www.bctc.com/NR/rdonlyres/0A2C638C-87DA-4D57-A7AE-1B4CD62386BB/0/2008hrlytielinedata.xls'
URL_2008 = 'http://www.bctc.com/NR/rdonlyres/0A2C638C-87DA-4D57-A7AE-1B4CD62386BB/0/2008hrlytielinedata.xls' # 2010-03-01
URL_2009 = 'http://www.bctc.com/NR/rdonlyres/86B3BEBF-B6F2-4E50-9C63-CC42836992BF/0/jandec2009hrlytielinedata.xls'
#URL_2010 = 'http://www.bctc.com/NR/rdonlyres/3BF88803-D760-463C-9562-248B3E42C9BB/0/jan2010hrlytielinedata.xls'
URL_2010 = 'http://www.bctc.com/NR/rdonlyres/3BF88803-D760-463C-9562-248B3E42C9BB/0/janfeb2010hrlytielinedata.xls' # 2010-03-01

URLMAP = {
    1999 : URL_1999_TO_2003,
    2000 : URL_1999_TO_2003,
    2001 : URL_1999_TO_2003,
    2002 : URL_1999_TO_2003,
    2003 : URL_1999_TO_2003,
    2004 : URL_2004,
    2005 : URL_2005,
    2006 : URL_2006,
    2007 : URL_2007,
    2008 : URL_2008,
    2009 : URL_2009,
    2010 : URL_2010,
}

class IntertieBookManager(YearBookManager):
    '''A cache manager that dynamically downloads historical flow data
    from 1999 onwards.  The managed hourly report files are those at
    <http://www.bctc.com/transmission_system/actual_flow_data/historical_data.htm> (2010-02-23).'''

    def __init__(self):
        super(type(self), self).__init__(URLMAP)


class IntertieFlowPoint(object):
    '''Object representing intertie flows at a given point in time.
    The object is iterable so that it can be unpacked::

        >>> from datetime import datetime
        >>> import pytz
        >>> point = IntertieFlowPoint(pytz.utc.localize(datetime(2001, 1, 1)), 12, 57)
        >>> t, us, ab = point
        >>> assert t == point.t
        >>> assert us == point.us
        >>> assert ab == point.ab

    :param t: UTC :class:`datetime.datetime`
    :param us: int
    :param ab: int
    '''

    def __init__(self, t, us, ab):
        self._t = t
        self._us = us
        self._ab = ab
        self._iterable = (self.t, self.us, self.ab)

    @property
    def t(self):
        ''':rtype: UTC offset-aware :class:`datetime.datetime`'''
        return self._t

    @property
    def us(self):
        '''Flow to US in MW.

        :rtype: int'''
        return self._us

    @property
    def ab(self):
        '''Flow to Alberta in MW.

        :rtype: int'''
        return self._ab

    def __iter__(self):
        return iter(self._iterable)


def parse_intertie_xlrd_book(book):
    '''Yields :class:`IntertieFlowPoint` objects extracted from open
    Excel :mod:`xlrd` *book*.'''
    sheet = book.sheets()[0]

    dt_normalizer = BctcDtNormalizer()
    num_extracted_rows = 0
    for row in xrange(0, sheet.nrows):
        cell_date, cell_hour, cell_us, cell_ab = sheet.cell(row, 0), sheet.cell(row, 1), sheet.cell(row, 2), sheet.cell(row, 3)

        if cell_date.ctype != xlrd.XL_CELL_DATE:
            if num_extracted_rows == 0:
                continue
            else:
                raise TypeError('Expected date ctype')

        # Prepare flow data
        us = int(cell_us.value)
        ab = int(cell_ab.value)

        if us == 0 and ab == 0:
            # This row contains no data; it is a placeholder for the
            # missing hour when DST begins.  The row looks something
            # like this:
            #
            # 99 Apr 04, 3, 0, 0
            #
            # Zero US and AB flows are the only indication that the
            # row is null-data.
            continue

        # Prepare UTC time stamp
        hour = int(cell_hour.value)
        date_tuple = xlrd.xldate_as_tuple(cell_date.value, book.datemode)
        try:
            dt = dt_normalizer.normalize(date_tuple[0:3], hour)
        except ValueError:
            year = date_tuple[0]
            month = date_tuple [1]

            if year == 2008 and month == 2:
                # February 2008 BCTC data is corrupted by bad hour information.
                continue
                # raise KnownBctcError('February 2008 BCTC data is corrupted by bad hour information.')
            else:
                raise

        dt = dt.astimezone(pytz.utc)

        yield IntertieFlowPoint(dt, us, ab)


def parse_intertie_xls_file(f):
    '''Yields :class:`IntertieFlowPoint` objects extracted from Excel
    file *f*.  File *f* may be either a file-like object or a string
    containing the path to an Excel file.'''
    book = open_workbook(f)
    for p in parse_intertie_xlrd_book(book):
        yield p



def yield_intertie_flows(start_dt = pytz.utc.localize(datetime(1999, 1, 1)), end_dt = pytz.utc.localize(datetime.today() + timedelta(1)), manager = IntertieBookManager()):
    '''Yields hourly historical :class:`IntertieFlowPoint` objects with
    time *t* such that *start_dt* <= *t* < *end_dt*.  By default all
    available data is returned.  A *manager* object, if provided, gives
    advanced users the ability to use previously cached files to save
    download time.

    :param start_dt: offset-aware :class:`datetime.datetime`; typically
                     like ``pytz.utc.localize(datetime(1999, 1, 1))``
    :param end_dt: offset-aware :class:`datetime.datetime`; typically
                   like
                   ``pytz.utc.localize(datetime.today() + timedelta(1))``
    :param manager: :class:`YearBookManager` instance like
                    :class:`IntertieBookManager`\(\)

    Example Usage::
        >>> from bctc.intertie import IntertieFlowPoint, yield_intertie_flows
        >>> from datetime import datetime
        >>> import pytz
        >>>
        >>> # list of all available data points
        >>> points = list(yield_intertie_flows())
        >>> assert len(points) > 10000
        >>>
        >>> # Create a list of all data for 2007 and use a manager
        >>> # object to cache downloaded data for later usage.
        >>> manager = IntertieBookManager()
        >>> start_dt = pytz.utc.localize(datetime(2007, 1, 1))
        >>> end_dt = pytz.utc.localize(datetime(2008, 1, 1))
        >>> points_2007 = list(yield_intertie_flows(start_dt, end_dt, manager = manager))
        >>> assert len(points_2007) > 10000
        >>>
        >>> # Create a new list of 2007 and 2008 points re-using the
        >>> # 2007 data already stored by *manager* to save time.
        >>> points_2007_and_2008 = list(yield_intertie_flows(start_dt, end_dt, manager = manager))
        >>> assert len(points_2007_and_2008) > 10000
    '''

    start_dt = start_dt.astimezone(pytz.utc)
    end_dt = end_dt.astimezone(pytz.utc)

    start_year = start_dt.year
    end_year = start_dt.year

    min_year = min(manager.years)
    max_year = max(manager.years)

    if end_year < min_year:
        return

    if start_year > max_year:
        return

    if start_year < min_year:
        start_year = min_year

    if end_year > max_year:
        end_year = max_year

    for year in xrange(start_year, end_year + 1):
        fn = manager.filename(year)
        for p in parse_intertie_xls_file(fn):
            if start_dt <= p.t < end_dt:
                yield p



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
Tools for parsing control area load historical reports posted at
<http://www.bctc.com/transmission_system/balancing_authority_load_data/historical_transmission_data.htm> (2010-02-08).
'''

from datetime import datetime
from datetime import timedelta

# 3rd party imports
import xlrd
import pytz

# Custom libraries
from bctc import BC_TZ
from bctc._util import dump_to_mkstemp
from bctc._util import open_workbook
from bctc._util import BctcDtNormalizer
from bctc._util import YearBookManager


URL_2001_TO_2003 = 'http://www.bctc.com/NR/rdonlyres/837CF09D-0730-40D8-A2D6-745CD9937A27/0/BCCALoad01April2001to31Dec2003.xls'
URLMAP = {
    2001 : URL_2001_TO_2003,
    2002 : URL_2001_TO_2003,
    2003 : URL_2001_TO_2003,
    2004 : 'http://www.bctc.com/NR/rdonlyres/ABD25491-A560-49F4-AC6F-64924D2DF025/0/2004controlareaload.xls',
    2005 : 'http://www.bctc.com/NR/rdonlyres/4A26DAD4-E8A8-41C6-9335-77A44B0E75F1/0/2005controlareaload.xls',
    2006 : 'http://www.bctc.com/NR/rdonlyres/C4BF362C-B661-4D8D-8FB5-0AF88DD7FFC3/0/2006controlareaload.xls',
    2007 : 'http://www.bctc.com/NR/rdonlyres/C6E06392-7235-4F39-ADCD-D58A70D493C7/0/2007controlareaload.xls',
    2008 : 'http://www.bctc.com/NR/rdonlyres/AB10E645-DC79-42BC-8620-046A245A44EE/0/2008controlareaload.xls',
    2009 : 'http://www.bctc.com/NR/rdonlyres/7386D585-BE05-494F-A377-D846D2A8C486/0/jandec2009controlareaload.xls',
    #~ 2010 : 'http://www.bctc.com/NR/rdonlyres/0A1D85D8-C257-4268-BC4A-46B0174AB9D3/0/jan2010controlareaload.xls',
    2010 : 'http://www.bctc.com/NR/rdonlyres/0A1D85D8-C257-4268-BC4A-46B0174AB9D3/0/janfeb2010controlareaload.xls', # 2010-03-02
}


class LoadBookManager(YearBookManager):
    '''A cache manager that dynamically downloads historical load data
    from 2001 onwards.  The managed hourly report files are those at
    <http://www.bctc.com/transmission_system/balancing_authority_load_data/historical_transmission_data.htm> (2010-02-23).'''
    def __init__(self):
        super(type(self), self).__init__(URLMAP)


class LoadPoint(object):
    '''Object representing load at a given point in time.  The object
    is iterable so that it can be unpacked::

        >>> from datetime import datetime
        >>> import pytz
        >>> point = LoadPoint(pytz.utc.localize(datetime(2001, 1, 1)), 1000)
        >>> t, load = point
        >>> assert t == point.t
        >>> assert load = point.load

    :param t: UTC :class:`datetime.datetime`
    :param load: int
    '''

    def __init__(self, t, load):
        self._t = t
        self._load = load
        self._iterable = (self.t, self.load)

    @property
    def t(self):
        ''':rtype: UTC offset-aware :class:`datetime.datetime`'''
        return self._t

    @property
    def load(self):
        '''Load in MW.

        :rtype: int'''
        return self._load

    def __iter__(self):
        return iter(self._iterable)


def parse_load_xlrd_book(book):
    '''Yields :class:`LoadPoint` objects extracted from open Excel
    :mod:`xlrd` *book*.'''
    sheet = book.sheets()[0]

    dt_normalizer = BctcDtNormalizer()
    num_extracted_rows = 0
    for row in xrange(0, sheet.nrows):
        try:
            cell_date, cell_hour, cell_load, cell_tz = sheet.cell(row, 0), sheet.cell(row, 1), sheet.cell(row, 2), sheet.cell(row, 3)
            tz = cell_tz.value
        except IndexError:
            cell_date, cell_hour, cell_load = sheet.cell(row, 0), sheet.cell(row, 1), sheet.cell(row, 2)
            tz = ''

        try:
            if cell_date.ctype != xlrd.XL_CELL_DATE:
                raise TypeError('Expected date ctype')
            num_extracted_rows += 1
        except TypeError:
            if num_extracted_rows == 0:
                continue
            else:
                raise

        hour = int(cell_hour.value)
        load = int(cell_load.value)
        if tz == 'PST' or load == 0:
            # This cell contains no data; it is a placeholder for the
            # missing hour when DST begins.  The row looks something
            # like this:
            #
            # 01 Apr 01, 3, 0, PST
            #
            # At other times in the same report, the "PST" marker is
            # ommitted like this:
            #
            # 01 Apr 01, 3, 0
            #
            # And this leaves a zero load as the only indication that
            # the row is null-data.
            continue

        date_tuple = xlrd.xldate_as_tuple(cell_date.value, book.datemode)
        dt = dt_normalizer.normalize(date_tuple[0:3], hour)
        dt = dt.astimezone(pytz.utc)
        yield LoadPoint(dt, load)


def parse_load_xls_file(f):
    '''Yields :class:`LoadPoint` objects extracted from Excel file *f*.
    File *f* may be either a file-like object or a string containing
    the path to an Excel file.'''

    book = open_workbook(f)
    for p in parse_load_xlrd_book(book):
        yield p


def yield_load_points(start_dt = pytz.utc.localize(datetime(2001, 1, 1)), end_dt = pytz.utc.localize(datetime.today() + timedelta(1)), manager = LoadBookManager()):
    '''Yields control area :class:`LoadPoint` objects with time *t*
    such that  *start_dt* <= *t* < *end_dt*.  By default all available
    data is returned.  A *manager* object, if provided, gives advanced
    users the ability to use previously cached files to save download
    time.

    :param start_dt: offset-aware :class:`datetime.datetime`; typically like
                     ``pytz.utc.localize(datetime(2001, 1, 1))``
    :param end_dt: offset-aware :class:`datetime.datetime`; typically like
                   ``pytz.utc.localize(datetime.today() + timedelta(1))``
    :param manager: :class:`YearBookManager` instance like :class:`LoadBookManager`\(\)

    Example Usage::
        >>> from bctc.load import LoadBookManager, yield_load_points
        >>> from datetime import datetime
        >>> import pytz
        >>>
        >>> # list of all available data points
        >>> points = list(yield_load_points())
        >>> assert len(points) > 10000
        >>>
        >>> # Create a list of all data for 2007 and use a manager
        >>> # object to cache downloaded data for later usage.
        >>> manager = LoadBookManager()
        >>> start_dt = pytz.utc.localize(datetime(2007, 1, 1))
        >>> end_dt = pytz.utc.localize(datetime(2008, 1, 1))
        >>> points_2007 = list(yield_load_points(start_dt, end_dt, manager = manager))
        >>> assert len(points_2007) > 10000
        >>>
        >>> # Create a new list of 2007 and 2008 points re-using the
        >>> # 2007 data already stored by *manager* to save time.
        >>> points_2007_and_2008 = list(yield_load_points(start_dt, end_dt, manager = manager))
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
        for point in parse_load_xls_file(fn):
            if start_dt <= point.t < end_dt:
                yield point

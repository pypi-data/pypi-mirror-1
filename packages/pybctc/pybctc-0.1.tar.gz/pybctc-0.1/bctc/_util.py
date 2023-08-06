# Standard library imports
from shutil import copyfileobj
from tempfile import mkstemp
from datetime import datetime
from datetime import timedelta
import os
import urllib2
from StringIO import StringIO
import sha

# 3rd party libraries
import xlrd
import pytz

# Custom libraries
from bctc import BC_TZ


def path_sha1(fn):
    f = open(fn)
    text = f.read()
    f.close()

    h = sha.new()
    h.update(text)
    return h.hexdigest()


def dump_to_mkstemp(src):
    fd, name = mkstemp()
    os.close(fd)

    dst = open(name, 'wb')
    copyfileobj(src, dst)
    dst.close()

    return name


def open_workbook(f):
    if isinstance(f, str):
        # *f* is a string.
        book = xlrd.open_workbook(f)
    else:
        # *f* is a file object
        xls_filename = dump_to_mkstemp(f)
        book = xlrd.open_workbook(xls_filename)
        os.remove(xls_filename)

    return book


def create_naive_dt(date_tuple, hour):
    year = date_tuple[0]
    month = date_tuple[1]
    day = date_tuple[2]

    add_one_day = False
    try:
        naive_datetime = datetime(year, month, day, hour, 0, 0)
    except ValueError:
        if hour == 24:
            naive_datetime = datetime(year, month, day, 0, 0, 0)
            add_one_day = True
        else:
            raise

    if add_one_day:
        naive_datetime += timedelta(1)

    return naive_datetime


def stringio_url(url):
    '''Write contents of *url* to a StringIO object then return that object.'''

    f = urllib2.urlopen(url)
    buff = StringIO()
    copyfileobj(f, buff)
    buff.seek(0)
    return buff


def dt_range(start_dt, end_dt, increment, include = False):
    dt = start_dt

    if start_dt <= end_dt:
        if include:
            while dt <= end_dt:
                yield dt
                dt += increment
        else:
            while dt < end_dt:
                yield dt
                dt += increment
    else:
        if include:
            while dt >= end_dt:
                yield dt
                dt += increment
        else:
            while dt > end_dt:
                yield dt
                dt += increment


class BctcDtNormalizer(object):
    def __init__(self):
        self._ambiguous_time_count = 0


    def normalize(self, date_tuple, hour):
        naive_datetime = create_naive_dt(date_tuple, hour)

        try:
            if self._ambiguous_time_count == 1 and naive_datetime.hour == 2:
                # At the end of DST, BCTC Load spreadsheets count hours:
                # 24 1 2 2 3 4
                #
                # There normally is only one "2am" because the clock
                # transitions from 1:59 to 1:00 and NOT 2:59 to 2:00.
                #
                # This block detects the first "2" and converts it to
                #
                # 0100 is_dst = False
                naive_datetime = datetime(naive_datetime.year, naive_datetime.month, naive_datetime.day, 1, naive_datetime.minute, naive_datetime.second)
                localized = BC_TZ.localize(naive_datetime, is_dst = False)
            else:
                localized = BC_TZ.localize(naive_datetime, is_dst = None)

            self._ambiguous_time_count = 0
        except pytz.AmbiguousTimeError:
            self._ambiguous_time_count += 1
            if hour == 1:
                # At the end of DST, BCTC Load spreadsheets count hours:
                # 24 1 2 2 3 4
                #
                # There normally is only one "2am" because the clock
                # transitions from 1:59 to 1:00 and NOT 2:59 to 2:00.
                #
                # Because of this, 1 can confidently be labeled as before
                # the DST transition.
                localized = BC_TZ.localize(naive_datetime, is_dst = True)
            else:
                raise
        except pytz.NonExistentTimeError, e:
            # On the day DST begins, normally hour transitions:
            # 0 1 3
            #
            # But BCTC hours are counted:
            # 0 1 2 (3) 4
            #
            # Three is in parenthesis because the hour line exists but is
            # zeroed.
            #
            if naive_datetime.hour == 2:
                naive_datetime = datetime(naive_datetime.year, naive_datetime.month, naive_datetime.day, 3, naive_datetime.minute, naive_datetime.second)
                localized = BC_TZ.localize(naive_datetime, is_dst = True)
            else:
                raise

        return localized


class YearBookManager(object):
    __remove_file = os.remove # Trickery to help with __del__

    def __init__(self, year_to_url_map):
        self._urlmap = year_to_url_map
        self._filenamemap = {}
        self._bookmap = {}
        self._urls = set(self._urlmap.values())

        minimum_yearmap = {}
        for year, url in year_to_url_map.items():
            minimum_yearmap[url] = year
        self._minimum_years = set(minimum_yearmap.values())


    def __del__(self):
        for fn in self._filenamemap.values():
            # Must use this method because os.remove may not be
            # accessible at this point
            #
            # See
            # http://docs.python.org/reference/datamodel.html#object.__del__
            #
            type(self).__remove_file(fn)


    def book(self, year):
        try:
            return self._bookmap[year]
        except KeyError:
            book = open_workbook(self.filename(year))
            self._bookmap[year] = book
            return book


    def filename(self, year):
        try:
            return self._filenamemap[year]
        except KeyError:
            f = urllib2.urlopen(self.url(year))
            filename = dump_to_mkstemp(f)
            f.close()

            self._filenamemap[year] = filename
            return filename


    def url(self, year):
        return self._urlmap[year]


    @property
    def years(self):
        return self._urlmap.keys()


    @property
    def minimum_years(self):
        return self._minimum_years


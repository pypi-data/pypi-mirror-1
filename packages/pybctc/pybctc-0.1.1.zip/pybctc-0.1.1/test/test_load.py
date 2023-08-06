import unittest
from os.path import join
from os.path import dirname
from datetime import datetime, timedelta
from pprint import pprint
import sha
from bz2 import BZ2File
from itertools import chain
from urllib2 import urlopen

# 3rd party libraries
import pytz

# Custom libraries
from bctc.load import parse_load_xls_file
from bctc.load import yield_load_points
from bctc.load import LoadBookManager
import bctc
from bctc import BC_TZ
from swissarmyknife import path_sha1
from swissarmyknife import dt_range
from swissarmyknife import pprint_url_hashes
from swissarmyknife import extract_hrefs

from bctc._util import BctcDtNormalizer
class TestBctcDtNormalizer(unittest.TestCase):
    def test_pytz_bctz(self):
        t = BC_TZ.localize(datetime(2001, 4, 1, 1))
        t = t.astimezone(pytz.utc)

        i = 0
        while i < 10:
            #~ print t.astimezone(BC_TZ)
            t += timedelta(0, 60*60)
            i += 1


class TestPytz(unittest.TestCase):
    def test_search_ambiguity(self):
        ab_tz = pytz.timezone('America/Edmonton')
        ambiguous_dates = []
        nonexistent_dates = []

        dt = datetime(2000, 1, 1, 0)
        while dt.year < 2002:
            try:
                ab_tz.localize(dt, is_dst = None)
            except pytz.AmbiguousTimeError:
                ambiguous_dates.append(dt)
            except pytz.NonExistentTimeError:
                nonexistent_dates.append(dt)

            dt += timedelta(0, 60*60)

        self.assertTrue(ambiguous_dates)
        self.assertTrue(nonexistent_dates)


    def test_eastern_tz(self):
        '''Testing code snippet from http://pytz.sourceforge.net.

        >>> eastern.localize(datetime(2002, 10, 27, 1, 30, 00), is_dst=None)
        ...
        AmbiguousTimeError: 2002-10-27 01:30:00
        '''
        eastern = pytz.timezone('US/Eastern')
        self.assertRaises(pytz.AmbiguousTimeError, eastern.localize, datetime(2002, 10, 27, 1, 30, 0), is_dst=None)
        self.assertRaises(pytz.AmbiguousTimeError, eastern.localize, datetime(2002, 10, 27, 1, 0, 0), is_dst=None)


    def test_ambiguity(self):
        dt = datetime(2009, 11, 1, 1, 0, 0)
        self.assertRaises(pytz.AmbiguousTimeError, BC_TZ.localize, dt, is_dst = None)


URL_HASHES = {
    'http://www.bctc.com/NR/rdonlyres/0A1D85D8-C257-4268-BC4A-46B0174AB9D3/0/jan2010controlareaload.xls': '7f1d6789f9e77e808f906c8273061b02ed97b228',
    'http://www.bctc.com/NR/rdonlyres/4A26DAD4-E8A8-41C6-9335-77A44B0E75F1/0/2005controlareaload.xls': '84341986454763410ec46e040df20778e9e1760b',
    'http://www.bctc.com/NR/rdonlyres/7386D585-BE05-494F-A377-D846D2A8C486/0/jandec2009controlareaload.xls': '74d90124e26d917c4bb42ba2f0adda17eccad15f',
    'http://www.bctc.com/NR/rdonlyres/837CF09D-0730-40D8-A2D6-745CD9937A27/0/BCCALoad01April2001to31Dec2003.xls': 'e4d081e851acc10dfcf0eae7761d4dd148b0f879',
    'http://www.bctc.com/NR/rdonlyres/AB10E645-DC79-42BC-8620-046A245A44EE/0/2008controlareaload.xls': 'd8db80edcc6cd6428ac139f9f5dca347e9d55d0c',
    'http://www.bctc.com/NR/rdonlyres/ABD25491-A560-49F4-AC6F-64924D2DF025/0/2004controlareaload.xls': '43dc0910c509bff1a365a645d93dced5a7f6fca6',
    'http://www.bctc.com/NR/rdonlyres/C4BF362C-B661-4D8D-8FB5-0AF88DD7FFC3/0/2006controlareaload.xls': 'a4ce762a7312a994c40ae55962e1dfee505d1bee',
    'http://www.bctc.com/NR/rdonlyres/C6E06392-7235-4F39-ADCD-D58A70D493C7/0/2007controlareaload.xls': '7389fc7adf8f29a06ab172a6fcc0a56ed28fa50d',
}


EXPECTED_2008HRLYTIELINEDATA_DATES = [
    (datetime(2001, 4, 1, 1), datetime(2001, 4, 3, 2)),
    (datetime(2001, 4, 30, 1), datetime(2001, 5, 3, 16)),
    (datetime(2001, 10, 26, 8), datetime(2002, 1, 1, 15)),
]
def build_expected_time_it():
    iters = []

    for start_dt, end_dt in EXPECTED_2008HRLYTIELINEDATA_DATES:
        start_dt = BC_TZ.localize(start_dt).astimezone(pytz.utc)
        end_dt = BC_TZ.localize(end_dt).astimezone(pytz.utc)

        iters.append(dt_range(start_dt, end_dt, timedelta(0, 60*60), include = True))

    return chain(*iters)


class TestLoadParsing(unittest.TestCase):
    def test_parse_load_xls_file(self):
        #~ testfile_path = join(dirname(__file__), 'res', 'BCCALoad01April2001to31Dec2003.xls')
        #~ f = open(testfile_path)
        testfile_path = join(dirname(__file__), 'res', 'BCCALoad01April2001to31Dec2003.xls.bz2')
        f = BZ2File(testfile_path)

        times = build_expected_time_it()
        for lp in parse_load_xls_file(f):
            expected_t = times.next()
            self.assertEquals(lp.t, expected_t)
        f.close()


class TestLoadWebservice(unittest.TestCase):
    @property
    def manager(self):
        if not hasattr(self, '_manager'):
            self._manager = LoadBookManager()

        return self._manager


    def assertYearUrlUnchanged(self, year):
        fn = self.manager.filename(year)
        digest = path_sha1(fn)
        url = self.manager.url(year)
        self.assertEquals(URL_HASHES[url], digest)


    def assert_load_xls_is_sane(self, fn, comment = ''):
        expected_dt = None
        num_rows = 0
        for actual_dt, load in parse_load_xls_file(fn):
            self.assertTrue(type(actual_dt) == datetime)
            self.assertTrue(type(load) == int)

            num_rows += 1
            if expected_dt is None:
                # Choose starting expected_dt from first actual_dt
                # value.
                expected_dt = actual_dt
            actual_bc = actual_dt.astimezone(BC_TZ)
            expected_bc = expected_dt.astimezone(BC_TZ)
            self.assertEquals(actual_bc, expected_bc, str(actual_bc) + ' != expected ' + str(expected_bc) + ', load=' + str(load))
            expected_dt += timedelta(0, 60*60)

        self.assertTrue(num_rows)


    def test_yield_load_points(self):
        num_rows = 0
        for dt, load in yield_load_points(manager = self.manager):
            num_rows += 1

        self.assertTrue(num_rows > 10000)

    def test_hrefs(self):
        load_link_page = 'http://www.bctc.com/transmission_system/balancing_authority_load_data/historical_transmission_data.htm'
        f = urlopen(load_link_page)
        text = f.read()
        f.close()

        hrefs = extract_hrefs(text)
        for url in LoadBookManager().urls:
            hint = '.com'
            path = url[url.index(hint)+len(hint):]
            self.assertTrue(path in hrefs, 'Missing expected url ' + path)


# Some metaprogramming to insert test cases to TestLoadWebservice
# for each year
def build_year_parse_xls_testcase(year):
    def test_year_parse_xls(self):
        fn = self.manager.filename(year)
        self.assert_load_xls_is_sane(fn)

    return test_year_parse_xls


def build_year_url_unchanged_testcase(year):
    def test_year_url_unchanged(self):
        self.assertYearUrlUnchanged(year)

    return test_year_url_unchanged


for year in LoadBookManager().minimum_years:
    setattr(TestLoadWebservice, 'test_' + str(year) + '_load_xls_parse', build_year_parse_xls_testcase(year))
    setattr(TestLoadWebservice, 'test_' + str(year) + '_load_url_unchanged', build_year_url_unchanged_testcase(year))


if __name__ == '__main__':
    #~ pprint_url_hashes(LoadBookManager())
    unittest.main()

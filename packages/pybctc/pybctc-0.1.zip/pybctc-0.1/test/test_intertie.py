import unittest
from os.path import join
from os.path import isfile
from os.path import exists
from os.path import dirname
from datetime import datetime
from datetime import timedelta
from bz2 import BZ2File
from pprint import pprint
from itertools import chain

# 3rd party libraries
import pytz

# Custom libraries
import bctc.intertie
from bctc.intertie import parse_intertie_xls_file
from bctc.intertie import yield_intertie_flows
from bctc.intertie import IntertieBookManager
from bctc import BC_TZ
from bctc._util import stringio_url
from bctc._util import path_sha1
from bctc._util import dt_range


def is_bctc_problem_date(dt):
    if dt.year == 2008 and dt.month == 2 and dt.day < 29:
        return True
    else:
        return False


class TestIntertieAssertions(unittest.TestCase):
    def assert_load_xls_is_sane(self, fn, comment = ''):
        expected_dt = None
        num_rows = 0
        for actual_dt, us, ab in parse_intertie_xls_file(fn):
            num_rows += 1
            if expected_dt is None:
                # Choose starting expected_dt from first actual_dt
                # value.
                expected_dt = actual_dt
            actual_bc = actual_dt.astimezone(bctc.BC_TZ)
            expected_bc = expected_dt.astimezone(bctc.BC_TZ)
            self.assertEquals(actual_bc, expected_bc, str(actual_bc) + ' != expected ' + str(expected_bc) + ', us=' + str(us) + ' us=' + str(ab))
            expected_dt += timedelta(0, 60*60)

        self.assertTrue(num_rows)


EXPECTED_2008HRLYTIELINEDATA_DATES = [
    (datetime(2008, 1, 1, 1), datetime(2008, 1, 13, 23)),
    (datetime(2008, 1, 29, 3), datetime(2008, 2, 1, 0)),
    (datetime(2008, 2, 29, 18), datetime(2008, 4, 1, 23)),
    (datetime(2008, 4, 3, 0), datetime(2008, 4, 3, 0)),  # Aberration caused by bad underlying data
    (datetime(2008, 4, 2, 1), datetime(2008, 4, 2, 22)),
    (datetime(2008, 4, 3, 23), datetime(2008, 4, 4, 0)),
    (datetime(2008, 4, 3, 1), datetime(2008, 4, 3, 19)),
    (datetime(2008, 10, 21, 17), datetime(2008, 11, 7, 10)),
    (datetime(2008, 11, 30, 13), datetime(2008, 12, 1, 18)),
    (datetime(2008, 12, 30, 18), datetime(2009, 1, 1, 0)),
]
def build_expected_time_it():
    iters = []

    for start_dt, end_dt in EXPECTED_2008HRLYTIELINEDATA_DATES:
        start_dt = BC_TZ.localize(start_dt).astimezone(pytz.utc)
        end_dt = BC_TZ.localize(end_dt).astimezone(pytz.utc)

        iters.append(dt_range(start_dt, end_dt, timedelta(0, 60*60), include = True))

    return chain(*iters)


class TestIntertieFuncs(TestIntertieAssertions):
    def setUp(self):
        self._res_dir = join(dirname(__file__), 'res')


    def localize(self, year, month, day, hour, is_dst = None):
        naive_datetime = datetime(year, month, day, hour, 0, 0)
        return BC_TZ.localize(naive_datetime, is_dst = is_dst)


    def test_2001_10_28_01(self):
        self.assertRaises(pytz.AmbiguousTimeError, self.localize, 2001, 10, 28, 1)
        self.localize(2001, 10, 28, 1, True)
        self.localize(2001, 10, 28, 1, False)


    def test_2001_10_28_02(self):
        self.localize(2001, 10, 28, 2)
        self.localize(2001, 10, 28, 2, True)
        self.localize(2001, 10, 28, 2, False)


    def test_parse_intertie_xls_file(self):
        testfile_path = join(dirname(__file__), 'res', '2008hrlytielinedata.xls.bz2')
        f = BZ2File(testfile_path)

        num_rows = 0
        times = build_expected_time_it()
        for lp in parse_intertie_xls_file(f):
            expected_t = times.next()
            self.assertEquals(lp.t, expected_t)
            num_rows += 1

        self.assertEquals(num_rows, 1669 - 7)
        f.close()


URL_HASHES = {
    'http://www.bctc.com/NR/rdonlyres/007F81EC-E339-4EBD-8F93-FAA42F3A1777/0/jan06to31december06hrlytielinedatapostingtowebsite.xls': '6804080f586e0233265fe1a6e42de323a2279912',
    'http://www.bctc.com/NR/rdonlyres/2C126A86-DA34-4A3C-8C06-0A80A3D76CAF/0/jandec2004tielinedata.xls': '62228a3560c6ce37255201c2bd6086c111b3e09f',
    'http://www.bctc.com/NR/rdonlyres/3BF88803-D760-463C-9562-248B3E42C9BB/0/jan2010hrlytielinedata.xls': '9b4860fd342d4da2c7cedd9f0fe489869fffb1d2',
    'http://www.bctc.com/NR/rdonlyres/71FD3459-2AA3-4A1E-B221-F7C764D01F96/0/2008hrlytielinedata.xls': '8fed2d16f3191b45661ad8b481799c3b7f475463',
    'http://www.bctc.com/NR/rdonlyres/7ED7ED16-0977-432F-B9AD-21B664FE1E1A/0/jan05to31dect05hrlytielinedatapostingtowebsite.xls': '6b8cc5c3ffadcb8dc2536c7845fd3e8e80e365be',
    'http://www.bctc.com/NR/rdonlyres/86B3BEBF-B6F2-4E50-9C63-CC42836992BF/0/jandec2009hrlytielinedata.xls': '42053be84a9a4fa1c15e10636b692d560c7c2120',
    'http://www.bctc.com/NR/rdonlyres/8AB9D0C8-55D0-4076-83E7-1D9166046D60/0/2007hrlytielinedatapostingtowebsite.xls': '81f076ce9000bbaa7c84423137f40c84399ad12d',
    'http://www.bctc.com/NR/rdonlyres/D31D28D9-23BE-4BB1-A4AB-7B9449FD7EA0/0/Hourly_Tielines_19992003.xls': '367990a22e14ae868747e77cf8b1a781cfc3cd5e',
}


def pprint_url_hashes(manager = bctc.intertie.IntertieBookManager()):
    url_hash_lut = {}
    for year in manager.minimum_years:
        fn = manager.filename(year)
        digest = path_sha1(fn)
        url = manager.url(year)

        # Can use pprint to print table to update URL_HASHES
        url_hash_lut[url] = digest
    pprint(url_hash_lut)


class TestIntertieWebservice(TestIntertieAssertions):
    @property
    def manager(self):
        if not hasattr(self, '_manager'):
            self._manager = bctc.intertie.IntertieBookManager()

        return self._manager


    def assertYearUrlUnchanged(self, year):
        fn = self.manager.filename(year)
        digest = path_sha1(fn)
        url = self.manager.url(year)
        self.assertEquals(URL_HASHES[url], digest)


    def test_yield_intertie_flows(self):
        num_rows = 0
        for dt, us, ab in yield_intertie_flows(manager = self.manager):
            num_rows += 1

        self.assertTrue(num_rows > 10000)


# Some metaprogramming to insert test cases to TestIntertieWebservice
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


for year in bctc.intertie.IntertieBookManager().minimum_years:
    setattr(TestIntertieWebservice, 'test_' + str(year) + '_intertie_xls_parse', build_year_parse_xls_testcase(year))
    setattr(TestIntertieWebservice, 'test_' + str(year) + '_intertie_url_unchanged', build_year_url_unchanged_testcase(year))


if __name__ == '__main__':
    unittest.main()

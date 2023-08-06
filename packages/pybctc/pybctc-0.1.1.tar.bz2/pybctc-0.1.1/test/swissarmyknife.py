from StringIO import StringIO
import sha
import urllib2
from shutil import copyfileobj
from pprint import pprint
import re

def stringio_url(url):
    '''Write contents of *url* to a StringIO object then return that object.'''

    f = urllib2.urlopen(url)
    buff = StringIO()
    copyfileobj(f, buff)
    buff.seek(0)
    return buff


def path_sha1(fn):
    f = open(fn)
    text = f.read()
    f.close()

    h = sha.new()
    h.update(text)
    return h.hexdigest()


def pprint_url_hashes(manager):
    url_hash_lut = {}
    for year in manager.minimum_years:
        fn = manager.filename(year)
        digest = path_sha1(fn)
        url = manager.url(year)

        # Can use pprint to print table to update URL_HASHES
        url_hash_lut[url] = digest
    pprint(url_hash_lut)


def extract_hrefs(string):
    hrefs = []
    pattern = re.compile('href="(.*?)"')
    for match in pattern.finditer(string, re.DOTALL):
        hrefs.append(match.group(1))

    return hrefs


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

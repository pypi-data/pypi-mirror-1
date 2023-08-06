# Standard library imports
import unittest
from optparse import OptionParser
import sys

# Testable libraries
import test_intertie
import test_load
import test_examples

loader = unittest.TestLoader()
suites = [
    loader.loadTestsFromTestCase(test_intertie.TestIntertieWebservice),
    loader.loadTestsFromTestCase(test_load.TestLoadWebservice),
    loader.loadTestsFromModule(test_examples),
]
remote_suite = unittest.TestSuite(suites)


suites = [
    loader.loadTestsFromTestCase(test_intertie.TestIntertieFuncs),
    loader.loadTestsFromTestCase(test_load.TestPytz),
    loader.loadTestsFromTestCase(test_load.TestBctcDtNormalizer),
    loader.loadTestsFromTestCase(test_load.TestLoadParsing),
]
local_suite = unittest.TestSuite(suites)


suites = [
    local_suite,
    remote_suite
]
comprehensive_suite = unittest.TestSuite(suites)


def main(argv):
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("--verbosity", type="int", dest="verbosity", default = 1)
    parser.add_option("--with-remote", action="store_true", dest="remote", default=False)

    (opts, args) = parser.parse_args()
    #~ if len(args) != 1:
        #~ parser.error("incorrect number of arguments")

    suite = local_suite
    if opts.remote:
        suite = comprehensive_suite
    result = unittest.TextTestRunner(verbosity=opts.verbosity).run(suite)

    if result.wasSuccessful():
        rc = 0
    else:
        rc = 1

    return rc



if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
    #unittest.TextTestRunner().run(suite)

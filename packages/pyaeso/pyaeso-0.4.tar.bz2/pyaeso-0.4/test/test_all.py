# Standard library imports
import unittest
from optparse import OptionParser
import sys

# Testable libraries
import test_examples
import test_ets
import test_marginal_pool_price

loader = unittest.TestLoader()
suites = [
    loader.loadTestsFromModule(test_examples),
    loader.loadTestsFromTestCase(test_marginal_pool_price.TestMarginalPoolPriceServiceBehaviour),
    loader.loadTestsFromModule(test_ets.TestLiveEtsConnection),
]
remote_suite = unittest.TestSuite(suites)


suites = [
    loader.loadTestsFromTestCase(test_marginal_pool_price.TestMarginalPoolPrice),
    loader.loadTestsFromTestCase(test_ets.TestDayBlockIt),
    loader.loadTestsFromTestCase(test_ets.TestPoolPrice),
    loader.loadTestsFromTestCase(test_ets.TestAssetList),
    loader.loadTestsFromTestCase(test_ets.TestAtcLimits),
]
local_suite = unittest.TestSuite(suites)


suites = [
    loader.loadTestsFromModule(test_ets),
    loader.loadTestsFromModule(test_marginal_pool_price),
    loader.loadTestsFromModule(test_examples),
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

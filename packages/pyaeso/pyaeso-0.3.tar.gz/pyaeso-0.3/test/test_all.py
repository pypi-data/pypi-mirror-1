# Standard library imports
import unittest

# Testable libraries
import test_examples
import test_ets

loader = unittest.TestLoader()
module_suites = [
    loader.loadTestsFromModule(test_ets),
    loader.loadTestsFromModule(test_examples),
]
suite = unittest.TestSuite(module_suites)

if __name__ == '__main__':
    #unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.TextTestRunner().run(suite)

# python import
import unittest

# tools import
from twisting.tests import test_base_worker

def suite():
    suite = unittest.TestSuite()
    suite.addTest(test_base_worker.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

import unittest

from tests import resources

def suite():
    _suite = unittest.TestSuite()
    _suite.addTest(resources.suite)
    return _suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')


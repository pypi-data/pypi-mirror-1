import doctest
import unittest
import virtualkeyring

def test_suite():
    doctest.testmod(virtualkeyring)
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(virtualkeyring))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(test_suite())

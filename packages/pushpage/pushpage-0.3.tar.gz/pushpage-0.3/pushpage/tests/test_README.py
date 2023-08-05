import unittest

from zope.testing.doctest import DocFileTest

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(DocFileTest('../README.txt'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

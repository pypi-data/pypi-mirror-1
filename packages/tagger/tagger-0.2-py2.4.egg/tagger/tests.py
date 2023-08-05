import os, sys, unittest, doctest
try:
    from zope.testing import doctest
except ImportError:
    pass

flags = doctest.ELLIPSIS | doctest.REPORT_ONLY_FIRST_FAILURE

def test_suite():
    return doctest.DocFileSuite('README.txt', optionflags=flags)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())

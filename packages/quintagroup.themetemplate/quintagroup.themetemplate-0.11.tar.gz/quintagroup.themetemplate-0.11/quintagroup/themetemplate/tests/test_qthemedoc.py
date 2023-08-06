# -*- coding: utf-8 -*-
"""
Grabs the tests in doctest
"""
__docformat__ = 'restructuredtext'

from zopeskel.tests.test_zopeskeldocs import *

current_dir = os.path.abspath(os.path.dirname(__file__))

def doc_suite(test_dir, setUp=testSetUp, tearDown=testTearDown, globs=None):
    """Returns a test suite, based on doctests found in /doctest."""
    suite = []
    if globs is None:
        globs = globals()

    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    package_dir = os.path.split(test_dir)[0]
    if package_dir not in sys.path:
        sys.path.append(package_dir)

    doctest_dir = package_dir

    # filtering files on extension
    docs = [os.path.join(doctest_dir, doc) for doc in
            os.listdir(doctest_dir) if doc.endswith('.txt')]

    for test in docs:
        suite.append(doctest.DocFileSuite(test, optionflags=flags, 
                                          globs=globs, setUp=setUp, 
                                          tearDown=tearDown,
                                          module_relative=False))

    return unittest.TestSuite(suite)


def test_suite():
    """returns the test suite"""
    suite = doc_suite(current_dir)
    suite.layer = ZopeSkelLayer
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


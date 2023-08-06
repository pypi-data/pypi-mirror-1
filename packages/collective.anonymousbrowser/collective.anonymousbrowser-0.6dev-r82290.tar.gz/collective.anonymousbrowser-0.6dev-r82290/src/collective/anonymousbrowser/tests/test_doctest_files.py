import unittest
import doctest
from doctest import DocFileSuite
from collective.anonymousbrowser.tests.utils import launch_servers, stop_servers

flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE)


def test_suite():
    tests = [\
             "browser.txt",
             "real.txt",
            ]
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(DocFileSuite(
            test,
            setUp = launch_servers,
            tearDown = stop_servers,
            globs = {
                'httpds' : [],
                'threads' : [],
            },
            optionflags = flags))
    return suite

if __name__ == '__main__':
    suite = unittest.TestSuite(test_suite())
    unittest.TextTestRunner().run(suite)




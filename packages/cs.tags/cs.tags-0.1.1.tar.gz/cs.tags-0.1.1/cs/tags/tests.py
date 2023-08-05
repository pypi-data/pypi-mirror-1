import unittest

from zope.testing.doctestunit import DocFileSuite
from zope.component import testing

import cs.tags

def setUp(test):
    testing.setUp(test)


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt', package='cs.tags', setUp=setUp, tearDown=testing.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

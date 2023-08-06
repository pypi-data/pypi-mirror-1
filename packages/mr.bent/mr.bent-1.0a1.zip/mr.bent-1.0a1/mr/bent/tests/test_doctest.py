from unittest import TestSuite
from zope.testing import doctest


optionflags = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return TestSuite((
        doctest.DocFileSuite('README.txt',
            package='mr.bent', optionflags=optionflags),
    ))


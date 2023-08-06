import unittest
from zope.testing import doctest
from Testing.ZopeTestCase import ZopeDocTestSuite

from Products.pluggablecatalog.tests import common
common.setupPloneSite()

from Products.PloneTestCase import PloneTestCase

optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)


def test_suite():
    return unittest.TestSuite(
        [ZopeDocTestSuite(module,
                          test_class=PloneTestCase.PloneTestCase,
                          optionflags=optionflags)
         for module in ('Products.pluggablecatalog.tool',)]
        )

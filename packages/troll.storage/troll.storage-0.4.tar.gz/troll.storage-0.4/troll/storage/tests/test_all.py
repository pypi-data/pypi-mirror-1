# -*- coding: utf-8 -*-

import unittest
from zope.component import testing
from zope.testing import doctestunit, doctest


import five.grok
import Products.Five
import troll.storage
import zope.annotation
from Products.Five import zcml


def setUp(test=None):
    testing.setUp(test)
    zcml.load_config('meta.zcml', package=Products.Five)
    zcml.load_config('configure.zcml', package=Products.Five)
    zcml.load_config('meta.zcml', package=five.grok)
    zcml.load_config('configure.zcml', package=five.grok)
    zcml.load_config('configure.zcml', package=zope.annotation)
    zcml.load_config('configure.zcml', package=troll.storage.tests)


def test_suite():
    return unittest.TestSuite([

        doctestunit.DocTestSuite(
            module='troll.storage.tests.annotation',
            setUp=setUp, tearDown=testing.tearDown),

        ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

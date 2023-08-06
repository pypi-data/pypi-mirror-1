# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import gocept.selenium.zope2
import gocept.selenium.tests.isolation
import Testing.ZopeTestCase

Testing.ZopeTestCase.installProduct('Five')


class Zope2Tests(gocept.selenium.tests.isolation.IsolationTests,
                 gocept.selenium.zope2.TestCase):
    pass


def test_suite():
    return unittest.makeSuite(Zope2Tests)

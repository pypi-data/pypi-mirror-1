# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import gocept.selenium.zope2
import gocept.selenium.tests.isolation
import Testing.ZopeTestCase
import Products.PloneTestCase.PloneTestCase


Products.PloneTestCase.PloneTestCase.setupPloneSite(id='plone')


class PloneTests(gocept.selenium.tests.isolation.IsolationTests,
                 gocept.selenium.plone.TestCase):

    def test_plone_login(self):
        sel = self.selenium
        sel.open('/plone')
        sel.type('name=__ac_name', 'portal_owner')
        sel.type('name=__ac_password', 'secret')
        sel.click('name=submit')
        sel.waitForPageToLoad()
        sel.assertTextPresent('Welcome! You are now logged in.')


def test_suite():
    return unittest.makeSuite(PloneTests)

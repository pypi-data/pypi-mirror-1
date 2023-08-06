# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from Products.PloneTestCase.layer import PloneSiteLayer
import Products.PloneTestCase.PloneTestCase
import gocept.selenium.base
import gocept.selenium.zope2

class TestCase(gocept.selenium.base.TestCase,
               Products.PloneTestCase.PloneTestCase.FunctionalTestCase):

    layer = gocept.selenium.zope2.Layer(PloneSiteLayer)

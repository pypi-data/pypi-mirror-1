# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.selenium.ztk
import pkg_resources
import zope.app.testing.functional

zcml_layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(
        'gocept.selenium.ztk.tests', 'ftesting.zcml'),
    __name__, __name__, allow_teardown=True)

selenium_layer = gocept.selenium.ztk.Layer(zcml_layer)


class TestCase(gocept.selenium.ztk.TestCase):

    layer = selenium_layer

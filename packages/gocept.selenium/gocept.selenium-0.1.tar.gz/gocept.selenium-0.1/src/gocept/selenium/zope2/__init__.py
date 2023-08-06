# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import Lifetime
import Testing.ZopeTestCase
import Testing.ZopeTestCase.utils
import gocept.selenium.base

try:
    # Zope 2 >= 2.11
    import Testing.ZopeTestCase.layer
    BASE_LAYERS = (Testing.ZopeTestCase.layer.ZopeLiteLayer, )
except ImportError:
    # Zope 2 < 2.11
    BASE_LAYERS = ()


class Layer(gocept.selenium.base.Layer):

    def setUp(self):
        # five threads
        self.host, self.port = Testing.ZopeTestCase.utils.startZServer(5)
        super(Layer, self).setUp()

    def tearDown(self):
        Lifetime.shutdown(0, fast=1)
        super(Layer, self).tearDown()

    def switch_db(self):
        # Nothing to do, we rely on ZopeLiteLayer et. al.
        pass


class TestCase(gocept.selenium.base.TestCase,
               Testing.ZopeTestCase.FunctionalTestCase):

    layer = Layer(*BASE_LAYERS)

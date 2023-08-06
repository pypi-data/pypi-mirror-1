# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.selenium.selenese
import selenium


class Layer(object):

    # XXX make configurable
    _server = 'localhost'
    _port = 4444
    _browser = '*firefox'

    # override in subclass
    host = None
    port = None

    __name__ = 'Layer'

    def __init__(self, *bases):
        self.__bases__ = bases

    def setUp(self):
        self.selenium = selenium.selenium(
            self._server, self._port, self._browser,
            'http://%s:%s/' % (self.host, self.port))
        self.selenium.start()

    def tearDown(self):
        self.selenium.stop()

    def switch_db(self):
        raise NotImplemented


class TestCase(object):

    def setUp(self):
        super(TestCase, self).setUp()
        self.layer.switch_db()
        self.selenium = gocept.selenium.selenese.Selenese(
            self.layer.selenium, self)

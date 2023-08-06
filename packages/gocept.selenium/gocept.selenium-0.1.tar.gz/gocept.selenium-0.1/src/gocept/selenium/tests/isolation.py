# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt


ENSURE_ORDER = False


class IsolationTests(object):

    def test_0_set(self):
        global ENSURE_ORDER
        self.selenium.open('http://%s/set.html' % self.selenium.server)
        self.selenium.open('http://%s/get.html' % self.selenium.server)
        self.selenium.assertBodyText('1')
        ENSURE_ORDER = True

    def test_1_get(self):
        global ENSURE_ORDER
        self.assertEquals(ENSURE_ORDER, True,
                          'Set test was not run before get test')
        self.selenium.open('http://%s/get.html' % self.selenium.server)
        self.selenium.assertNotBodyText('1')
        ENSURE_ORDER = False

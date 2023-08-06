# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.security.proxy


class Set(object):

    def __call__(self):
        c = zope.security.proxy.removeSecurityProxy(self.context)
        c.foo = 1
        return 'setting done'


class Get(object):

    def __call__(self):
        c = zope.security.proxy.removeSecurityProxy(self.context)
        return str(c.foo)

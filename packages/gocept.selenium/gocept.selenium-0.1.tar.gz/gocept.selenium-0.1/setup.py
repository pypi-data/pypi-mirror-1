# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
from setuptools import setup, find_packages


setup(
    name='gocept.selenium',
    version = '0.1',
    author='Wolfgang Schnerring',
    author_email='ws@gocept.com',
    description='zope.testing layer that integrates Selenium-RC',
    long_description = (
        open(os.path.join('src', 'gocept', 'selenium', 'README.txt')).read() +
        '\n\n' +
        open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL 2.1',
    namespace_packages=['gocept'],
    install_requires=[
        'selenium',
        'setuptools',
        ],
    extras_require=dict(
        ztk=['zope.app.server',
            'zope.app.testing',
            'zope.app.wsgi',
            'zope.server'],
        test_ztk=[
            'zope.app.appsetup',
            'zope.app.zcmlfiles',
            'zope.securitypolicy',
            'zope.testing >= 3.8.0',
            'zope.interface',
            'zope.schema',
            'ZODB3',
            ]),
)

# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: setup.py 5486 2007-12-19 10:03:02Z zagy $

import os.path

from setuptools import setup, find_packages


setup(
    name = 'gocept.form',
    version = "0.7.1",
    author = "Christian Zagrodnick",
    author_email = "cz@gocept.com",
    description = "Extensions for zope.formlib",
    long_description = file(os.path.join(os.path.dirname(__file__),
                                         'README.txt')).read(),
    license = "ZPL 2.1",
    url='http://pypi.python.org/pypi/gocept.form',

    packages = find_packages('src'),
    package_dir = {'': 'src'},

    include_package_data = True,
    zip_safe = False,

    namespace_packages = ['gocept'],
    install_requires = [
        'setuptools',
        'gocept.mochikit>=1.3.1',
        'zope.interface',
        'zope.component',
        'zope.contentprovider',
        'zope.viewlet',
        'zc.resourcelibrary',
    ],
    extras_require = dict(
        test=['zope.testing',
              'zope.testbrowser',
              'zope.app.testing',
              'zope.app.zcmlfiles',
             ],
        formlib=['zope.formlib',
                 'zope.app.pagetemplate',
                ],
        z3cform=['z3c.form',
                 'z3c.pagelet'
                ])
    )

# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: setup.py 5091 2007-08-22 14:25:17Z zagy $

import os.path

from setuptools import setup, find_packages


setup(
    name = 'gocept.form',
    version = "0.1",
    author = "Christian Zagrodnick",
    author_email = "cz@gocept.com",
    description = "Provides some extened form layout for zope.formlib",
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
        'zope.interface',
        'zope.component',
        'zope.formlib',
        'zope.app.pagetemplate',
    ],
    extras_require = {
        'test': ['zope.testing',
                 'zope.testbrowser',
                 'zope.app.testing',
                 'zope.app.zcmlfiles',
                ],
    },
    )

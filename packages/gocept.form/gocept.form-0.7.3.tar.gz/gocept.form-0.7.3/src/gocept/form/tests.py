# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: tests.py 5639 2008-03-27 09:59:57Z nilo $

import os
import unittest

from zope.testing import doctest

import zope.app.testing.functional


Layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'gocept.form.layer', allow_teardown=True)


def FunctionalDocFileSuite(*paths, **kw):
    try:
        layer = kw['layer']
    except KeyError:
        layer = Layer
    else:
        del kw['layer']
    kw['package'] = doctest._normalize_module(kw.get('package'))
    test = zope.app.testing.functional.FunctionalDocFileSuite(
        *paths, **kw)
    test.layer = layer
    return test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(FunctionalDocFileSuite(
        'base.txt', 'grouped.txt', 'destructive-action.txt', 
        'multiple-constraints.txt', 'jsvalidation.txt'))
    return suite

# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: tests.py 6166 2008-07-22 08:04:52Z sweh $

import os
import unittest

from zope.testing import doctest

import zope.app.testing.functional


Layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'gocept.sequence.layer')


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
    suite.addTest(FunctionalDocFileSuite('README.txt'))
    suite.addTest(FunctionalDocFileSuite('migration.txt'))
    return suite

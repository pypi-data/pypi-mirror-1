# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: tests.py 5130 2007-09-11 10:53:09Z zagy $

import os
import unittest

import zope.app.testing.functional


GoceptLxmlLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'GoceptLxmlLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    test = zope.app.testing.functional.FunctionalDocFileSuite('README.txt')
    test.layer = GoceptLxmlLayer
    suite.addTest(test)

    return suite

# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: tests.py 5415 2007-11-22 09:27:31Z nilo $

import unittest

from zope.testing import doctest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite('README.txt', optionflags=doctest.ELLIPSIS))
    return suite

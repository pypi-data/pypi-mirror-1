# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: tests.py 5728 2008-05-16 15:05:12Z sweh $

import unittest

from zope.testing import doctest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
                    'paypal.txt',
                    optionflags=doctest.ELLIPSIS))
    return suite

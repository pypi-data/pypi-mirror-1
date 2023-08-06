##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: test_layer.py 81572 2007-11-07 05:41:28Z srichter $
"""
import re
import unittest
from zope.testing import renormalizing
from zope.app.testing import functional

functional.defineLayer('TestLayer', 'ftesting.zcml')


def test_suite():
    suite = unittest.TestSuite()

    s = functional.FunctionalDocFileSuite(
        '../README.txt',
        checker = renormalizing.RENormalizing([
            (re.compile(r'httperror_seek_wrapper:', re.M), 'HTTPError:'),
            ])
        )
    s.layer = TestLayer
    suite.addTest(s)

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

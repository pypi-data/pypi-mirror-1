##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""listcontainer module test runner

$Id: tests.py 678 2005-02-22 21:49:28Z gary $
"""
import unittest
from zope.testing import doctest
from zope.app.testing import placelesssetup

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

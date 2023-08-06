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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
$Id: tests.py 84972 2008-03-27 17:52:53Z benji_york $
"""
import unittest

from zope.testing import doctest
from zope.app.testing import placelesssetup

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'search.txt',
            setUp=placelesssetup.setUp,
            tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
           ),
       ))

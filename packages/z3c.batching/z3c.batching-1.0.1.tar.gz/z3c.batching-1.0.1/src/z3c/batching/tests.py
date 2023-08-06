##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Tag test setup

$Id: tests.py 90992 2008-09-09 10:34:36Z fafhrd $
"""
__docformat__ = "reStructuredText"

import doctest, unittest


def test_suite():

    return unittest.TestSuite((
        doctest.DocFileSuite(
                'README.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))

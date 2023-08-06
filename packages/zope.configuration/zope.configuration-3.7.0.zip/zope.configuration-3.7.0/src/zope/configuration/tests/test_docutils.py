##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Doc Tests for for zope.configuration.docutils

$Id: test_docutils.py 106877 2009-12-22 15:11:04Z hannosch $
"""
import unittest
from zope.testing.doctest import DocTestSuite

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.configuration.docutils'),
        ))

if __name__ == '__main__': unittest.main()

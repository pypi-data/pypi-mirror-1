##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""LDAPAdapter tests

$Id: test_field.py 70248 2006-09-20 08:30:10Z dobe $
"""
__docformat__ = "reStructuredText"

import sys

import unittest

from zope.testing import doctest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../field.py'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

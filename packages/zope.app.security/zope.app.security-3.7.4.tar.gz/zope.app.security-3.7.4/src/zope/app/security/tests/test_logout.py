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
"""
$Id: test_logout.py 106800 2009-12-20 04:52:54Z fafhrd $
"""
import unittest
from zope.testing import doctest

def test_bbb_imports():
    """
    Let's check if original imports still work:

      >>> import zope.app.security as old
      >>> import zope.authentication.logout as new

      >>> old.NoLogout is new.NoLogout
      True

      >>> old.LogoutSupported is new.LogoutSupported
      True

    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))

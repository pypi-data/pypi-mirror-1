##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Test bbb imports for checkPrincipal

$Id: test_principal.py 106799 2009-12-20 04:50:49Z fafhrd $
"""
import unittest
from zope.testing import doctest

def test_bbb_imports():
    """
      >>> import zope.authentication.principal as new
      >>> import zope.app.security.principal as old
      >>> old.checkPrincipal is new.checkPrincipal
      True

    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))

##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Backward compatibility: code was moved to zope.security.protectclass.

$Id: protectclass.py 95310 2009-01-28 13:16:45Z brandon_rhodes $
"""
from zope.security.checker import defineChecker, getCheckerForInstancesOf
from zope.security.checker import Checker, CheckerPublic

from zope.security.protectclass import (protectName,
                                        protectSetAttribute,
                                        protectLikeUnto)

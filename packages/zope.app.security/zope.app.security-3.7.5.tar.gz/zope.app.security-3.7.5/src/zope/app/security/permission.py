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
"""Backward compatibility imports for zope.app.localpermission.

$Id: permission.py 98062 2009-03-13 23:49:38Z nadako $
"""
__docformat__ = 'restructuredtext'

# BBB: the functionality was moved to zope.app.localpermission
from zope.app.localpermission.permission import (
    NULL_ID,
    LocalPermission,
    setIdOnActivation,
    unsetIdOnDeactivation,
    )

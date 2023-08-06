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
"""Backward-compatibility imports for PrincipalSource and permission vocabularies.

$Id: vocabulary.py 97943 2009-03-12 00:38:29Z nadako $
"""

# BBB
from zope.security.permission import PermissionsVocabulary
from zope.security.permission import PermissionIdsVocabulary
from zope.authentication.principal import PrincipalSource

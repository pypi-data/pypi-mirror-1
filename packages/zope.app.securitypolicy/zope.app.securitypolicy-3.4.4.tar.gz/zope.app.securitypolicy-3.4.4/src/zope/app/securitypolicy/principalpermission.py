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
"""Mappings between principals and permissions, stored in an object locally.

$Id: principalpermission.py 80149 2007-09-26 22:00:18Z rogerineichen $
"""

import zope.deferredimport

zope.deferredimport.deprecated(
    "It has moved to zope.securitypolicy.principalpermission  This reference will be "
    "removed somedays",
    AnnotationPrincipalPermissionManager = 'zope.securitypolicy.principalpermission:AnnotationPrincipalPermissionManager',
    PrincipalPermissionManager = 'zope.securitypolicy.principalpermission:PrincipalPermissionManager',
    principalPermissionManager = 'zope.securitypolicy.principalpermission:principalPermissionManager',
    )

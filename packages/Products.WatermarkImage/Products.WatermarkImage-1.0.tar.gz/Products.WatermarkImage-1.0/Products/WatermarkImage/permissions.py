##############################################################################
#
# Copyright (c) 2008-2009 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Products.WatermarkImage permissions

$Id: permissions.py 1757 2009-05-07 10:20:09Z jens $
"""

import Products
from AccessControl import ModuleSecurityInfo
from AccessControl import Permissions
from AccessControl.Permission import _registeredPermissions
from AccessControl.Permission import pname
from Globals import ApplicationDefaultPermissions


security = ModuleSecurityInfo('Products.CMFCore.permissions')

security.declarePrivate('setDefaultRoles')
def setDefaultRoles(permission, roles):
    """ Sets the defaults roles for a permission.
    """ 
    registered = _registeredPermissions
    if not registered.has_key(permission):
        registered[permission] = 1
        Products.__ac_permissions__=(
            Products.__ac_permissions__+((permission,(),roles),))
        mangled = pname(permission)
        setattr(ApplicationDefaultPermissions, mangled, roles)

# Note that we can only use the default Zope roles in calls to
# setDefaultRoles().  The default Zope roles are:
# Anonymous, Manager, and Owner.

security.declarePublic('ViewOriginal')
ViewOriginal = 'WatermarkImage: View original'
setDefaultRoles(ViewOriginal, ('Manager',))

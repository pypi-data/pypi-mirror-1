# -*- coding: utf-8 -*-


# CMF imports
from Products.CMFCore.permissions import setDefaultRoles

# Archetypes imports
from Products.Archetypes.public import listTypes

# Products imports
from config import PROJECTNAME

TYPE_ROLES = ('Manager')

permissions = {}
def wireAddPermissions():
    """Creates a list of add permissions for all types in this project
    
    Must be called **after** all types are registered!
    """
    
    global permissions
    all_types = listTypes(PROJECTNAME)
    for atype in all_types:
        permission = "%s: Add %s" % (PROJECTNAME, atype['portal_type'])
        setDefaultRoles(permission, TYPE_ROLES)
        permissions[atype['portal_type']] = permission
    return permissions

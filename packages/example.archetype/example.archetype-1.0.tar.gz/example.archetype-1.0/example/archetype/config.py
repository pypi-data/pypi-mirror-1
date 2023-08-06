
# CMF and Archetypes imports
#from Products.CMFCore.permissions import setDefaultRoles
#from Products.Archetypes.atapi import listTypes

# Archetypes imports
from Products.Archetypes.atapi import DisplayList


PROJECTNAME = "example.archetype"

# To be used in the InstantMessage priority field definition
MESSAGE_PRIORITIES = DisplayList((
    ('high', 'High Priority'),
    ('normal', 'Normal Priority'),
    ('low', 'Low Priority'),
    ))


## Being generic by defining an "Add" permission
## for each content type in the product
#ADD_CONTENT_PERMISSIONS = {}
#types = listTypes(PROJECTNAME)
#for atype in  types:
    #permission = "%s: Add %s" % (PROJECTNAME, atype['portal_type'])
    #ADD_CONTENT_PERMISSIONS[atype['portal_type']] = permission

    ## Assign default roles for the permission
    #setDefaultRoles(permission, ('Owner', 'Manager',))

ADD_CONTENT_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'InstantMessage': 'example.archetype: Add InstantMessage',
}

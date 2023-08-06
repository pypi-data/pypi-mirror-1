from Products.CMFCore.permissions import setDefaultRoles
from Products.Archetypes.atapi import listTypes
from config import PROJECTNAME

# Add an Instant Message
EDIT_NORMATIVA_PERMISSION = 'DigestoContentTypes: Edit Normativa'
EDIT_NORMATIVA_METADATA_PERMISSION = 'DigestoContentTypes: Edit Normativa Metadata'

# Assign default roles
#setDefaultRoles(EDIT_NORMATIVA_PERMISSION, ('Owner', 'Manager',))
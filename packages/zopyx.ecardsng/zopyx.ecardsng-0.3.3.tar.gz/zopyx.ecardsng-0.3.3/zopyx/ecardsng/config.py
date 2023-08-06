"""Common configuration constants
"""

PROJECTNAME = 'zopyx.ecardsng'

ADD_PERMISSIONS = {
'ECardsSavedFolder' : 'Add ECards Saved Folder',
'ECardsFolder' : 'Add ECards Folder',
'ECard' : 'Add ECard',
}

from Products.CMFCore.permissions import setDefaultRoles

setDefaultRoles('Add ECard', ('Anonymous', 'Manager', 'Authenticated'))

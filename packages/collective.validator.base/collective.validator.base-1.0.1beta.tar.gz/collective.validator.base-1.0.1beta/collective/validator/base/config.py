from Products.CMFCore.permissions import setDefaultRoles
from Products.CMFCore.permissions import AddPortalContent


PROJECTNAME = 'collective.validator.base'
SKINS_DIR = 'skins'
TITLE = 'Validator Tool'
DESCRIPTION = 'Validator for Plone'

GLOBALS = globals()

DEFAULT_ADD_TOOL_PERMISSION = "Use Validator Tool"
USE_VALIDATION_PERMISSION = PROJECTNAME + ": Launch portal validation"

setDefaultRoles(DEFAULT_ADD_TOOL_PERMISSION, ('Manager', 'Owner',))
setDefaultRoles(USE_VALIDATION_PERMISSION, ('Manager',))

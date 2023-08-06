# -*- coding: utf-8 -*-

from Products.CMFCore.permissions import setDefaultRoles
from Products.Archetypes.atapi import listTypes
from config import PROJECTNAME
from Products.CMFCore.permissions import AddPortalContent

# Add permissions differ for each type, and are imported by __init__.initialize
# so don't change their names!

AddATReport = 'collective.validator.base: Add ATreport'


# Set up default roles for permissions

setDefaultRoles(AddATReport,('Manager',))

DEFAULT_ADD_CONTENT_PERMISSION = AddATReport
ADD_CONTENT_PERMISSIONS = {
    'ATReport'   : AddATReport ,}


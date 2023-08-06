# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr


def setupVarious(context):
    portal = context.getSite()
    if shasattr(portal, 'portal_validationtool'):
	pvt = getattr(portal,'portal_validationtool')
	pvt.unindexObject()
# -*- coding: utf-8 -*-

from zope import component
from Products.CMFCore.utils import getToolByName

def setupVarious(context):
    portal = context.getSite()
    
    if context.readDataFile('redturtle.smartlink_various.txt') is None: 
        return
    
    backupATLink(portal)

def backupATLink(portal):
    """Make a backup of ATLink before the types.xml step overwrite it"""
    portal_types = portal.portal_types
    try:
        oldevent_fti = getattr(portal_types, 'oldATLink')
    except AttributeError:
        oldevent_fti = None
    if oldevent_fti:
        print "Doing nothing: ATLink already disabled"
        return
    
    portal_types.manage_renameObject('Link', 'oldATLink')
    oldevent_fti = getattr(portal_types, 'oldATLink')
    
    oldevent_fti.global_allow = False
    print "Disabled Plone original ATLink"

    
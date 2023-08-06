# -*- coding: utf-8 -*-

from zope import component
from Products.CMFCore.utils import getToolByName

def setupVarious(context):
    portal = context.getSite()
    
    if context.readDataFile('redturtle.imagedevent_various.txt') is None: 
        return
    
    # Disabled: have the old portal_type in the types_tool duplicate "Event" choice in some places
    #backupATEvent(portal)

def backupATEvent(portal):
    """Make a backup of ATEvent before the types.xml step overwrite it"""
    portal_types = portal.portal_types
    try:
        oldevent_fti = getattr(portal_types, 'oldATEvent')
    except AttributeError:
        oldevent_fti = None
    if oldevent_fti:
        print "Doing nothing: ATEvent already disabled"
        return
    
    portal_types.manage_renameObject('Event', 'oldATEvent')
    oldevent_fti = getattr(portal_types, 'oldATEvent')
    
    oldevent_fti.global_allow = False
    print "Disabled Plone original ATEvent"

    
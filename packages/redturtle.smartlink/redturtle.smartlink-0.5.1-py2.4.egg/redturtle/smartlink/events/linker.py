# -*- coding: utf-8 -*-

from zope import interface
from Products.CMFCore.utils import getToolByName
from redturtle.smartlink.interfaces import ISmartLinked

def smartLink(object, event):
    """Mark target object as ISmartLinked"""
    target = object.getInternalLink()
    
    if target and not ISmartLinked.providedBy(target):
        interface.directlyProvides(target, ISmartLinked)

def keepLink(object, event):
    """ISmartLinked object has been modified/renamed.
    We need to catalog/update all ISmartLinks referencing it
    """
    rcatalog = getToolByName(object, 'reference_catalog')
    backRefs = rcatalog.getBackReferences(object)
    for r in backRefs:
        # BBB: updating only getRemoteUrl could lead to problem is someone use custom index
        # on the other hand, update all index change the modification date also.
        r.reindexObject(['getRemoteUrl'])

def unLink(object, event):
    """If the ISmartLinked is removed, we need to change the
    internal link to a normal external link.
    This way going ISmartLink object's edit form we see the link info.
    """
    catalog = getToolByName(object, 'portal_catalog')
    backRefs = catalog(getRawInternalLink=object.UID())
    for r in backRefs:
        obj = r.getObject()
        obj.setInternalLink(None)
        obj.setExternalLink(object.absolute_url())
        obj.reindexObject(['getRemoteUrl'])

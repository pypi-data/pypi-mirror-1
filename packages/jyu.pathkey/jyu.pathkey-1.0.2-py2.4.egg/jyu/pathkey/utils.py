# -*- coding: utf-8 -*-

import sys
from zope.event import notify
from interfaces import AfterTraverseEvent

from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.component import getUtility
from zope.interface import classProvides
from AccessControl import ClassSecurityInfo

from jyu.pathkey.interfaces import IPathkey
from jyu.pathkey.interfaces import IPathkeyFinnishForm
from jyu.pathkey.interfaces import IPathkeyEnglishForm
from jyu.pathkey.interfaces import IPathkeyListing

from OFS.SimpleItem import SimpleItem

# this hook will be called when traversal is complete
def postTraversehook():
    frame = sys._getframe(2)
    published = frame.f_locals['object']
    request = frame.f_locals['self']
    notify(AfterTraverseEvent(published, request))

# hook into the request.post_traversal through the IBeforeTraverse event
# only registered for ISiteRoot
def insertPostTraversalHook(object, event):
    event.request.post_traverse(postTraversehook)
    
def form_adapter(context):
    """Form Adapter"""
    return getUtility(IPathkey)


class Pathkey(SimpleItem):
    """Pathkey Utility"""
    implements(IPathkey)

    classProvides(
        IPathkeyFinnishForm,
        IPathkeyEnglishForm,
        IPathkeyListing,
        )

    security = ClassSecurityInfo()

    pathkeyTitle_fi = FieldProperty(IPathkeyFinnishForm['pathkeyTitle_fi'])
    pathkeyDescription_fi = FieldProperty(IPathkeyFinnishForm['pathkeyDescription_fi'])

    pathkeyTitle_en = FieldProperty(IPathkeyEnglishForm['pathkeyTitle_en'])
    pathkeyDescription_en = FieldProperty(IPathkeyEnglishForm['pathkeyDescription_en'])

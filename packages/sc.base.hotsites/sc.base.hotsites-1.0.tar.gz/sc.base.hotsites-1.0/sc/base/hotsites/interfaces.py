#! -*- coding: UTF-8 -*-

from zope.interface import Interface, alsoProvides
from zope.app.content.interfaces import IContentType

class IHotSite(Interface):
    ''' A section of your Plone Site that act as a Hot Site '''

alsoProvides(IHotSite, IContentType)

class INoHotSite(Interface):
    ''' A marker interface that allows subtyping reset '''

alsoProvides(INoHotSite, IContentType)

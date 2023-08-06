#! -*- coding: UTF-8 -*-

from p4a.subtyper.interfaces import IPortalTypedFolderishDescriptor
from zope.interface import implements

from zope.interface import Interface, alsoProvides
from zope.app.content.interfaces import IContentType

from sc.base.hotsites.interfaces import IHotSite, INoHotSite
from sc.base.hotsites import MessageFactory as _

class HotSite(object):
    implements(IPortalTypedFolderishDescriptor)

    title = _(u'Hot Site')
    description = _(u'Website section that acts as a Hot Site')
    type_interface = IHotSite
    for_portal_type = 'Folder'


class NoHotSite(object):
    implements(IPortalTypedFolderishDescriptor)

    title = _(u'Normal Folder')
    description = _(u'Just a plain Folder that does NOT acts as a Hot Site')
    type_interface = INoHotSite
    for_portal_type = 'Folder'

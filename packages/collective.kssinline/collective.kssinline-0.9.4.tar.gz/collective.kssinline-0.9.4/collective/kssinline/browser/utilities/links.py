from zope.interface import implements
from collective.kssinline.browser.interfaces import ILinkableItem
from Acquisition import aq_inner

class Brain(object):
    """
    Make sense from catalog brains
    """
    implements(ILinkableItem)

    def obj(self, item):
        return item.getObject()

    def uid(self, item):
        return item.UID

    def url(self, item):
        return item.getURL()

class FolderContents(object):
    """
    Make sense from the dictionary provided by plone.app.content's
    browser/foldercontents.py
    """
    implements(ILinkableItem)

    def obj(self, item):
        context = aq_inner(self.context)
        portal = getToolByName(context, 'portal_url').getPortalObject() 
        return portal.restrictedTraverse(item['path']())

    def uid(self, item):
        context = aq_inner(self.context)
        portal = getToolByName(context, 'portal_url').getPortalObject() 
        return portal.restrictedTraverse(item['path']()).UID()

    def url(self, item):
        return item['url']

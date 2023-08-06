from zope.interface import implements
from collective.kssinline.browser.interfaces import ILinkableItem

class Brain(object):

    implements(ILinkableItem)

    def __init__(self, context):
        self.context = context

    def obj(self):
        return self.context.getObject()

    def uid(self):
        return self.context.UID

    def url(self):
        return self.context.getURL()


from zope.interface import implements
from collective.kssinline.browser.interfaces import ILinkableItemView

class CollectivePortletExplore(object):
    """
    Adapters are preferable to utilities
    todo:
    """

    implements(ILinkableItemView)

    def __init__(self, context):
        self.context = context

    def obj(self, item):
        return item['item'].getObject()

    def uid(self, item):
        return item['item'].UID

    def url(self, item):
        return item['item'].getURL()

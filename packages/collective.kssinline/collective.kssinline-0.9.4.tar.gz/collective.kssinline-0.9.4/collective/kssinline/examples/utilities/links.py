from zope.interface import implements
from collective.kssinline.browser.interfaces import ILinkableItem

class CollectivePortletExplore(object):
    """
    A link utility which handles nodes that are provided 
    by collective.portlet.explore

    Experimental! collective.portlet.portlet needs a small 
    patch to recurse.pt for this to take effect.

    I still have to discuss with the developers.

    Basically, put the following next to the link anchor in
    recurse.pt:

    <tal:def define="dummy python:request.set('item', node)">
      <div tal:replace="structure provider:content.links" />
    </tal:def>
    """

    implements(ILinkableItem)

    def obj(self, item):
        return item['item'].getObject()

    def uid(self, item):
        return item['item'].UID

    def url(self, item):
        return item['item'].getURL()

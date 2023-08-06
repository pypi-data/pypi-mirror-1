from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Archetypes.interfaces.base import IBaseObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from zope.component import getUtility, queryUtility, queryAdapter
from collective.kssinline.browser.interfaces import ILinkableItem, ILinkableItemView
from warnings import warn

class BaseLink(BrowserView):
    """
    This view provides information on an item. This item is 
    typically a catalog brain, but can be any data type. Eg.
    for folder_contents the item will be a dictionary, and
    for collective.portlet.explore it is a different dictionary.
    """
    implements(IViewlet)
  
    def __init__(self, context, request, view, manager):           
        self.context = context
        self.request = request
        self.__parent__ = view
        self.manager = manager
        self.link_adapter = None
        self.link_utility = None

        # Adapters can be looked up for item, but for view we must
        # look up utilities. 
        #
        # The only reason that utilities are even used is that it 
        # makes it easier for third party products to be integrated. 
        # By easier I mean that the item that is supplied to this 
        # class does not have to be refactored.
        # 
        # Preferably a product should register an adapter for its 
        # item.

        # Find adapter for item
        item = request.get('item')
        self.link_adapter = queryAdapter(item, ILinkableItem)
        if self.link_adapter is not None:
            return

        msg = """Cannot find an ILinkableItem adapter for item. Handling \
of item now reverts to view adapters and utilities. You should modify your \
item to implement ILinkableItem and provide a suitable adapter."""
        warn(msg, DeprecationWarning, stacklevel=2)

        # Find adapter for view
        # This adapter has the same API as link_utility
        self.link_utility = queryAdapter(view, ILinkableItemView)
        if self.link_utility is not None:
            return
       
        # Find utility for view
        module_name = str(view.__module__)
        class_name = str(view.__class__.__name__)
        self.link_utility = queryUtility(ILinkableItem, '%s.%s' % (module_name, class_name))
        if self.link_utility is not None:
            return

        # Fall back to sensible default
        self.link_utility = getUtility(ILinkableItem, 'content.links.brain')

    def update(self):
        pass

    render = ViewPageTemplateFile("links.pt")    
   
    def obj(self, item):
        if self.link_adapter is not None:
            return self.link_adapter.obj()
        else:
            return self.link_utility.obj(item)

    def uid(self, item):
        if self.link_adapter is not None:
            return self.link_adapter.uid()
        else:
            return self.link_utility.uid(item)

    def url(self, item):
        if self.link_adapter is not None:
            return self.link_adapter.url()
        else:
            return self.link_utility.url(item)

    def editable(self, item, obj=None, return_object_if_true=False):
        # Return false if tool not available
        kssinline = getToolByName(self.context, 'portal_kssinline', None)        
        if kssinline is None:
            return False

        # Now we must fetch the object if not supplied
        if obj is None:
            obj = self.obj(item)

        pms = getToolByName(self.context, 'portal_membership')
        member = pms.getAuthenticatedMember()
        # xxx: IBaseObject check is very AT specific and may be redundant
        result = IBaseObject.isImplementedBy(obj) \
            and getattr(obj, 'portal_type', '') in kssinline.getEditableTypes() \
            and member.has_permission(ModifyPortalContent, obj)
        if not result:
            return False
        if return_object_if_true:
            return obj
        return True

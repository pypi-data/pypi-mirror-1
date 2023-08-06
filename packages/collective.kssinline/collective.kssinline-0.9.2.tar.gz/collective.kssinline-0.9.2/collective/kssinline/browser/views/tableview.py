from plone.app.content.browser import tableview
from Products.Archetypes.interfaces.base import IBaseObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from zope.app.pagetemplate import ViewPageTemplateFile
#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner

class Table(tableview.Table):

    def __init__(self, request, base_url, view_url, items, show_sort_column=False,
                             buttons=[], pagesize=20, context=None):
        tableview.Table.__init__(self, request, base_url, view_url, items, show_sort_column, buttons, pagesize)
        self.context = context

    def render(self, *args, **kwargs):
        pt = ViewPageTemplateFile("table.pt")
        return pt(self, *args, **kwargs)

    #batching = ViewPageTemplateFile("batching.pt")

    def editable(self, obj=None, item={}, return_object_if_true=False):
        # Return false if tool not available
        kssinline = getToolByName(self.context, 'portal_kssinline', None)        
        if kssinline is None:
            return False

        # Now we must fetch the object if not supplied
        if obj is None:
            obj = self.context.restrictedTraverse(item['relative_url'])

        pms = getToolByName(self.context, 'portal_membership')
        member = pms.getAuthenticatedMember()
        result = IBaseObject.isImplementedBy(obj) \
            and getattr(obj, 'portal_type', '') in kssinline.getEditableTypes() \
            and member.has_permission(ModifyPortalContent, obj)
        if not result:
            return False
        if return_object_if_true:
            return obj

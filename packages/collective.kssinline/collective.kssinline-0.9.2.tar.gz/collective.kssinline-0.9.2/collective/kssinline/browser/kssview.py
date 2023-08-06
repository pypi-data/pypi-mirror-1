from zope.interface import implements

from Acquisition import aq_inner, aq_parent
from Acquisition import Implicit
from Products.CMFCore.utils import getToolByName
from Products.CMFFormController.ControllerState import ControllerState

from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView

from archetypes.kss.validation import validate, SKIP_KSSVALIDATION_FIELDTYPES
from Products.CMFPlone import PloneMessageFactory as _
from cgi import parse_qs

from urlparse import urlsplit

from kss.core import kssaction, KSSExplicitError
from kss.core.BeautifulSoup import BeautifulSoup
from plone.app.kss.content_replacer import acquirerFactory

from plone.app.layout.globals.interfaces import IViewView
from plone.locking.interfaces import ILockable

from zope.interface import alsoProvides
from zope.interface import implements
from zope.component import getMultiAdapter

from ZPublisher.HTTPRequest import HTTPRequest

from zope.component.exceptions import ComponentLookupError
import base64

class KssView(Implicit, PloneKSSView):

    implements(IPloneKSSView)

    def prepareAndShowPopup(self, dom_node_id, item_uid=None, container_uid=None, type_name=None, context=None):
        if context is None:
            context = aq_inner(self.context)
        ksscore = self.getCommandSet('core')
        rc = getToolByName(context, 'reference_catalog')

        # Find the container if container_uid supplied
        container = context
        if container_uid:
            container = rc.lookupObject(container_uid)

        # Find the item if item_uid supplied
        item = None
        if item_uid:
            item = rc.lookupObject(item_uid)
            # The item must be in the container
            assert item.aq_parent == container

        # No item_uid supplied. This is a new item.
        if item is None:        
            # The content type must be subject to portal_factory else
            # we end up with turds on cancelled creation.
            # todo:
            assert type_name is not None
            pf = getToolByName(context, 'portal_factory')            
            if pf.getFactoryTypes().get(type_name, False):
                newid = pf.generateUniqueId(type_name)
                pf_url = "%s/portal_factory/%s/%s" % ('/'.join(context.getPhysicalPath()), type_name, newid)
                item = pf.restrictedTraverse(pf_url)
            else:
                newid = container.generateUniqueId(type_name)
                container.invokeFactory(type_name, newid)
                item = container._getOb(newid)

        # Prep the popup
        html = container.evalMacro(
                'archetype',
                template='kssinline_macros', 
                here=item,
                context=item,
                container=container,
                controller_state=ControllerState(id='dummy',context=item,errors={}))
        selector = ksscore.getHtmlIdSelector('kssinline-popup')
        ksscore.replaceInnerHTML(selector, html)
   
        # Show popup
        commands = self.getCommands()
        selector = ksscore.getHtmlIdSelector('kssinline-popup')
        commands.addCommand('kssinline-popupShow', 
            selector=selector, 
            dom_node_id=dom_node_id)

        return self.render()

    def actionMenuClickHandler(self, dom_node_id, href):
        context = aq_inner(self.context)
        ksscore = self.getCommandSet('core')

        (proto, host, path, query, anchor) = urlsplit(href)

        if not query:
            raise KSSExplicitError, 'Nothing to do'
        
        # Parse
        di = parse_qs(query)

        # Get type_name. Clean up a bit.
        type_name = di.get('type_name', None)
        if type(type_name) == type([]):
            type_name = type_name[-1]

        if not type_name:
            raise KSSExplicitError, 'No type_name specified'

        # Check that we are allowed to edit this type inline
        tool = getToolByName(context, 'portal_kssinline', None)
        if (tool is None) or (type_name not in tool.getEditableTypes()):
            raise KSSExplicitError, 'Inline editing not allowed'

        # We cannot trust context in this case, eg. when on Plone's Events View
        # tab the context is in fact the aggregator. Obtain the correct context
        # from the URL.
        physical_path = list(self.request.physicalPathFromURL('%s://%s/%s' % (proto, host, path)))
        # The last element of physical_path is createObject and must be discarded
        physical_path = physical_path[:-1]
        # Override context
        new_context = self.context.restrictedTraverse('/'.join(physical_path))

        return self.prepareAndShowPopup(dom_node_id=dom_node_id, type_name=type_name, context=new_context)
       
    def saveItem(self, action, url, item_uid=None, item_path=None):
        context = aq_inner(self.context)
        ksscore = self.getCommandSet('core')
        
        item = context

        if (item_path is not None) and (item_path.find('portal_factory') != -1):
            # Try and find the item in portal_factory
            pf = getToolByName(context, 'portal_factory')            
            item = pf.restrictedTraverse(item_path)

        elif item_uid:
            # Find the item if item_uid supplied
            rc = getToolByName(context, 'reference_catalog')
            item = rc.lookupObject(item_uid)

        if action != 'form_submit':
            # Unlock
            try:
                lock = getMultiAdapter((item,self.request), name='plone_lock_operations')
            except ComponentLookupError:
                pass
            else:
                lock.safe_unlock()
            # Close popup
            commands = self.getCommands()
            selector = ksscore.getHtmlIdSelector('kssinline-popup')
            commands.addCommand('kssinline-popupHide', selector=selector)
            return self.render()

        # Adapted from archetypes.kss.validation
        instance = item
        schema = instance.Schema()
        errors = validate(schema, instance, self.request, errors={}, data=1, metadata=0,
                    predicates=(lambda field: field.type not in SKIP_KSSVALIDATION_FIELDTYPES, )
                    )

        if errors:
            # Issue message similar to portal status message, but bound
            # to the popup.
            tool = getToolByName(context, 'plone_utils')
            tool.addPortalMessage(_("Please correct the indicated errors"), type="error")
            html = context.evalMacro(
                'portal_message',
                template='global_statusmessage')
            selector = ksscore.getHtmlIdSelector('kssinline-popup-messages')
            ksscore.replaceInnerHTML(selector, html)

            # Reset all error fields (as we only know the error ones)
            ksscore.clearChildNodes(ksscore.getCssSelector('div.field div.fieldErrorBox'))
            # Set error fields
            for fieldname, error in errors.iteritems():
                if isinstance(error, str):
                    error = error.decode('utf', 'replace')
                self.context = instance
                self.getCommandSet('atvalidation').issueFieldError(fieldname, error)

        else:
            # Make it a real object. This call is safe on existing 'real' objects.
            pf = getToolByName(context, 'portal_factory')
            instance = pf.doCreate(instance)

            # Apply changes
            instance.processForm(REQUEST=context.REQUEST)

            # Unlock
            try:
                lock = getMultiAdapter((instance,self.request), name='plone_lock_operations')
            except ComponentLookupError:
                pass
            else:
                lock.safe_unlock()

            # Close popup
            commands = self.getCommands()
            selector = ksscore.getHtmlIdSelector('kssinline-popup')
            commands.addCommand('kssinline-popupHide', selector=selector)

            # Refresh content. The request must be cleaned since it influences getFolderContents and 
            # possibly other methods as well.
            self.request.form = {}            
            if url:
                (proto, host, path, query, anchor) = urlsplit(url)
                if query:
                    # Update request from query string present in url
                    env = {'SERVER_NAME': 'testingharnas', 'SERVER_PORT': '80'}
                    env['QUERY_STRING'] = query
                    req = HTTPRequest(None, env, None)
                    req.processInputs()
                    for k,v in req.form.items():
                        self.request.form[k] = v
                html = self.replaceContentRegion('%s://%s/%s' % (proto, host, path), tabid='contentview-folderContents')
            else:
                html = self.replaceContentRegion(context.absolute_url(), tabid='contentview-folderContents')

            # Don't trash the content region if something went wrong
            if html:
                ksscore.replaceHTML(ksscore.getHtmlIdSelector('region-content'), html)

            # Message
            self.getCommandSet('plone').issuePortalMessage(_(u'Changes saved.'))

        return self.render()

    def replaceContentRegion(self, url, tabid=''):
        """
        Shamelessly stolen from plone.app.kss
        """
        context = aq_inner(self.context)

        if not tabid or tabid == 'content':
            raise KSSExplicitError, 'No tabid on the tab'
        if not tabid.startswith('contentview-'):
            raise RuntimeError, 'Not a valid contentview id "%s"' % tabid
        # Split the url into it's components
        (proto, host, path, query, anchor) = urlsplit(url)
        # if the url doesn't use http(s) or has a query string or anchor
        # specification, don't bother
        if query or anchor or proto not in ('http', 'https'):
            raise KSSExplicitError, 'Unhandled protocol on the tab'
        # make the wrapping for the context, to overwrite main_template
        # note we have to use aq_chain[0] *not* aq_base.
        # XXX however just context would be good too? Hmmm
        wrapping = acquirerFactory(context)
        # Figure out the template to render.
        # We need the physical path which we can obtain from the url
        path = list(self.request.physicalPathFromURL(url))
        obj_path = list(context.getPhysicalPath())
        if path == obj_path:
            # target is the default view of the method.
            # url is like: ['http:', '', 'localhost:9777', 'kukitportlets', 'prefs_users_overview']
            # physical path is like: ('', 'kukitportlets')
            # We lookup the default view for the object, which may be
            # another object, if so we give up, otherwise we use the
            # appropriate template
            utils = getToolByName(context, 'plone_utils')
            if utils.getDefaultPage(context) is not None:
                raise KSSExplicitError, 'no default page on the tab'
            viewobj, viewpath = utils.browserDefault(context)
            if len(viewpath) == 1:
                viewpath = viewpath[0]
            template = viewobj.restrictedTraverse(viewpath)
        else:
            # see if it is a method on the same context object...
            # url is like: ['http:', '', 'localhost:9777', 'kukitportlets', 'prefs_users_overview']
            # physical path is like: ('', 'kukitportlets')
            if path[:-1] != obj_path:
                raise KSSExplicitError, 'cannot reload since the tab visits a different context'
            method = path[-1]
            # Action method may be a method alias: Attempt to resolve to a template.
            try:
                method = context.getTypeInfo().queryMethodID(method, default=method)
            except AttributeError:
                # Don't raise if we don't have a CMF 1.5 FTI
                pass
            template = wrapping.restrictedTraverse(method)
        # We render it
        content = template()
        # Now. We take out the required node from it!
        # We need this in any way, as we don't know if the template
        # actually used main_template! In that case we would have
        # the *whole* html which is wrong.
        soup = BeautifulSoup(content)
        replace_id = 'region-content'
        tag = soup.find('div', id=replace_id)
        if tag is None:
            raise RuntimeError, 'Result content did not contain <div id="%s">' % replace_id
        # now we send it back to the client
        result = unicode(tag)

        return result
        
class ArchetypesKssWrapperView(Implicit, PloneKSSView):
    """
    Traversal only cares about the context it is aware of, which means
    ZCML permission settings operate on that context. Those permissions
    may not allow traversal, so we have to change the context and then 
    do the traversal.
    """

    implements(IPloneKSSView)

    def kssValidateField(self, fieldname, value, uid=None, item_path=None):
        """
        Our popup does have an item_path available, but it never gets 
        passed to this method since Archetypes' at.kss does not provide
        it.

        Instead we abuse kssattr-uid to store the item path if the object
        is temporary. This is done in override.py.
        """
        context = aq_inner(self.context)

        if (item_path is not None) and (item_path.find('portal_factory') != -1):
            # Try and find the item in portal_factory
            pf = getToolByName(context, 'portal_factory')            
            new_context = pf.restrictedTraverse(item_path)

        elif uid is not None:
            possibly_decoded_uid = base64.b64decode(uid)

            if possibly_decoded_uid.find('portal_factory') != -1:
                # Try and find the item in portal_factory
                pf = getToolByName(context, 'portal_factory')            
                new_context = pf.restrictedTraverse(possibly_decoded_uid)
            else:
                rc = getToolByName(context, 'reference_catalog')
                new_context = rc.lookupObject(uid)

        # Fallback
        if new_context is not None:
            context = new_context

        return context.restrictedTraverse('originalKssValidateField')(fieldname, value, uid=None)

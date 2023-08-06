# -*- coding: utf-8 -*-
#
# File: kssinline.py
#
# Copyright (c) 2008 by Upfront Systems CC
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Hedley Roos <hedley@upfrontsystems.co.za>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from collective.kssinline.config import *


from Products.CMFCore.utils import UniqueObject

    
##code-section module-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName
##/code-section module-header

schema = Schema((

    LinesField(
        name='editableTypes',
        widget=MultiSelectionWidget(
            label="Editable Types",
            size=20,
            label_msgid='kssinline_label_editableTypes',
            i18n_domain='collective.kssinline',
        ),
        multiValued=1,
        vocabulary='editableTypesVocabulary',
        default_method='defaultEditableTypes',
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

KssInlineTool_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class KssInlineTool(UniqueObject, BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IKssInlineTool)

    meta_type = 'KssInlineTool'
    _at_rename_after_creation = True

    schema = KssInlineTool_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        BaseContent.__init__(self,'portal_kssinline')
        self.setTitle('')
        
        ##code-section constructor-footer #fill in your manual code here
        ##/code-section constructor-footer


    # tool should not appear in portal_catalog
    def at_post_edit_script(self):
        self.unindexObject()
        
        ##code-section post-edit-method-footer #fill in your manual code here
        ##/code-section post-edit-method-footer


    # Methods

    # Manually created methods

    def editableTypesVocabulary(self):
        tool = getToolByName(self, 'portal_types')
        return tool.objectIds()

    def defaultEditableTypes(self):
        # Go through all portal types and exclude those with either
        # file or image in their schema.
        # todo:
        return [t for t in self.editableTypesVocabulary() if not t in ('File','Image')]

    def Title(self):
        return "KssInline Tool"



registerType(KssInlineTool, PROJECTNAME)
# end of class KssInlineTool

##code-section module-footer #fill in your manual code here
##/code-section module-footer




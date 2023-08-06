# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2008 by Upfront Systems CC
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Hedley Roos <hedley@upfrontsystems.co.za>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('kssinline: setuphandlers')
from collective.kssinline.config import PROJECTNAME
from collective.kssinline.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
##/code-section HEAD

def isNotkssinlineProfile(context):
    return context.readDataFile("kssinline_marker.txt") is None

def setupHideToolsFromNavigation(context):
    """hide tools"""
    if isNotkssinlineProfile(context): return 
    # uncatalog tools
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'kssinline': # avoid infinite recursions
        return
    site = context.getSite()
    toolnames = ['portal_kssinline']
    portalProperties = getToolByName(site, 'portal_properties')
    navtreeProperties = getattr(portalProperties, 'navtree_properties')
    if navtreeProperties.hasProperty('idsNotToList'):
        for toolname in toolnames:
            try:
                portal[toolname].unindexObject()
            except:
                pass
            current = list(navtreeProperties.getProperty('idsNotToList') or [])
            if toolname not in current:
                current.append(toolname)
                kwargs = {'idsNotToList': current}
                navtreeProperties.manage_changeProperties(**kwargs)

def fixTools(context):
    """do post-processing on auto-installed tool instances"""
    site = context.getSite()

    tool_ids=['portal_kssinline']
    for tool_id in tool_ids:
        tool=site[tool_id]
        tool.initializeArchetype()



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotkssinlineProfile(context): return 
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'kssinline': # avoid infinite recursions
        return
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotKssInlineProfile(context): return
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'KssInline': # avoid infinite recursions
        return
    site = context.getSite()



##code-section FOOT
isNotKssInlineProfile = isNotkssinlineProfile
##/code-section FOOT

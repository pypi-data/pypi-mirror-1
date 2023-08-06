# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2009 by Menttes SRL
# Generator: ArchGenXML Version 2.4.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Emanuel Sartor <emanuel@menttes.com>, Santiago Bruno <unknown>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('DigestoContentTypes: setuphandlers')
from Products.DigestoContentTypes.config import PROJECTNAME
from Products.DigestoContentTypes.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
from Products.DigestoContentTypes.config import PLACEFUL_WORKFLOW_POLICY
##/code-section HEAD

def isNotDigestoContentTypesProfile(context):
    return context.readDataFile("DigestoContentTypes_marker.txt") is None



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotDigestoContentTypesProfile(context): return 
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotDigestoContentTypesProfile(context): return
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'DigestoContentTypes': # avoid infinite recursions
        return
    site = context.getSite()



##code-section FOOT
def registerAttachmentsFormControllerActions(context, contentType=None, template='manage_attachments'):
    """Register the form controller actions necessary for the widget to work.
    This should probably be called from the Install.py script. The parameter
    'context' should be the portal root or another place from which the form
    controller can be acquired. The contentType and template argument allow
    you to restrict the registration to only one content type and choose a
    template other than base_edit, if necessary.
    """
    site = context.getSite()
    pfc = site.portal_form_controller
    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'UploadAttachment',
                      'traverse_to',
                      'string:widget_attachmentsmanager_upload')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'RenameAttachments',
                      'traverse_to',
                      'string:widget_attachmentsmanager_rename')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'MoveAttachments',
                      'traverse_to',
                      'string:widget_attachmentsmanager_move')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'DeleteAttachments',
                      'traverse_to',
                      'string:widget_attachmentsmanager_delete')

def allowNormativaInLargeFolders(context):
    """Allow Normativa as an addable type inside Large Plone Folders.
    """
    types = getToolByName(context.getSite(), 'portal_types')
    fti = getattr(types, 'Large Plone Folder')
    if 'Normativa' not in fti.allowed_content_types:
        fti.allowed_content_types = fti.allowed_content_types + ('Normativa',)


def addAreaPlacefulWorkflowPolicy(context):
    """Add the placeful workflow policy used for areas.
    """
    placeful_workflow = getToolByName(context, 'portal_placeful_workflow')
    if PLACEFUL_WORKFLOW_POLICY not in placeful_workflow.objectIds():
        placeful_workflow.manage_addWorkflowPolicy(PLACEFUL_WORKFLOW_POLICY)
        policy = placeful_workflow.getWorkflowPolicyById(PLACEFUL_WORKFLOW_POLICY)
        policy.setTitle('[DigestoContentTypes] Area workflows')
        policy.setDefaultChain(('area_workflow',))
        types = ('Folder', 'Large Plone Folder')
        policy.setChainForPortalTypes(types, ('area_workflow',))
        policy.setChainForPortalTypes(('Normativa',), ('normativa_workflow',))


def addCatalogIndexes(context):
    """Add our indexes to the catalog.

    Doing it here instead of in profiles/default/catalog.xml means we do
    not need to reindex those indexes after every reinstall.
    """

    catalog = getToolByName(context.getSite(), 'portal_catalog')
    indexes = catalog.indexes()
    wanted = (('getDate', 'DateIndex'),
              ('getSource', 'FieldIndex'),
              ('getNumber', 'FieldIndex'),
              ('getRepeals', 'FieldIndex'),
              ('getModifies', 'FieldIndex'),
              ('getRepealedBy', 'FieldIndex'),
              ('getKind', 'FieldIndex'),
              ('getAbbreviation', 'FieldIndex'),
              ('getArea', 'FieldIndex'),
              ('getCudap', 'FieldIndex'),
             )

    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            logger.info("Added %s for field %s.", meta_type, name)
##/code-section FOOT

# -*- coding: utf-8 -*-
#
# File: Area.py
#
# Copyright (c) 2009 by Menttes SRL
# Generator: ArchGenXML Version 2.4.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Emanuel Sartor <emanuel@menttes.com>, Santiago Bruno <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.DigestoContentTypes.config import *

# additional imports from tagged value 'import'
from Products.ATExtensions.ateapi import *

##code-section module-header #fill in your manual code here
from zope.component import adapter
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IObjectInitializedEvent
from Products.DigestoContentTypes.config import PLACEFUL_WORKFLOW_POLICY
from zope.app.annotation.interfaces import IAttributeAnnotatable, IAnnotations
##/code-section module-header

schema = Schema((

    RecordsField(
        name='sources',
        widget=RecordsWidget(
            description="Add sources and associate document types with them.",
            visible={'view': 'invisible', 'edit': 'visible'},
            label='Sources',
            label_msgid='DigestoContentTypes_label_sources',
            description_msgid='DigestoContentTypes_help_sources',
            i18n_domain='DigestoContentTypes',
        ),
        required=1,
    ),
    LinesField(
        name='addressBook',
        widget=LinesField._properties['widget'](
            label="Address Book",
            description="Enter an e-mail address per line.",
            visible={'view': 'invisible', 'edit': 'visible'},
            label_msgid='DigestoContentTypes_label_addressBook',
            description_msgid='DigestoContentTypes_help_addressBook',
            i18n_domain='DigestoContentTypes',
        ),
        validators=('is_address_book',),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
schema['sources'].subfields = ('source', 'kinds')
schema['sources'].subfield_types = {'source':'string', 'kinds':'lines'}
schema['sources'].subfield_vocabularies = {}
schema['sources'].required_subfields = ('source', 'kinds')
schema['sources'].subfield_validators = {'source':('is_source_name',), 'kinds':('is_not_empty_kinds',)}
schema['sources'].innerJoin = ', '
schema['sources'].outerJoin = '<br />'
schema['sources'].widget.macro = 'dct_records_widget'
##/code-section after-local-schema

Area_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Area(BaseFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IArea)

    meta_type = 'Area'
    _at_rename_after_creation = True

    schema = Area_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    # Manually created methods

    security.declarePublic('setAbbreviations')
    def setAbbreviations(self, value):
        if value:
            annotations = IAnnotations(self)
            annotations[ABBREVIATIONS_KEY] = value

    security.declarePublic('getAbbreviations')
    def getAbbreviations(self):
        annotations = IAnnotations(self)
        return annotations.get(ABBREVIATIONS_KEY, None)
    ##/code-section class-header


registerType(Area, PROJECTNAME)
# end of class Area

##code-section module-footer #fill in your manual code here
from Products.CMFPlone.interfaces import INonStructuralFolder
from zope.interface import classImplements

classImplements(Area, [INonStructuralFolder, IAttributeAnnotatable])

@adapter(interfaces.IArea, IObjectInitializedEvent)
def handle_area_added(obj, event):
    """Handle the IObjectInitializedEvent event for area.
    """
    policy_below = PLACEFUL_WORKFLOW_POLICY
    obj.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
    config = obj.portal_placeful_workflow.getWorkflowPolicyConfig(obj)
    config.setPolicyBelow(policy=policy_below)
    getToolByName(obj, 'portal_workflow').updateRoleMappings()

##/code-section module-footer




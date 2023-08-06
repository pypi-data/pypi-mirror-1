# -*- coding: utf-8 -*-
#
# File: Attachment.py
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
from iw.fss.FileSystemStorage import FileSystemStorage

##code-section module-header #fill in your manual code here
from zope.component import adapter
from Products.Archetypes.interfaces import IObjectInitializedEvent, IObjectEditedEvent
from zope.app.event.interfaces import IObjectModifiedEvent, IObjectCreatedEvent
from Acquisition import aq_inner, aq_parent
from zope.app.component.interfaces import ISite
##/code-section module-header

schema = Schema((

    FileField(
        name='file',
        widget=FileField._properties['widget'](
            label='File',
            label_msgid='DigestoContentTypes_label_file',
            i18n_domain='DigestoContentTypes',
        ),
        storage=FileSystemStorage(),
        searchable=1,
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Attachment_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Attachment(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IAttachment)

    meta_type = 'Attachment'
    _at_rename_after_creation = True

    schema = Attachment_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(Attachment, PROJECTNAME)
# end of class Attachment

##code-section module-footer #fill in your manual code here

@adapter(interfaces.IAttachment, IObjectModifiedEvent)
def handle_attachment_added(obj, event):
    """Handle the IObjectInitializedEvent event for attachments.
    """
    #rename the file using the attachment id

    obj.schema['file'].setFilename(obj, obj.id)


##/code-section module-footer




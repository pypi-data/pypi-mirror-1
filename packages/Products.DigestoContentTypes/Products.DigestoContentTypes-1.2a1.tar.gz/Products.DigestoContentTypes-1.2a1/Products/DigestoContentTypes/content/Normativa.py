# -*- coding: utf-8 -*-
#
# File: Normativa.py
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
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.ATBackRef.backref import BackReferenceField
from Products.ATBackRef.backref import BackReferenceWidget
from iw.fss.FileSystemStorage import FileSystemStorage
from Products.DigestoContentTypes.widget import AttachmentsManagerWidget

##code-section module-header #fill in your manual code here
import transaction

# Imports for event handlers
from Acquisition import aq_inner, aq_parent, aq_base
from zope.interface import alsoProvides
from zope.component import adapter
from zope.app.component.interfaces import ISite
from zope.event import notify
from zope.app.container.contained import notifyContainerModified
from zope.app.container.contained import ObjectMovedEvent
from OFS.event import ObjectWillBeMovedEvent

from Products.Archetypes.interfaces import IObjectInitializedEvent, IObjectEditedEvent
from Products.CMFPlone.utils import normalizeString, _createObjectByType

# Security imports
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser

##/code-section module-header

schema = Schema((

    StringField(
        name='title',
        widget=StringField._properties['widget'](
            label='Title',
            label_msgid='DigestoContentTypes_label_title',
            i18n_domain='DigestoContentTypes',
        ),
        required=0,
        accessor="Title",
        searchable=1,
        write_permission='DigestoContentTypes: Edit Normativa',
    ),
    TextField(
        name='description',
        widget=TextAreaWidget(
            label="Description",
            label_msgid='DigestoContentTypes_label_description',
            i18n_domain='DigestoContentTypes',
        ),
        accessor="Description",
        searchable=1,
        write_permission='DigestoContentTypes: Edit Normativa',
    ),
    FileField(
        name='file',
        widget=FileField._properties['widget'](
            label='File',
            label_msgid='DigestoContentTypes_label_file',
            i18n_domain='DigestoContentTypes',
        ),
        searchable=1,
        required=1,
        storage=FileSystemStorage(),
        write_permission='DigestoContentTypes: Edit Normativa',
    ),
    DateTimeField(
        name='date',
        widget=DateTimeField._properties['widget'](
            show_hm=False,
            format='%d/%m/%Y',
            label='Date',
            label_msgid='DigestoContentTypes_label_date',
            i18n_domain='DigestoContentTypes',
        ),
        required=1,
        write_permission='DigestoContentTypes: Edit Normativa',
    ),
    StringField(
        name='source',
        widget=StringField._properties['widget'](
            label='Source',
            label_msgid='DigestoContentTypes_label_source',
            i18n_domain='DigestoContentTypes',
        ),
        required=1,
        write_permission='DigestoContentTypes: Edit Normativa',
    ),
    IntegerField(
        name='number',
        widget=IntegerField._properties['widget'](
            size=30,
            label='Number',
            label_msgid='DigestoContentTypes_label_number',
            i18n_domain='DigestoContentTypes',
        ),
        required=1,
        write_permission='DigestoContentTypes: Edit Normativa',
        searchable=1,
    ),
    ReferenceField(
        name='repeals',
        widget=ReferenceBrowserWidget(
            label="Repeals to...",
            label_msgid='DigestoContentTypes_label_repeals',
            i18n_domain='DigestoContentTypes',
        ),
        multiValued=True,
        relationship="repeal",
        write_permission='DigestoContentTypes: Edit Normativa Metadata',
    ),
    ReferenceField(
        name='modifies',
        widget=ReferenceBrowserWidget(
            label="Modifies to...",
            label_msgid='DigestoContentTypes_label_modifies',
            i18n_domain='DigestoContentTypes',
        ),
        multiValued=True,
        relationship="modify",
        write_permission='DigestoContentTypes: Edit Normativa Metadata',
    ),
    BackReferenceField(
        name='repealedBy',
        widget=BackReferenceWidget(
            label="Repealed by...",
            visible={'view': 'visible', 'edit': 'invisible'},
            label_msgid='DigestoContentTypes_label_repealedBy',
            i18n_domain='DigestoContentTypes',
        ),
        multiValued=True,
        relationship="repeal",
        write_permission='DigestoContentTypes: Edit Normativa',
    ),
    StringField(
        name='kind',
        widget=StringField._properties['widget'](
            label='Kind',
            label_msgid='DigestoContentTypes_label_kind',
            i18n_domain='DigestoContentTypes',
        ),
        required=1,
        write_permission='DigestoContentTypes: Edit Normativa',
    ),
    StringField(
        name='abbreviation',
        widget=StringField._properties['widget'](
            visible={'view': 'visible', 'edit': 'invisible'},
            label='Abbreviation',
            label_msgid='DigestoContentTypes_label_abbreviation',
            i18n_domain='DigestoContentTypes',
        ),
        write_permission='DigestoContentTypes: Edit Normativa',
    ),
    LinesField(
        name='dossierNumber',
        widget=LinesField._properties['widget'](
            label="Dossier Numbers",
            label_msgid='DigestoContentTypes_label_dossierNumber',
            i18n_domain='DigestoContentTypes',
        ),
        write_permission='DigestoContentTypes: Edit Normativa',
        searchable=1,
        validators=('is_dossier_number_list',),
    ),
    BooleanField(
        name='displayAttachments',
        default="True",
        widget=AttachmentsManagerWidget(
            description="If selected, a list of uploaded attachments will be presented at the bottom of the document to allow them to be easily downloaded",
            label="Display attachments download box",
            visible={'view': 'invisible', 'edit': 'invisible'},
            label_msgid='DigestoContentTypes_label_displayAttachments',
            description_msgid='DigestoContentTypes_help_displayAttachments',
            i18n_domain='DigestoContentTypes',
        ),
        languageIndependent=0,
        write_permission='DigestoContentTypes: Edit Normativa',
    ),
    StringField(
        name='area',
        widget=StringField._properties['widget'](
            visible={'view': 'invisible', 'edit': 'invisible'},
            label='Area',
            label_msgid='DigestoContentTypes_label_area',
            i18n_domain='DigestoContentTypes',
        ),
        write_permission='DigestoContentTypes: Edit Normativa',
    ),
    BooleanField(
        name='autoTitle',
        widget=BooleanField._properties['widget'](
            visible={'view':'invisible', 'edit':'invisible'},
            label='Autotitle',
            label_msgid='DigestoContentTypes_label_autoTitle',
            i18n_domain='DigestoContentTypes',
        ),
        write_permission='DigestoContentTypes: Edit Normativa',
    ),
    ComputedField(
        name='normativaFilename',
        widget=ComputedField._properties['widget'](
            visible={'view': 'invisible', 'edit': 'invisible'},
            label='Normativafilename',
            label_msgid='DigestoContentTypes_label_normativaFilename',
            i18n_domain='DigestoContentTypes',
        ),
        expression="context._getNormativaFilename()",
        write_permission='DigestoContentTypes: Edit Normativa',
        searchable=1,
    ),
    StringField(
        name='cudap',
        widget=StringField._properties['widget'](
            label="CUDAP",
            description="Format: TYPEDOC-SERVER:NUMBER/YEAR   Example: RESOREC-UNC:0003657/2008",
            label_msgid='DigestoContentTypes_label_cudap',
            description_msgid='DigestoContentTypes_help_cudap',
            i18n_domain='DigestoContentTypes',
        ),
        write_permission='DigestoContentTypes: Edit Normativa',
        searchable=1,
        validators=('is_cudap_number',),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Normativa_schema = OrderedBaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
Normativa_schema['kind'].widget.macro_edit = 'normativa_kind_widget'
Normativa_schema['source'].widget.macro_edit = 'normativa_source_widget'
Normativa_schema['subject'].write_permission = 'DigestoContentTypes: Edit Normativa Metadata'
##/code-section after-schema

class Normativa(OrderedBaseFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.INormativa)

    meta_type = 'Normativa'
    _at_rename_after_creation = True

    schema = Normativa_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    # Manually created methods

    def _renameAfterCreation(self, check_auto_id=False):

        normativa_id = str(self.number) + '_' + str(self.date.year())

        if not self.title:
            normativa_title = self.kind + ' ' + str(self.number) + '/' + str(self.date.year())
            self.setTitle(normativa_title)
            self.setAutoTitle(True)
        else:
            self.setAutoTitle(False)

        # Can't rename without a subtransaction commit when using
        # portal_factory!
        transaction.commit(1)
        self.setId(normativa_id)

    def _getNormativaFilename(self):
        """search helper"""
        return self.schema['file'].getFilename(self)



registerType(Normativa, PROJECTNAME)
# end of class Normativa

##code-section module-footer #fill in your manual code here
from Products.CMFPlone.interfaces import INonStructuralFolder
from zope.interface import classImplements

classImplements(Normativa, INonStructuralFolder)


@adapter(interfaces.INormativa, IObjectInitializedEvent)
def handle_normativa_added(obj, event):
    """Handle the IObjectInitializedEvent event for normativa"""

    # Generate and Store the Abbreviation
    parent = aq_parent(aq_inner(obj))
    abbreviations = parent.getAbbreviations()
    if abbreviations:
        abbreviation = abbreviations.get( (obj.getSource(), obj.getKind()) )
    else:
        abbreviation = None

    # In case that no abreviations were provided, we took the name the
    # name of the normativa. Since it's usually too long, we only take
    # the first 3 letters from the title if given, otherwise the 'kind'
    # field is used.
    if not abbreviation:
        try:
            abbreviation = obj.Title()[:3].upper()
        except:
            abbreviation = obj.getKind()[:3].upper()

    obj.setAbbreviation(abbreviation)

    # Renames the main file
    if obj.getFile() and abbreviation:
        filename = obj.schema['file'].getFilename(obj)
        extension = filename.split('.')[-1]

        kind = normalizeString(obj.getKind(), obj)
        number = str(obj.getNumber())
        year = str(obj.getDate().year())

        prefix = "_".join( (abbreviation, number, year) )
        new_filename = prefix + '.' + extension
        if filename != new_filename:
            obj.schema['file'].setFilename(obj, new_filename)

    move_normativa(obj, event)


@adapter(interfaces.INormativa, IObjectEditedEvent)
def handle_normativa_edited(obj, event):
    """Handle the IObjectEditedEvent event for normativa"""

    parent = aq_parent(aq_inner(obj))
    grand_parent = aq_parent(aq_inner(parent))
    area = aq_parent(aq_inner(grand_parent))

    source_id = normalizeString(obj.getSource(), obj)
    kind_id = normalizeString(obj.getKind(), obj)

    kind_changed = parent.id != kind_id or grand_parent.id != source_id

    normativa_id = obj.id
    splitted_id = normativa_id.split("_")

    # Generates a new id if the fields that forms it have changed
    new_number = str(obj.getNumber())
    new_year = str(obj.getDate().year())
    new_id = new_number + '_' + new_year
    if len(splitted_id) >= 2:
        if new_number == splitted_id[0] and new_year == splitted_id[1]:
            new_id = ""

    # Title depends on kind, number, and year. We regenerate it if one
    # of this fields changed, and the title was an autogenerated title.
    # We also check if it is still autogenerated or if in this edition
    # the user changed the title manually. Emptying the title makes it
    # auto generated again.
    title = obj.Title()
    if not title or (obj.getAutoTitle() and (new_id or kind_changed)):
        autotitle = True
        splitted_title = title.split(" ")

        if not title:
            autotitle = True
        elif len(splitted_title) != 2:
            autotitle = False
        else:
            try:
                splitted_number = splitted_title[1].split("/")
                int(splitted_number[0])
                int(splitted_number[1])
                if len(splitted_number) != 2:
                    autotitle = False
            except:
                autotitle = False

        if autotitle:
            normativa_title = obj.getKind() + ' ' + str(obj.getNumber()) + \
                              '/' + str(obj.getDate().year())
            obj.setTitle(normativa_title)
            obj.setAutoTitle(True)
        else:
            obj.setAutoTitle(False)

    # Generate and Store the Abbreviation
    try:
        abbreviations = area.getAbbreviations()
    except:
        abbreviations = None

    if abbreviations:
        abbreviation = abbreviations.get( (obj.getSource(), obj.getKind()) )
    else:
        abbreviation = None

    # In case that no abreviations were provided, we took the name the
    # name of the normativa. Since it's usually too long, we only take
    # the first 3 letters from the title if given, otherwise the 'kind'
    # field is used.
    if not abbreviation:
        try:
            abbreviation = obj.Title()[:3].upper()
        except:
            abbreviation = obj.getKind()[:3].upper()

    obj.setAbbreviation(abbreviation)

    # Renames the main file
    file_renamed = False
    if obj.getFile() and abbreviation:
        filename = obj.schema['file'].getFilename(obj)
        extension = filename.split('.')[-1]

        kind = normalizeString(obj.getKind(), obj)
        number = str(obj.getNumber())
        year = str(obj.getDate().year())

        prefix = "_".join( (abbreviation, number, year) )
        new_filename = prefix + '.' + extension
        if filename != new_filename:
            file_renamed = True
            obj.schema['file'].setFilename(obj, new_filename)

            # Rename the attachments
            for brain in obj.getFolderContents(
                            contentFilter={'portal_type': ['Attachment']}):
                attach = getattr(obj, brain.getId).getFile()
                dotDelimited = attach.filename.split('.')
                if len(dotDelimited) > 1:
                    ext      = dotDelimited[-1]
                    filename = "".join(dotDelimited[:-1])
                else:
                    ext      = None
                    filename = attach.filename

                # Add the suffix
                if len(filename.split('_')) > 3:
                    new_filename = prefix + '_' +filename.split('_')[-1]
                else:
                    new_filename = prefix

                if ext is not None:
                    new_filename = new_filename + '.' + ext

                obj.invokeFactory( id = new_filename,
                            type_name = 'Attachment',
                                 file = attach,
                                title = attach.Title()
                                )

                obj.manage_delObjects(brain.getId)

    if new_id:
        # Just change its id. Check if new object id exists on parent
        # folder. Generate one that does not exist in that case.
        target_ids = parent.objectIds()
        object_id = new_id
        new_object_id = new_id

        if object_id in target_ids:
            suffix = 1
            new_object_id = object_id + "_1"
            while new_object_id in target_ids:
                suffix = suffix + 1
                new_object_id = object_id + '_' + str(suffix)

        obj.setId(new_object_id)

    if parent.id != kind_id or grand_parent.id != source_id:
        # Move the normativa and possibly change its id
        move_normativa(obj, event, new_id)

    # Reindex SearchableText if main file was renamed
    if file_renamed:
        obj.reindexObject(idxs=['SearchableText'])


def allow_delete_object(obj, roles, parent_roles):
    """XXX Change the permission 'Delete objects' of obj and obj's
    parent setting them as true for the roles paramenter. The old roles
    set for the 'Delete objects' permission in obj and obj's parent is
    returned in a tuple.
    """
    obj_permissions = [r['name'] for r in \
                       obj.rolesOfPermission('Delete objects') if r['selected']]
    parent = aq_parent(aq_inner(obj))
    parent_permissions = [r['name'] for r in \
                          parent.rolesOfPermission('Delete objects') \
                          if r['selected']]

    sm = getSecurityManager()
    newSecurityManager(None, UnrestrictedUser('god', '', ['Manager'], ''))
    obj.manage_permission('Delete objects',
                          roles = roles,
                          acquire=False)
    parent.manage_permission('Delete objects',
                          roles = parent_roles,
                          acquire=False)
    setSecurityManager(sm)
    return obj_permissions, parent_permissions


def move_normativa(obj, event, new_id=""):
    """Move a normativa to area/source/kind based on the source and
    kind fields.
    """

    # Disable security for a bit
    objdel_roles, parentdel_roles = allow_delete_object(obj, \
        ["Editor", "Metadata Editor", "Manager"], \
        ["Editor", "Metadata Editor", "Manager"])

    # Look for the area the normativa belongs to
    parent = area = aq_parent(aq_inner(obj))
    while not interfaces.IArea.providedBy(area) and not ISite.providedBy(area):
        area = aq_parent(aq_inner(area))

    # If we reached the portal root, we have nothing to do
    if ISite.providedBy(area):
        return

    source_id = normalizeString(obj.getSource(), obj)

    if source_id not in area.objectIds():
        _createObjectByType('Folder', area, id=source_id,
                             title=obj.getSource())
        #non Managers can't set the title :S
        source_object = getattr(area, source_id, None)
        if source_object is not None and not source_object.Title():
            source_object.setTitle(obj.getSource())

    source = getattr(area, source_id)
    alsoProvides(source, INonStructuralFolder)
    source.reindexObject()

    #reindex area field
    obj.setArea(area.id)
    obj.reindexObject(idxs=['getArea'])

    kind_id = normalizeString(obj.getKind(), obj)

    if kind_id not in source.objectIds():
        _createObjectByType('Large Plone Folder', source, id=kind_id,
                             title=obj.getKind())
        #non Managers can't set the title :S
        kind_object = getattr(source, kind_id, None)
        if kind_object is not None and not kind_object.Title():
            kind_object.setTitle(obj.getKind())

    kind = getattr(source, kind_id)
    alsoProvides(kind, INonStructuralFolder)
    kind.reindexObject()


    # Check if object id exists on target folder. Generate one that
    # does not exist in that case.
    target_ids = kind.objectIds()

    if new_id:
        new_object_id = new_id
        org_object_id = new_id
    else:
        new_object_id = obj.id
        org_object_id = obj.id

    if new_object_id in target_ids:
        suffix = 1
        new_object_id = org_object_id + "_1"
        while new_object_id in target_ids:
            suffix = suffix + 1
            new_object_id = org_object_id + '_' + str(suffix)

    # Set the newly generated id before moving the object
    obj.setId(new_object_id)

    # Copy and paste the normativa
    cb_copy_data = parent.manage_cutObjects([obj.id])
    kind.manage_pasteObjects(cb_copy_data)

    # Enable security
    res = allow_delete_object(obj, objdel_roles, parentdel_roles)
    assert(res, (objdel_roles, parentdel_roles))

##/code-section module-footer




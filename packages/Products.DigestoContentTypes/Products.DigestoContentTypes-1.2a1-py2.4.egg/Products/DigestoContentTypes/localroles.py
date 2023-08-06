from plone.app.workflow.interfaces import ISharingPageRole
from zope.interface import implements

from Products.DigestoContentTypes import DigestoContentTypesMessageFactory as _


class MetadataEditorRole(object):
    implements(ISharingPageRole)

    title = _(u"title_can_edit_metadata", default=u"Can edit metadata")
    required_permission = None

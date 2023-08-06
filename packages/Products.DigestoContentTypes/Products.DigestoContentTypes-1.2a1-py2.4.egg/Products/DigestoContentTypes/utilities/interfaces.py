from zope.interface import Interface
from zope.app.container.constraints import contains

from zope import schema

from Products.DigestoContentTypes import DigestoContentTypesMessageFactory as _


class INormativaTypes(Interface):
    """Normativa Types.
    """

    types = schema.List(title=_(u'Normativa Types'),
                           description=_(u'Normativa Types'),
                           required=False,
                           value_type=schema.TextLine(title=u'Type'))


    def get_types():
        """ Returns the types as a list of utf-8 encoded strings into ascii.
            Plone needs this kind of strings, while the input widget is managed
            with Zope 3 stuff like formlib, and it seems to prefer utf-8 strings
            instead. :S
        """


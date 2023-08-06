# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements

from plone.app.controlpanel.form import ControlPanelForm
from Products.DigestoContentTypes import DigestoContentTypesMessageFactory as _
from Products.DigestoContentTypes.browser.widget import NormativaDynamicSequenceWidget
from Products.DigestoContentTypes.utilities.interfaces import INormativaTypes

def normativa_types_settings(context):
    """Adapter factory"""
    return getUtility(INormativaTypes)


class NormativaTypesControlPanel(ControlPanelForm):
    """Control panel form view for the normativa types management.
    """

    form_fields = form.FormFields(INormativaTypes)
    form_fields['types'].custom_widget = NormativaDynamicSequenceWidget

    form_name = _(u"Normativa Types Management")
    label = _(u"Normativa Types Management")
    description = _(u"Please enter Normativa Types")

    def _on_save(self, data):
        nt = getUtility( INormativaTypes )
        nt.types.sort()


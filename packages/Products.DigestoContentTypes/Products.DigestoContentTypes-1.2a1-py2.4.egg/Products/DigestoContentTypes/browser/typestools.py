# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.interface import implements

from Products.Archetypes.utils import DisplayList
from Products.DigestoContentTypes import DigestoContentTypesMessageFactory as _
from Products.DigestoContentTypes.utilities.interfaces import INormativaTypes
from Products.Five.browser import BrowserView

from Products.CMFPlone.utils import normalizeString

from interfaces import ITypesTools
from Products.CMFCore.utils import getToolByName
import time

from plone.app.kss.plonekssview import PloneKSSView
from plone.app.kss.interfaces import IPloneKSSView
from Acquisition import aq_inner

class TypesTools(BrowserView):
    implements(ITypesTools)

    def get_vocabulary_for(self, subfield, instance=None, req_kind=None, req_source=None, include_current=False):
        """A hack for returning Normativa Types Display List from the utility to ATExtensions"""

        if subfield == 'kinds':
            # Returns all types of normativas.
            nt = getUtility( INormativaTypes )
            ret = [(a,a) for a in nt.get_types()]
            return DisplayList(tuple(ret))

        if subfield == 'area_kinds':
            # Returns the normativa types from the area in the instance
            # parameter.
            def source_index(sources, source):
                i = 0
                while i < len(sources):
                    if sources[i].get('source') == source:
                        return i
                    i = i + 1
                return -1

            nt = getUtility( INormativaTypes )


            source = req_source or instance.getSource()
            if source:
                try:
                    if include_current:
                        # Even when it's not in the area, we initially
                        # show the object type in the dropdown
                        kind = req_kind or instance.getKind()
                        ret = [(a,a) for a in nt.get_types() if a == kind or a in instance.sources[source_index(instance.sources, source)].get('kinds')]
                    else:
                        ret = [(a,a) for a in nt.get_types() if a in instance.sources[source_index(instance.sources, source)].get('kinds')]
                except IndexError:
                    ret = []
            else:
                ret = [(a,a) for a in nt.get_types()]

            return DisplayList(tuple([('','')] + ret))

        if subfield == 'area_sources':
            # Returns the normativa types from the area in the instance
            # parameter depending on the value of 'kind' in that same
            # area.
            kind = req_kind or instance.getKind()

            if kind:
                sources = [(b.get('source'), b.get('source')) for b in instance.sources if kind in b.get('kinds')]
                source = req_source or instance.getSource()
                if include_current and source and not (source, source) in sources:
                    # Even when it's not in the area, we initially
                    # show the object type in the dropdown (if not
                    # empty).
                    sources = [(source, source)] + sources
                return DisplayList(tuple([('','')] + sources ))
            else:
                sources = [(b.get('source'), b.get('source')) for b in instance.sources]
                source = instance.getSource()
                if include_current and source and not (source, source) in sources:
                    # Even when it's not in the area, we initially
                    # show the object type in the dropdown (if not
                    # empty).
                    sources = [(source, source)] + sources
                return DisplayList(tuple([('','')] + sources))


    def get_years(self):
        values = range(1970,time.localtime()[0] + 1)
        values.reverse()
        return values

    def get_areas(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        return portal_catalog.searchResults(portal_type = 'Area', sort_on = 'sortable_title')

    def get_area_emails(self, area):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        if area is None:
            return []
        try:
            a = getattr(portal, area)
        except:
            return []
        return a.getAddressBook()

    def get_kinds(self):
        nt = getUtility( INormativaTypes )
        return nt.types

    def get_normalized_kinds(self):
        nt = getUtility( INormativaTypes )
        return nt.get_types()


class KSSModifyView(PloneKSSView):

    implements(IPloneKSSView)

    def kssModifyOtherField(self, fieldname, source, kind):

        instance = aq_inner(self.context)

        field = instance.getField(fieldname)
        self.getCommandSet('digestocontenttypes').modifyFields(fieldname, source, kind)
        return self.render()

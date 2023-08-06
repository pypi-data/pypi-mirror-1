# -*- coding: utf-8 -*-
from kss.core.kssview import CommandSet

from Acquisition import aq_inner, aq_parent

from zope.app.component.interfaces import ISite
from zope.component import getUtility
from Products.DigestoContentTypes.content.interfaces import IArea
from Products.DigestoContentTypes.utilities.interfaces import INormativaTypes

class DigestoContentTypesCommands(CommandSet):

    __allow_access_to_unprotected_subobjects__ = 1


    def modifyFields(self, fieldname, source, kind):
        """Modifies the html code of the normativa source and kind dropdowns"""
        context = aq_inner(self.context)
        ksscore = self.getCommandSet('core')
        if fieldname == 'source':
            # Look for the area the normativa belongs to
            area = aq_parent(aq_inner(context))
            while not IArea.providedBy(area) and not ISite.providedBy(area):
                area = aq_parent(aq_inner(area))

            # If we reached the portal root, we have nothing to do
            if ISite.providedBy(area):
                return

            area_sources = area.sources
            types = []
            if source:
                for items in area_sources:
                    if items['source'] == source:
                        types = items['kinds']
                        break
            else:
                nt = getUtility( INormativaTypes )
                types = nt.get_types()

            selector = ksscore.getHtmlIdSelector('kind')

            kind_html = u'<select name="kind" id="kind" class="sourceorkind">\
                         <option value=""></option>'

            if source:
                for item in types:
                    if item == kind:
                        kind_html += u'<option selected="selected" value="%s">%s</option>' % (item.decode('utf-8'),item.decode('utf-8'))
                    else:
                        kind_html += u'<option value="%s">%s</option>' % (item.decode('utf-8'),item.decode('utf-8'))
            else:
                for item in types:
                    if item == kind:
                        kind_html += u'<option selected="selected" value="%s">%s</option>' % (item.decode('utf-8'),item.decode('utf-8'))
                    else:
                        kind_html += u'<option value="%s">%s</option>' % (item.decode('utf-8'),item.decode('utf-8'))

            kind_html += u'</select>'

            ksscore.replaceHTML(selector, kind_html )

            selector = ksscore.getHtmlIdSelector('deletedsource')
            ksscore.replaceInnerHTML(selector, u'' ) 

            selector = ksscore.getHtmlIdSelector('disallowedkind')
            ksscore.replaceInnerHTML(selector, u'' ) 

        elif fieldname == 'kind':

            # Look for the area the normativa bolongs to
            area = aq_parent(aq_inner(context))
            while not IArea.providedBy(area) and not ISite.providedBy(area):
                area = aq_parent(aq_inner(area))

            # If we reached the portal root, we have nothing to do
            if ISite.providedBy(area):
                return

            area_sources = area.sources
            sources = []
            for items in area_sources:
                if not kind or kind in items['kinds']:
                    sources.append(items['source'])

            source_html = u'<select name="source" id="source" class="sourceorkind">\
                           <option value=""></option>'

            for item in sources:
                if item == source:
                    source_html += u'<option value="%s" selected="selected">%s</option>' % (item.decode('utf-8'),item.decode('utf-8'))
                else:
                    source_html += u'<option value="%s">%s</option>' % (item.decode('utf-8'),item.decode('utf-8'))

            source_html += u'</select>'

            selector = ksscore.getHtmlIdSelector('source')
            ksscore.replaceHTML(selector, source_html ) 

            selector = ksscore.getHtmlIdSelector('disallowedkind')
            ksscore.replaceInnerHTML(selector, u'' ) 

            selector = ksscore.getHtmlIdSelector('deletedsource')
            ksscore.replaceInnerHTML(selector, u'' ) 



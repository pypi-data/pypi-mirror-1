from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from Acquisition import aq_inner

from Products.DigestoContentTypes import DigestoContentTypesMessageFactory as _

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class INormativaSearchPortlet(IPortletDataProvider):
    """ A portlet displaying a (live) search box
    """

    enableLivesearch = schema.Bool(
            title = _(u"Enable LiveSearch"),
            description = _(u"Enables the LiveSearch feature, which shows "
                             "live results if the browser supports "
                             "JavaScript."),
            default = True,
            required = False)

class Assignment(base.Assignment):
    implements(INormativaSearchPortlet)

    def __init__(self, enableLivesearch=True):
        self.enableLivesearch=True

    @property
    def title(self):
        return _(u"Search")


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('normativasearchportlet.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

        portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()
        self.typestools = getMultiAdapter((context, request), name=u'typestools')

    def enable_livesearch(self):
        return self.data.enableLivesearch

    def search_form(self):
        return '%s/normativa_search_form' % self.portal_url

    def search_action(self):
        return '%s/normativa_search' % self.portal_url

    def years(self):
        return self.typestools.get_years()

    def areas(self):
        return self.typestools.get_areas()

class AddForm(base.AddForm):
    form_fields = form.Fields(INormativaSearchPortlet)
    label = _(u"Add Search Portlet")
    description = _(u"This portlet shows a search box.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(INormativaSearchPortlet)
    label = _(u"Edit Search Portlet")
    description = _(u"This portlet shows a search box.")







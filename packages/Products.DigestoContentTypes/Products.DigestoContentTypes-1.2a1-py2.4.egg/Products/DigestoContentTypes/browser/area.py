# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.interface import implements

from Products.DigestoContentTypes import DigestoContentTypesMessageFactory as _
from Products.Five.browser import BrowserView

from interfaces import IAbbreviationsView
from Products.CMFCore.utils import getToolByName
from DateTime.DateTime import DateTime

class AbbreviationsView(BrowserView):
    implements(IAbbreviationsView)


class SetAbbreviations(BrowserView):
    implements(IAbbreviationsView)

    def __call__(self):

        context = self.context
        request = self.request

        submit = request.get('submit', False)
        cancel = request.get('form.button.cancel', False)

        permission = context.portal_membership.checkPermission('Manage portal content', context)

        if permission and submit:
            abbreviations = request.get('abbreviations', [])

            new_abbreviations = {}

            for item in abbreviations:
            #     if not item['value']:
            #         message = _(u'No pueden dejarse abreviaturas en blanco.')
            #         context.plone_utils.addPortalMessage(message, 'error')
            #         return state.set(status='failure')
                new_abbreviations[(item['source'], item['kind'])] = item['value']

            context.setAbbreviations(new_abbreviations)

            context.plone_utils.addPortalMessage(_(u'Changes saved.'))

        elif not permission:
            context.plone_utils.addPortalMessage(_(u'Not enough permissions.'))

        request.response.redirect('view')


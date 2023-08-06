# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.DigestoContentTypes.utilities.interfaces import INormativaTypes
from Products.DigestoContentTypes.utilities.types import NormativaTypes


def afterInstall(self, reinstall, product):

    portal = getToolByName(self,'portal_url').getPortalObject()
    sm = portal.getSiteManager()
    if not sm.queryUtility(INormativaTypes):
        sm.registerUtility(NormativaTypes(), INormativaTypes)
        nt = sm.getUtility(INormativaTypes)
        nt.types = [u'Ley', u'Ordenanza', u'Decreto',
                    unicode('Resolución','utf-8')]

    portal_setup = getToolByName(self, 'portal_setup')
    profile = 'profile-Products.DigestoContentTypes:extra'
    portal_setup.runAllImportStepsFromProfile(profile)

# -*- coding: utf-8 -*-

import os
import unittest

from zope.component import getMultiAdapter

from Products.DigestoContentTypes.tests.base import DigestoContentTypesTestCase, test_home

from DateTime import DateTime
from zope.event import notify

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.event import ObjectInitializedEvent, ObjectEditedEvent

# Import the class to test
from Products.DigestoContentTypes.content.Normativa import Normativa

# Import the view
from Products.DigestoContentTypes.browser.searchtools import SearchTools

class TestSearch(DigestoContentTypesTestCase):
    """ Testing the DigestoContentTypes Search.
    """

    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')
        self.quickinstaller = getToolByName(self.portal, 'portal_quickinstaller')

        self.setRoles(('Manager',))
        input_dir = os.path.join(test_home, 'input')
        input = open(os.path.join(input_dir, 'test2.pdf'), 'rb')

        #creo areas
        self.portal.invokeFactory('Area', 'area1')
        self.portal.invokeFactory('Area', 'area2')

        #creo normativas
        self.portal.area1.invokeFactory('Normativa', 'normativa1', source='source1', kind='kind1', title='normativa1', file=input, date=DateTime(2008,4,4), number='123')
        notify(ObjectInitializedEvent(self.portal.area1.normativa1))

        self.portal.area2.invokeFactory('Normativa', 'normativa2', source='source2', kind='kind2', title='normativa2', file=input, date=DateTime(2008,5,5), number='456')
        notify(ObjectInitializedEvent(self.portal.area2.normativa2))

        self.portal.area2.invokeFactory('Normativa', 'normativa3', source='source2', kind='kind1', title='normativa3', file=input, date=DateTime(2007,5,5), number='789')
        notify(ObjectInitializedEvent(self.portal.area2.normativa3))

        self.portal.area1.invokeFactory('Normativa', 'normativa4', source='source2', kind='Ley', title='normativa4', file=input, date=DateTime(2007,5,5), number='444')
        notify(ObjectInitializedEvent(self.portal.area1.normativa4))

        #diccionario para acceder a las normativas
        self.normativas = {'normativa1': self.portal.area1.source1.kind1.normativa1,
                           'normativa2': self.portal.area2.source2.kind2.normativa2,
                           'normativa3': self.portal.area2.source2.kind1.normativa3,
                           'normativa4': self.portal.area1.source2.ley.normativa4,
                          }

        #creo relaciones entre normativas
        self.normativas['normativa1'].setModifies(self.normativas['normativa2'].UID())
        self.normativas['normativa1'].setRepeals(self.normativas['normativa2'].UID())
        self.normativas['normativa1'].reindexObject()
        self.normativas['normativa2'].reindexObject()


        #esto se hace en el afterInstall de digesto.policy
        from Products.DigestoContentTypes.utilities.interfaces import INormativaTypes
        from Products.DigestoContentTypes.utilities.types import NormativaTypes

        sm = self.portal.getSiteManager()
        if not sm.queryUtility(INormativaTypes):
            sm.registerUtility(NormativaTypes(),
                                INormativaTypes)
            nt = sm.getUtility(INormativaTypes)
            nt.types = [u'Ley', u'Ordenanza', u'Decreto', unicode('Resolución','utf-8')]

    def test_search_by_area(self):
        """ Test the search of Normativas by Area
        """

        request = self.portal.REQUEST
        request['getArea'] = 'area2'
        search_view = getMultiAdapter((self.portal, request,), name="searchtools")
        results = search_view.search_results(request)
        area_uids = [self.normativas['normativa2'].UID(), self.normativas['normativa3'].UID()]
        area_uids.sort()
        self.failUnless(len(results) == 2)
        results_uids = [results[0].getObject().UID(), results[1].getObject().UID()]
        results_uids.sort()
        self.failUnless(results_uids == area_uids)


    def test_search_by_number_normativa(self):
        """ Test the search of Normativas by Normativa Number
        """

        request = self.portal.REQUEST
        request['getNumber'] = '789'
        request['numero_normativa'] = 'number'
        search_view = getMultiAdapter((self.portal, request,), name="searchtools")
        results = search_view.search_results(request)
        number_uids = [self.normativas['normativa3'].UID()]
        number_uids.sort()
        self.failUnless(len(results) == 1)
        results_uids = [results[0].getObject().UID()]
        results_uids.sort()
        self.failUnless(results_uids == number_uids)

    def test_search_by_number_modifies(self):
        """ Test the search of Normativas by Modifies number
        """
        request = self.portal.REQUEST
        request['getNumber'] = '456'
        request['numero_normativa'] = 'modifies'
        search_view = getMultiAdapter((self.portal, request,), name="searchtools")
        results = search_view.search_results(request)
        number_uids = [self.normativas['normativa1'].UID()]
        number_uids.sort()
        self.failUnless(len(results) == 1)
        results_uids = [results[0].getObject().UID()]
        results_uids.sort()
        self.failUnless(results_uids == number_uids)

    def test_search_by_number_repeals(self):
        """ Test the search of Normativas by Repeals number
        """
        request = self.portal.REQUEST
        request['getNumber'] = '456'
        request['numero_normativa'] = 'repeals'
        search_view = getMultiAdapter((self.portal, request,), name="searchtools")
        results = search_view.search_results(request)
        number_uids = [self.normativas['normativa1'].UID()]
        number_uids.sort()
        self.failUnless(len(results) == 1)
        results_uids = [results[0].getObject().UID()]
        results_uids.sort()
        self.failUnless(results_uids == number_uids)

    def test_search_by_number_repealedby(self):
        """ Test the search of Normativas by Repealedby number
        """
        request = self.portal.REQUEST
        request['getNumber'] = '123'
        request['numero_normativa'] = 'isrepealedby'
        search_view = getMultiAdapter((self.portal, request,), name="searchtools")
        results = search_view.search_results(request)
        number_uids = [self.normativas['normativa2'].UID()]
        number_uids.sort()
        self.failUnless(len(results) == 1)
        results_uids = [results[0].getObject().UID()]
        results_uids.sort()
        self.failUnless(results_uids == number_uids)

    def test_search_by_year(self):
        """ Test the search of Normativas by year
        """
        request = self.portal.REQUEST
        request['getDate'] = '2008'
        search_view = getMultiAdapter((self.portal, request,), name="searchtools")
        results = search_view.search_results(request)
        number_uids = [self.normativas['normativa1'].UID(), self.normativas['normativa2'].UID()]
        number_uids.sort()
        self.failUnless(len(results) == 2)
        results_uids = [results[0].getObject().UID(), results[1].getObject().UID()]
        results_uids.sort()
        self.failUnless(results_uids == number_uids)

    def test_search_by_kind(self):
        """ Test the search of Normativas by kind
        """
        request = self.portal.REQUEST
        request['getKind'] = 'kind1'
        search_view = getMultiAdapter((self.portal, request,), name="searchtools")
        results = search_view.search_results(request)
        number_uids = [self.normativas['normativa1'].UID(), self.normativas['normativa3'].UID()]
        number_uids.sort()
        self.failUnless(len(results) == 2)
        results_uids = [results[0].getObject().UID(), results[1].getObject().UID()]
        results_uids.sort()
        self.failUnless(results_uids == number_uids)

    def test_search_id_in_searchabletext(self):
        """ Test the search of Normativas by number and year in the searchable text
        """
        request = self.portal.REQUEST
        request['SearchableText'] = '456/08'
        search_view = getMultiAdapter((self.portal, request,), name="searchtools")
        results = search_view.search_results(request)
        number_uids = [self.normativas['normativa2'].UID()]
        number_uids.sort()
        self.failUnless(len(results) == 1)
        results_uids = [results[0].getObject().UID()]
        results_uids.sort()
        self.failUnless(results_uids == number_uids)

        request['SearchableText'] = '789-07'
        search_view = getMultiAdapter((self.portal, request,), name="searchtools")
        results = search_view.search_results(request)
        number_uids = [self.normativas['normativa3'].UID()]
        number_uids.sort()
        self.failUnless(len(results) == 1)
        results_uids = [results[0].getObject().UID()]
        results_uids.sort()
        self.failUnless(results_uids == number_uids)

        request['SearchableText'] = '123/2008'
        results = search_view.search_results(request)
        number_uids = [self.normativas['normativa1'].UID()]
        number_uids.sort()
        self.failUnless(len(results) == 1)
        results_uids = [results[0].getObject().UID()]
        results_uids.sort()
        self.failUnless(results_uids == number_uids)

        request['SearchableText'] = '444-2007'
        results = search_view.search_results(request)
        number_uids = [self.normativas['normativa4'].UID()]
        number_uids.sort()
        self.failUnless(len(results) == 1)
        results_uids = [results[0].getObject().UID()]
        results_uids.sort()
        self.failUnless(results_uids == number_uids)

        request['SearchableText'] = 'Ley 444-2007'
        results = search_view.search_results(request)
        number_uids = [self.normativas['normativa4'].UID()]
        number_uids.sort()
        self.failUnless(len(results) == 1)
        results_uids = [results[0].getObject().UID()]
        results_uids.sort()
        self.failUnless(results_uids == number_uids)

    def test_search_attachments(self):
        """Test that if we search for a word that is in an attachment,
        then the normativa that contains it is in the results.
        """
        input_dir = os.path.join(test_home, 'input')
        attachment = open(os.path.join(input_dir, 'test1.pdf'), 'rb')
        self.normativas['normativa1'].invokeFactory('Attachment', 'adjunto1',
                                                    file=attachment)
        self.normativas['normativa1'].adjunto1.reindexObject()

        #We are going to search for the word 'file' which only appears
        #in the test1.pdf file
        request = self.portal.REQUEST
        request['SearchableText'] = 'file'
        search_view = getMultiAdapter((self.portal, request,), name="searchtools")
        results = search_view.search_results(request)

        auid = self.normativas['normativa1'].adjunto1.UID()
        results_uids = [i.getObject().UID() for i in  results]
        self.failIf(auid not in results_uids)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSearch))
    return suite

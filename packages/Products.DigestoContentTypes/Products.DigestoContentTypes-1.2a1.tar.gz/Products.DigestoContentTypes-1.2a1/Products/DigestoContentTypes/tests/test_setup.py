"""Test product installation
"""

import unittest
from Products.DigestoContentTypes.tests.base import DigestoContentTypesTestCase

from Products.CMFCore.utils import getToolByName

class TestDCTSetup(DigestoContentTypesTestCase):
    """ Testing the DigestoContentTypes setup.
    """

    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.placeful_workflow = getToolByName(self.portal,
                                               'portal_placeful_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')
        self.quickinstaller = getToolByName(self.portal,
                                            'portal_quickinstaller')
        self.catalog = getToolByName(self.portal, 'portal_catalog')

    def test_workflows_installed(self):
        """Test that the workflows for Normativa and Area are created and
        properly associated.
        """
        self.failUnless('normativa_workflow' in self.workflow.objectIds())
        self.failUnless('area_workflow' in self.workflow.objectIds())
        self.assertEquals(self.workflow.getChainForPortalType('Normativa'),
                          ('normativa_workflow',))
        self.assertEquals(self.workflow.getChainForPortalType('Area'),
                          ('area_workflow',))

    def test_metadata_editor_role(self):
        """Test that the Metadata Editor role in available in the site
        after the install.
        """
        self.failUnless("Metadata Editor", self.portal.validRoles())

    def test_area_placeful_workflow_policy(self):
        """Test that the placeful workflow policy for areas is installed.
        """
        area_wf_id = 'area_placeful_workflow'
        self.failUnless(area_wf_id in self.placeful_workflow)
        area_wf = getattr(self.placeful_workflow, area_wf_id)
        self.assertEquals(area_wf.getChainFor('Folder'),
                          ('area_workflow',))
        self.assertEquals(area_wf.getChainFor('Large Plone Folder'),
                          ('area_workflow',))
        self.assertEquals(area_wf.getChainFor('Normativa'),
                          ('normativa_workflow',))

    def test_indexes_added(self):
        """Test that indexes are added at install time
        """
        indexes = (('getDate', 'DateIndex'),
                   ('getSource', 'FieldIndex'),
                   ('getNumber', 'FieldIndex'),
                   ('getRepeals', 'FieldIndex'),
                   ('getModifies', 'FieldIndex'),
                   ('getRepealedBy', 'FieldIndex'),
                   ('getKind', 'FieldIndex'),
                   ('getAbbreviation', 'FieldIndex'),
                   ('getArea', 'FieldIndex'),
                   ('getCudap', 'FieldIndex'),
                  )
        indexes = dict(indexes).keys()

        for index in indexes:
            self.failUnless(self.catalog.Indexes.get(index, None) is not None)

    def test_indexes_not_cleaned_on_reinstall(self):
        """Test that indexes are not cleaned on reinstall.
        """
        # Create a Normativa
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Area', 'area1')
        self.portal.area1.invokeFactory('Normativa', 'normativa1', number=112)

        # Make sure it gets cataloged
        self.portal.area1.normativa1.reindexObject()
        get_number_idx = self.catalog.Indexes['getNumber']
        self.assertEquals(get_number_idx.numObjects(), 1)

        # Reinstall the product and make sure that it is still
        # catalogued.
        self.quickinstaller.reinstallProducts(['DigestoContentTypes'])
        self.assertEquals(get_number_idx.numObjects(), 1)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDCTSetup))
    return suite

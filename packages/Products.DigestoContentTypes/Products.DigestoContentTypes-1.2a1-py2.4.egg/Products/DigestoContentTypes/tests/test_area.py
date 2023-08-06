import unittest
from Products.DigestoContentTypes.tests.base import DigestoContentTypesTestCase

from Products.CMFCore.utils import getToolByName

# Import the class to test
from Products.DigestoContentTypes.content.Area import Area

class TestArea(DigestoContentTypesTestCase):
    """Testing the DigestoContentTypes Area content type.
    """

    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')
        self.quickinstaller = getToolByName(self.portal, \
            'portal_quickinstaller')


    def test_type_installed(self):
        """Test that the Area content type exists.
        """
        area_fti = getattr(self.types, 'Area')
        self.assertEquals("Area", area_fti.title)


    def test_globally_allowed(self):
        """Test that Area is globally allowed.
        """
        area_fti = getattr(self.types, 'Area')
        self.failUnless(area_fti.global_allow)


    def test_allowed_content_types(self):
        """Test allowed content types inside an Area.
        """
        area_fti = getattr(self.types, 'Area')
        self.failUnless('Normativa' in area_fti.allowed_content_types)
        self.failUnless('Large Plone Folder' in area_fti.allowed_content_types)
        self.failUnless('Folder' in area_fti.allowed_content_types)
        self.failIf(len(area_fti.allowed_content_types) != 3)


    def test_field_names(self):
        """Test field names.
        """
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Area', 'area1')
        field_names = [i.getName() for i in self.portal.area1.schema.fields()]
        self.failIf('sources' not in field_names)
        self.failIf('addressBook' not in field_names)


    def test_add_permission(self):
        """Test that members cannot add an Area.
        """
        from AccessControl import Unauthorized
        self.setRoles(('Member',))
        self.failUnlessRaises(Unauthorized, self.portal.invokeFactory,
                              'Area', 'area1')


    def test_area_is_non_structural_folder(self):
        """Test that Area is a folderish type and that is non structural.
        """
        from Products.CMFPlone.interfaces import INonStructuralFolder
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Area', 'area1')
        self.failUnless(INonStructuralFolder.providedBy(self.portal.area1))


    def test_address_book_validator(self):
        """Check that all the items in the address book are actually valid email
        addresses.
        """
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Area', 'area1')
        validators = zip(*self.portal.area1.schema['addressBook'].validators)[0]
        validators = [i.name for i in validators]
        self.failUnless(validators is not None)
        self.failUnless('is_address_book' in validators)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestArea))
    return suite

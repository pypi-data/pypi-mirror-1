import os
import unittest
from Products.DigestoContentTypes.tests.base import DigestoContentTypesTestCase, test_home

from DateTime import DateTime
from zope.event import notify

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.event import ObjectInitializedEvent, ObjectEditedEvent

# Import the class to test
from Products.DigestoContentTypes.content.Normativa import Normativa

class TestNormativa(DigestoContentTypesTestCase):
    """Testing the DigestoContentTypes Normativa content type.
    """

    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')
        self.quickinstaller = getToolByName(self.portal, 'portal_quickinstaller')


    def test_type_installed(self):
        """Test that the Normativa content type exists.
        """
        normativa_fti = getattr(self.types, 'Normativa')
        self.assertEquals("Normativa", normativa_fti.title)


    def test_not_globally_allowed(self):
        """Test that Normativa is not globally allowed.
        """
        normativa_fti = getattr(self.types, 'Normativa')
        self.failIf(normativa_fti.global_allow)


    def test_allowed_content_types(self):
        """Test allowed content types inside an Normativa.
        """
        normativa_fti = getattr(self.types, 'Normativa')
        self.failUnless('Attachment' in normativa_fti.allowed_content_types)
        self.failIf(len(normativa_fti.allowed_content_types) != 1)


    def test_fields(self):
        """Test field names.
        """
        #self.setRoles(('Manager',))
        #self.portal.invokeFactory('Normativa', 'normativa1')
        #field_names = [i.getName() for i in self.portal.normativa1.schema.fields()]
        pass


    def test_required_fields(self):
        """Test required fields.
        """
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Area', 'area1')
        self.portal.area1.invokeFactory('Normativa', 'normativa1')
        required_fields = ['file', 'date', 'source', 'number', 'kind']

        object_fields = self.portal.area1.normativa1.schema.fields()

        for field in object_fields:
            self.failUnless((field.getName() in required_fields and field.required) or
                            (field.getName() not in required_fields and not field.required) )


    def test_add_permission(self):
        """Test that only managers can add an Normativa.
        """
        pass


    def test_normativa_is_non_structural_folder(self):
        """Test that Normativa is a folderish type and that is non structural.
        """
        from Products.CMFPlone.interfaces import INonStructuralFolder
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Area', 'area1')
        self.portal.area1.invokeFactory('Normativa', 'normativa1')
        self.failUnless(INonStructuralFolder.providedBy(self.portal.area1.normativa1))


    def test_normativa_title_after_create(self):
        """Test that the title is properly changed on creation.
        """
        self.setRoles(('Manager',))
        input_dir = os.path.join(test_home, 'input')
        input = open(os.path.join(input_dir, 'test2.pdf'), 'rb')
        self.portal.invokeFactory('Area', 'area1')

        #Title from input
        self.portal.area1.invokeFactory('Normativa', 'normativa1', source='Rector', kind='Decreto', title='Normativa 1', file=input, date=DateTime('2008/01/01'), number='123')
        notify(ObjectInitializedEvent(self.portal.area1.normativa1))
        self.portal.area1.rector.decreto.normativa1._renameAfterCreation()
        normativa = getattr(self.portal.area1.rector.decreto, '123_2008')
        self.failUnless(normativa.title_or_id() == 'Normativa 1')

        #Auto generated title
        self.portal.area1.invokeFactory('Normativa', 'normativa2', source='Rector', kind='Decreto', file=input, date=DateTime('2008/01/01'), number='345')
        notify(ObjectInitializedEvent(self.portal.area1.normativa2))
        self.portal.area1.rector.decreto.normativa2._renameAfterCreation()
        normativa = getattr(self.portal.area1.rector.decreto, '345_2008')
        self.failUnless(normativa.title_or_id() == 'Decreto 345/2008')

    def test_normativa_url(self):
        """Test that the normativa URL is site/area/source/kind after add.
        """
        self.setRoles(('Manager',))
        input_dir = os.path.join(test_home, 'input')
        input = open(os.path.join(input_dir, 'test2.pdf'), 'rb')
        self.portal.invokeFactory('Area', 'area1')
        self.portal.area1.invokeFactory('Normativa', 'normativa1', source='A source', kind='Kind', title='normativa1', file=input, date=DateTime(), number='123')

        notify(ObjectInitializedEvent(self.portal.area1.normativa1))

        try:
            source = getattr(self.portal.area1, 'a-source')
            norma = source.kind.normativa1
        except:
            norma = None

        target_url = self.portal.absolute_url() + '/area1/a-source/kind/normativa1'
        self.failIf(norma is None)
        self.assertEquals(norma.absolute_url(), target_url)


    def test_normativa_url_on_edit(self):
        """Test that the normativa URL changes properly on edition.
        """
        self.setRoles(('Manager',))
        input_dir = os.path.join(test_home, 'input')
        input = open(os.path.join(input_dir, 'test2.pdf'), 'rb')
        self.portal.invokeFactory('Area', 'area1')
        self.portal.area1.invokeFactory('Normativa', 'normativa1', source='A source', kind='Kind', title='normativa1', file=input, date=DateTime(), number='123')
        self.portal.area1.normativa1.setSource('Another source')
        self.portal.area1.normativa1.setKind('Another kind')

        notify(ObjectEditedEvent(self.portal.area1.normativa1))

        try:
            source = getattr(self.portal.area1, 'another-source')
            kind = getattr(source, 'another-kind')
            norma = getattr(kind, '123_'+str(DateTime().year()))
        except:
            norma = None

        target_url = self.portal.absolute_url() + '/area1/another-source/another-kind/'+'123_'+str(DateTime().year())
        self.failIf(norma is None)
        self.assertEquals(norma.absolute_url(), target_url)


    def test_type_folder_wstate(self):
        """Test workflow state of the type folder created on a normativa
        creation.
        """
        pass


    def test_source_folder_wstate(self):
        """Test workflow state of the source folder created on a normativa
        creation.
        """
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNormativa))
    return suite

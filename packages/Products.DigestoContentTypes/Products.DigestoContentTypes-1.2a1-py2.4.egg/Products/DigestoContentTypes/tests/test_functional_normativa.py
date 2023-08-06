import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing

from Testing import ZopeTestCase as ztc

from Products.DigestoContentTypes.tests.base import DigestoContentTypesFunctionalTestCase

def test_suite():
    return unittest.TestSuite([

        ## Test the back reference for the repeals field
        #ztc.ZopeDocFileSuite(
            #'tests/repealedby.txt', package='Products.DigestoContentTypes',
            #test_class=DigestoContentTypesFunctionalTestCase,
            #optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Test full text search
        ztc.ZopeDocFileSuite(
            'tests/fulltextsearch.txt', package='Products.DigestoContentTypes',
            test_class=DigestoContentTypesFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Test normativas sent by mail
        ztc.ZopeDocFileSuite(
            'tests/sendmail.txt', package='Products.DigestoContentTypes',
            test_class=DigestoContentTypesFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Test normativas created with duplicated ids
        ztc.ZopeDocFileSuite(
            'tests/duplicatedid.txt', package='Products.DigestoContentTypes',
            test_class=DigestoContentTypesFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Test area created with empty source
        ztc.ZopeDocFileSuite(
            'tests/requiredsource.txt', package='Products.DigestoContentTypes',
            test_class=DigestoContentTypesFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Test manage_attachment_upload preserve the file extension
        ztc.ZopeDocFileSuite(
            'tests/extensionattachments.txt', package='Products.DigestoContentTypes',
            test_class=DigestoContentTypesFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Test the rename of the attachments when the normativa is edited
        ztc.ZopeDocFileSuite(
            'tests/renameattachements.txt', package='Products.DigestoContentTypes',
            test_class=DigestoContentTypesFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

       ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

import unittest
from Testing import ZopeTestCase
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase
from Testing.ZopeTestCase import doctest

from Products.validation import validation

class TestValidators(ATSiteTestCase):

    def test_is_addressbook(self):
        valid_address_book = ('adress@something.com',
                              'another.address@test.com.ar',
                              'my_addres@domain.com',
                              'other-address@domain.tv')
        invalid_address_book1 = ('adress@something.com',
                                 'another.address@test.com.ar',
                                 '@something.com')
        invalid_address_book2 = ('adress@something.com',
                                 'address1@domain.com anoher@domain.com',
                                 'another.address@test.com.ar')
        invalid_address_book3 = ('adresssomething.com',
                                 'address1@domain.com',
                                 'another.address@test.com.ar')
        invalid_address_book4 = ('adresss@omething.com',
                                 'address1 domain.com',
                                 'another.address@test.com.ar')

        v = validation.validatorFor('is_address_book')
        self.failUnlessEqual(v(valid_address_book), 1)
        self.failIfEqual(v(invalid_address_book1), 1)
        self.failIfEqual(v(invalid_address_book2), 1)
        self.failIfEqual(v(invalid_address_book3), 1)
        self.failIfEqual(v(invalid_address_book4), 1)

    def test_is_dossiernumber_list(self):
        valid_dossier_numbers = ('12-23-12345',
                                 'EXP-UNC:0000005/2008',
                                 'PROY-SIU:0000003/2008')

        invalid_dossier_numbers1 = ('12-23-12345',
                                    'exp-unc:0000005/2008',
                                    'PROY-SIU:0000003/2008')

        invalid_dossier_numbers2 = ('123-23-12345',
                                    'EXP-UNC:0000005/2008',
                                    'PROY-SIU:0000003/2008')

        invalid_dossier_numbers3 = ('12-2-12345',
                                    'EXP-UNC:0000005/2008',
                                    'PROY-SIU:0000003/2008')

        invalid_dossier_numbers4 = ('12-23-123456',
                                    'EXP-UNC:0000005/2008',
                                    'PROY-SIU:0000003/2008')

        invalid_dossier_numbers5 = ('123-23-12345',
                                    'EXP-UNC:0000005/2008',
                                    'PROY-SIUM:0000003/2008')

        invalid_dossier_numbers6 = ('123-23-12345',
                                    'EXP-UNC:0000005/2008',
                                    'PROY-SI:0000003/2008')

        invalid_dossier_numbers7 = ('123-23-12345',
                                    'EXP-UNC:000005/2008',
                                    'PROY-SI:0000003/2008')

        invalid_dossier_numbers8 = ('123-23-12345',
                                    'EXP-UNC:00000005/2008',
                                    'PROY-SI:0000003/2008')

        invalid_dossier_numbers9 = ('123-23-12345',
                                    'EXP-UNC:0000005/2008',
                                    'PROY-SI:0000003/20008')


        v = validation.validatorFor('is_dossier_number_list')
        self.failUnlessEqual(v(valid_dossier_numbers), 1)
        self.failIfEqual(v(invalid_dossier_numbers1), 1)
        self.failIfEqual(v(invalid_dossier_numbers2), 1)
        self.failIfEqual(v(invalid_dossier_numbers3), 1)
        self.failIfEqual(v(invalid_dossier_numbers4), 1)
        self.failIfEqual(v(invalid_dossier_numbers5), 1)
        self.failIfEqual(v(invalid_dossier_numbers6), 1)
        self.failIfEqual(v(invalid_dossier_numbers7), 1)
        self.failIfEqual(v(invalid_dossier_numbers8), 1)
        self.failIfEqual(v(invalid_dossier_numbers9), 1)

    def test_is_cudap_number(self):
        valid_cudap_numbers = ('RESO-ABC:0823561/2008',
                               'RESOREC-DDD:0003657/2008',
                               'RESODEC-LAA:1234567/2002',
                               'RESOHCD-BBB:0000000/1992',
                               'RESOHCS-NAN:3246172/2222',
                               'RESOSEC-LOL:6542937/2334',
                               'ORDEHCD-CCC:7536291/1234',
                               'ORDEHCS-DOT:0019283/2009'
                               )

        invalid_cudap_numbers = ('RES-ABC:0823561/2008',
                                 'reso-abc:0823561/2008',
                                 'RESO-abc:0823561/2008',
                                 'RESO-ABC:926374/2008',
                                 'RESO-ABC:7283654/200',
                                 'mal'
                                 )


        v = validation.validatorFor('is_cudap_number')
        for i in valid_cudap_numbers:
            self.failUnlessEqual(v(i), 1, '%s should validate correctly' %str(i))
        for i in invalid_cudap_numbers:
            self.failIfEqual(v(i), 1, '%s should NOT validate' %str(i))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestValidators))
    return suite

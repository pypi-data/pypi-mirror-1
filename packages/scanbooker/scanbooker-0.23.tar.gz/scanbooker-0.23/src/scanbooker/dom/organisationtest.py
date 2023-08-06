import unittest
from scanbooker.dom.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(TestOrganisation),
    ]
    return unittest.TestSuite(suites)


class TestOrganisation(TestCase):

    def setUp(self):
        self.organisation = self.registry.organisations.create(formalName='Example Organisation')

    def tearDown(self):
        self.organisation.delete()
    
    def test_attributes(self):
        self.failUnless(self.organisation)
        self.failUnlessEqual(self.organisation.formalName, 'Example Organisation')

    def test_getLabelValue(self):
        self.failUnlessEqual(self.organisation.getLabelValue(), 'Example Organisation')
        self.organisation.nickname = 'test example'
        self.failUnlessEqual(self.organisation.getLabelValue(), 'test example')


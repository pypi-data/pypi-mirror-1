import unittest
from scanbooker.exceptions import *
from scanbooker.dom.testunit import TestCase
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestPerson),
    ]
    return unittest.TestSuite(suites)

class TestPerson(TestCase):

    name = 'testperson'
    roleName = 'Staff'
    fullname = 'Test Person'

    def setUp(self):
        self.role = self.registry.roles[self.roleName]
        self.researcher = self.registry.researchers.create(
            realname=self.fullname,
        )
        self.person = self.registry.persons.create(
            self.name,
            fullname=self.fullname,
            role=self.role,
            researcher=self.researcher,
        )

    def tearDown(self):
        try:
            self.person.delete()
        finally:
            self.researcher.delete()
    
    def test_attributes(self):
        self.failUnlessEqual(self.person.name, self.name)
        self.failUnlessEqual(self.person.fullname, self.fullname)
        self.failUnlessEqual(self.person.role, self.role)
        self.failUnlessEqual(self.person.researcher, self.researcher)



import unittest
from scanbooker.exceptions import *
from scanbooker.dom.testunit import TestCase
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestResearcher),
    ]
    return unittest.TestSuite(suites)

class TestResearcher(TestCase):

    realname = 'Test Researcher'
    roleName = 'Staff'

    def setUp(self):
        self.role = self.registry.roles[self.roleName]
        self.researcher = self.registry.researchers.create(
            realname=self.realname,
            theory=True,
            practical=True,
            AED=True,
        )
        self.researcher2 = None
        self.researcher3 = None
        self.researcher4 = None
        self.researcher5 = None

    def tearDown(self):
        self.researcher.delete()
        if self.researcher2:
            self.researcher2.delete()
        if self.researcher3:
            self.researcher3.delete()
        if self.researcher4:
            self.researcher4.delete()
        if self.researcher5:
            self.researcher5.delete()

    def test_attributes(self):
        self.failUnlessEqual(self.researcher.realname, self.realname)
        self.failUnlessEqual(self.researcher.initials, "TR")

    def test_isTrained(self):
        self.failUnless(self.researcher.isTrained())
        self.researcher.theory = False
        self.researcher.save()
        self.failIf(self.researcher.isTrained())

    def test_uniqueInitials(self):
        find = self.registry.researchers.findDomainObjects
        self.researcher2 = self.registry.researchers.create(
            realname=self.realname,
        )
        initials = self.researcher2.initials
        self.failUnlessEqual(initials, "TR1")
        self.failUnless(len(find(initials=initials)), 1)
        self.researcher3 = self.registry.researchers.create(
            realname=self.realname,
        )
        initials = self.researcher3.initials
        self.failUnlessEqual(initials, "TR2")
        self.failUnless(len(find(initials=initials)), 1)
        self.researcher4 = self.registry.researchers.create(
            realname=self.realname,
        )
        initials = self.researcher4.initials
        self.failUnlessEqual(initials, "TR3")
        self.failUnless(len(find(initials=initials)), 1)
        self.researcher5 = self.registry.researchers.create(
            realname='',
        )
        initials = self.researcher5.initials
        self.failUnlessEqual(initials, "ANO")
        self.failUnless(len(find(initials=initials)), 1)
        self.researcher5.initials = 'tr3'
        self.researcher5.save()
        initials = self.researcher5.initials
        self.failUnlessEqual(initials, "TR4")


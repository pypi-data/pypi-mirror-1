import unittest
from scanbooker.exceptions import *
from scanbooker.dom.testunit import TestCase
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestProject),
    ]
    return unittest.TestSuite(suites)


class TestProject(TestCase):

    title = 'My Great Test Project'
    nickname = 'test'
    preparationMinutes = 30
    leader = None
    leaderName = 'Sonia Bishop'
    code1 = '555-444'
    code2 = '444-333'

    def setUp(self):
        self.leader = self.registry.researchers.findSingleDomainObject(
            realname=self.leaderName
        )
        self.approval1 = self.registry.approvals.create(
            code=self.code1,
        )
        self.approval2 = self.registry.approvals.create(
            code=self.code2,
        )
        self.project = self.registry.projects.create(
            title=self.title,
            nickname=self.nickname,
            preparationMinutes=self.preparationMinutes,
            leader=self.leader,
        )
        self.project.approvals.create(self.approval1)
        self.project.approvals.create(self.approval2)

    def tearDown(self):
        self.project.delete()
        self.approval2.delete()
        self.approval1.delete()
    
    def test_attributes(self):
        self.failUnlessEqual(self.project.title, self.title)
        self.failUnlessEqual(self.project.nickname, self.nickname)
        self.failUnlessEqual(self.project.preparationMinutes, self.preparationMinutes)
        self.failUnlessEqual(self.project.leader, self.leader)
        self.failUnlessEqual(self.project.researchers.count(), 0)
        self.failUnlessEqual(self.project.approvals.count(), 2)
        self.failUnless(self.approval1 in self.project.approvals)
        self.failUnless(self.approval2 in self.project.approvals)

    def test_getLabelValue(self):
        self.failUnlessEqual(self.project.getLabelValue(), self.nickname)
        self.project.nickname = ""
        self.failUnlessEqual(self.project.getLabelValue(), self.title)


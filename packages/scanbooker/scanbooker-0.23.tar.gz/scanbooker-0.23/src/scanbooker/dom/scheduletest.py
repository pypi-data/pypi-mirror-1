import unittest
from scanbooker.exceptions import *
from scanbooker.dom.testunit import TestCase
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestEarmarkedTimeTemplateWeek),
        unittest.makeSuite(TestEarmarkedTimeTemplate),
        unittest.makeSuite(TestScanningSession),
        unittest.makeSuite(TestApproval),
    ]
    return unittest.TestSuite(suites)


class TestEarmarkedTimeTemplateWeek(TestCase):

    def testDomainClass(self):
        domainClassName = 'EarmarkedTimeTemplateWeek'
        self.failUnless(self.registry.getDomainClass(domainClassName))


class TestEarmarkedTimeTemplate(TestCase):

    def testDomainClass(self):
        domainClassName = 'EarmarkedTimeTemplate'
        self.failUnless(self.registry.getDomainClass(domainClassName))


class TestScanningSession(TestCase):

    def setUp(self):
        self.session = self.registry.scanningSessions.create(
            starts=mx.DateTime.DateTime(2001, 1, 1, 9, 0, 0),
            ends=mx.DateTime.DateTime(2001, 1, 1, 10, 0, 0),
        )

    def tearDown(self):
        self.session.delete()
    
    def test_arrivalTime(self):
        arrives = mx.DateTime.DateTime(2001, 1, 1, 9, 0, 0)
        self.failUnlessEqual(self.session.getArrivalTime(), arrives)

    def test_getContact(self):
        self.failUnlessEqual(self.session.getContact(), None)
        project = self.registry.projects[1]
        self.session.project = project
        self.failUnlessEqual(self.session.getContact(), project.leader)
        sessionLeader = project.researchers.keys()[0]
        self.session.leader = sessionLeader
        self.failUnlessEqual(self.session.getContact(), sessionLeader)


class TestApproval(TestCase):

    def setUp(self):
        self.approval = self.registry.approvals.create(
            code='TestApproval',
            numberAllocated=50,
            numberUsedAdjustment=5,
            expires=mx.DateTime.DateTime(2010, 12, 31, 0, 0, 0)
        )
        self.session1 = self.registry.scanningSessions.create(
            starts=mx.DateTime.DateTime(2001, 1, 1, 9, 0, 0),
            ends=mx.DateTime.DateTime(2001, 1, 1, 10, 0, 0),
            approval=self.approval
        )
        self.session2 = self.registry.scanningSessions.create(
            starts=mx.DateTime.DateTime(2001, 1, 1, 10, 0, 0),
            ends=mx.DateTime.DateTime(2001, 1, 1, 11, 0, 0),
            approval=self.approval
        )
        self.session3 = self.registry.scanningSessions.create(
            starts=mx.DateTime.DateTime(2001, 1, 1, 11, 0, 0),
            ends=mx.DateTime.DateTime(2001, 1, 1, 12, 0, 0),
            approval=self.approval
        )

    def tearDown(self):
        self.session3.delete()
        self.session2.delete()
        self.session1.delete()
        self.approval.delete()

    def test_numberUser(self):
        self.failUnlessEqual(self.approval.numberRemaining(), 42)


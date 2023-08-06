import unittest
from scanbooker.exceptions import *
from scanbooker.dom.testunit import TestCase
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestVolunteer),
    ]
    return unittest.TestSuite(suites)

class TestVolunteer(TestCase):

    realname = 'Test Volunteer'
    requiredAttrs = ['realname', 'dateCreated', 'lastModified', 'state']

    def setUp(self):
        dob = mx.DateTime.now() - mx.DateTime.DateTimeDelta(366*20)
        handedness = self.registry.handednesses['Right-handed']
        self.volunteer = self.registry.volunteers.create(
            realname=self.realname,
            handedness=handedness,
            dateOfBirth=dob,
            onHitlist=True,
        )

    def tearDown(self):
        try:
            self.volunteer.delete()
        finally:
            pass
            
    def test_attributes(self):
        "For: http://desire.appropriatesoftware.net/requirements/23/"
        self.failUnlessEqual(self.volunteer.realname, self.realname)
        for metaAttr in self.volunteer.meta.attributes:
            if metaAttr.name in self.requiredAttrs:
                if not metaAttr.isRequired:
                    self.fail("Attr '%s' is required." % metaAttr.name)
            else:
                if metaAttr.isRequired:
                    self.fail("Attr '%s' is not required." % metaAttr.name)
        self.failUnless(self.volunteer.onHitlist)

    def test_lastScan(self):
        self.volunteer.lastScan()

    def test_age(self):
        self.failUnlessEqual(self.volunteer.age(), 20)
    
    def test_hand(self):
        self.failUnlessEqual(self.volunteer.hand(), 'R')

    def test_status(self):
        self.failUnlessEqual(self.volunteer.status.name, 'Active')

    def test_isInactive(self):
        self.failIf(self.volunteer.isInactive())
        self.volunteer.status = self.registry.volunteerStatuses['Inactive']
        self.failUnless(self.volunteer.isInactive())
        self.volunteer.status = None
        self.failUnless(self.volunteer.isInactive())
        self.volunteer.status = self.registry.volunteerStatuses['Active']
        self.failIf(self.volunteer.isInactive())


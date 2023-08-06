import unittest
from scanbooker.django.apps.sui.views.test.base import AdminSessionViewTestCase
from scanbooker.django.apps.sui.views.volunteer import VolunteerBookingSelectVolunteer
from scanbooker.django.apps.sui.views.volunteer import VolunteerBookingSelectSession
from scanbooker.django.apps.sui.views.volunteer import VolunteerBookingConfirmSelection
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestVolunteerBookingSelectVolunteer),
        unittest.makeSuite(TestVolunteerBookingSelectSession),
        unittest.makeSuite(TestVolunteerBookingConfirmSelection),
    ]
    return unittest.TestSuite(suites)


class TestVolunteerBookingSelectVolunteer(AdminSessionViewTestCase):

    viewClass = VolunteerBookingSelectVolunteer


class TestVolunteerBookingSelectSession(AdminSessionViewTestCase):

    viewClass = VolunteerBookingSelectSession

    def createViewKwds(self):
        k = super(TestVolunteerBookingSelectSession, self).createViewKwds()
        k['volunteerId'] = 1
        return k


class TestVolunteerBookingConfirmSelection(AdminSessionViewTestCase):

    viewClass = VolunteerBookingConfirmSelection

    def setUp(self):
        now = mx.DateTime.now() + mx.DateTime.oneDay * 3
        self.session = self.registry.scanningSessions.create(
            starts = mx.DateTime.DateTime(
                now.year, now.month, now.day, 10, 0, 0),
            ends = mx.DateTime.DateTime(
                now.year, now.month, now.day, 11, 30, 0),
        )
        super(TestVolunteerBookingConfirmSelection, self).setUp()
        
    def tearDown(self):
        super(TestVolunteerBookingConfirmSelection, self).tearDown()
        self.session.delete()

    def createViewKwds(self):
        k = super(TestVolunteerBookingConfirmSelection, self).createViewKwds()
        k['volunteerId'] = 1
        k['sessionId'] = self.session.id
        k['isConfirmed'] = False
        return k


import unittest
from scanbooker.django.apps.sui.views.test.base import AdminSessionViewTestCase
from scanbooker.django.apps.sui.views.rpc2 import ScheduleService
from scanbooker.django.apps.sui.views.rpc2 import ReportService
import mx.DateTime
import simplejson

# todo: TestRpcUpdatePostView
# Todo: Test for sending unicode chars in with RPC JSON request. It breaks unless .encode('ascii', 'xmlcharrefreplace') is used on the JSON string before parsing as JSON.

def suite():
    suites = [
        unittest.makeSuite(TestViewWeek),
        unittest.makeSuite(TestViewWeekTimestamp),
        unittest.makeSuite(TestCreateTimeSlotEarmark),
        unittest.makeSuite(TestCreateTimeSlotSession),
        unittest.makeSuite(TestUpdateTimeSlot),
        unittest.makeSuite(TestDeleteTimeSlot),
        unittest.makeSuite(TestDuplicateTimeSlotEarmarkedTime),
        unittest.makeSuite(TestDuplicateTimeSlotScanningSession),
        unittest.makeSuite(TestDuplicateTimeSlotScanningSessionApproval),
        unittest.makeSuite(TestDuplicateTimeSlotMaintenanceSession),
        unittest.makeSuite(TestGetEarmarkTemplateNames),
        unittest.makeSuite(TestEarmarkCurrentWeek),
        unittest.makeSuite(TestCreateEarmarkTemplate),
        unittest.makeSuite(TestDeleteEarmarkTemplate),
        unittest.makeSuite(TestGetTimeSlotUpdateFormEarmark),
        unittest.makeSuite(TestGetTimeSlotUpdateFormScanning),
        unittest.makeSuite(TestGetWeekIsPublishedTrue),
        unittest.makeSuite(TestGetWeekIsPublishedFalse),
        unittest.makeSuite(TestSetWeekIsPublishedTrue),
        unittest.makeSuite(TestSetWeekIsPublishedFalse),
        unittest.makeSuite(TestSetWeekNotesPublicTrue),
        unittest.makeSuite(TestSetWeekNotesPublicFalse),
        # Report tests.
        unittest.makeSuite(TestGetReportColumns),
    ]
    return unittest.TestSuite(suites)


class TestViewWeek(AdminSessionViewTestCase):

    viewClass = ScheduleService

    def initPost(self):
        jsonString = simplejson.dumps({
            'method': 'viewWeek',
            'params': ['current', ''],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestViewWeek, self).test_getResponse()
        message = self.view.message
        self.failUnless(message)
        self.failUnless(message.has_key('config'), message)
        self.failUnless(message.has_key('earmarks'), message)
        self.failUnless(message.has_key('sessions'), message)
        config = message['config']
        self.failUnless(config.has_key('weekStarts'), config)
        self.failUnless(config.has_key('workingStartsHour'), config)
        self.failUnless(config.has_key('workingEndsHour'), config)
        earmarks = message['earmarks']
        self.failUnless(earmarks.has_key('monday'), earmarks)
        sessions = message['sessions']
        self.failUnless(sessions.has_key('tuesday'), sessions)
        self.failUnless(sessions.has_key('saturday'), sessions)


class TestViewWeekTimestamp(TestViewWeek):

    def initPost(self):
        jsonString = simplejson.dumps({
            'method': 'viewWeek',
            'params': ['1204871400', ''],
        })
        self.POST[jsonString] = 1


class TestCreateTimeSlotEarmark(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2008, 7, 1, 9, 0, 0)
    fixtureEnds = mx.DateTime.DateTime(2008, 7, 1, 10, 0, 0)
    fixtureLayerName = 'earmark'
    fixtureSummary = 'scanning'
    fixtureId = None

    def initPost(self):
        jsonString = simplejson.dumps({
            'method': 'createTimeSlot',
            'params': [{
                'dtstart': int(self.fixtureStarts),
                'dtend': int(self.fixtureEnds),
                'layer': self.fixtureLayerName,
                'sessionType': self.fixtureSummary,
            }],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestCreateTimeSlotEarmark, self).test_getResponse()
        message = self.view.message
        self.failUnless(message)
        self.failUnless(message.has_key('id'), message)
        self.fixtureId = message['id']
        self.failUnless(message.has_key('dtstart'), message)
        self.failUnless(message.has_key('dtend'), message)
        self.failUnless(message.has_key('layer'), message)
        self.failUnless(message.has_key('sessionType'), message)
        self.failUnless(message.has_key('location'), message)
        calendarId = message['id']
        calendarIdSplit = calendarId.split('.')
        self.failUnlessEqual(calendarIdSplit[0], 'EarmarkedTime')
        self.failUnlessEqual(message['dtstart'], int(self.fixtureStarts))
        self.failUnlessEqual(message['dtend'], int(self.fixtureEnds))
        self.failUnlessEqual(message['layer'], str(self.fixtureLayerName))
        self.failUnlessEqual(message['sessionType'], str(self.fixtureSummary))

    def tearDown(self):
        super(TestCreateTimeSlotEarmark, self).tearDown()
        if self.fixtureId != None:
            sessionId = int(self.fixtureId.split('.')[1])
            fixtureSession = self.registry.earmarkedTimes[sessionId]
            fixtureSession.delete()
            fixtureSession.purge()


class TestCreateTimeSlotSession(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2008, 7, 1, 9, 0, 0)
    fixtureEnds = mx.DateTime.DateTime(2008, 7, 1, 10, 0, 0)
    fixtureSummary = 'scanning'
    fixtureLayerName = 'session'
    fixtureId = None

    def initPost(self):
        jsonString = simplejson.dumps({
            'method': 'createTimeSlot',
            'params': [{
                'dtstart': int(self.fixtureStarts),
                'dtend': int(self.fixtureEnds),
                'layer': self.fixtureLayerName,
                'sessionType': self.fixtureSummary,
            }],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestCreateTimeSlotSession, self).test_getResponse()
        message = self.view.message
        self.failUnless(message)
        self.failUnless(message.has_key('id'), message)
        self.fixtureId = message['id']
        self.failUnless(message.has_key('dtstart'), message)
        self.failUnless(message.has_key('dtend'), message)
        self.failUnless(message.has_key('layer'), message)
        self.failUnless(message.has_key('sessionType'), message)
        self.failUnless(message.has_key('location'), message)
        calendarId = message['id']
        calendarIdSplit = calendarId.split('.')
        self.failUnlessEqual(calendarIdSplit[0], 'ScanningSession')
        self.failUnlessEqual(message['dtstart'], int(self.fixtureStarts))
        self.failUnlessEqual(message['dtend'], int(self.fixtureEnds))
        self.failUnlessEqual(message['layer'], str(self.fixtureLayerName))
        self.failUnlessEqual(message['sessionType'], str(self.fixtureSummary))

    def tearDown(self):
        super(TestCreateTimeSlotSession, self).tearDown()
        if self.fixtureId != None:
            sessionId = int(self.fixtureId.split('.')[1])
            fixtureSession = self.registry.scanningSessions[sessionId]
            fixtureSession.delete()
            fixtureSession.purge()


class TestUpdateTimeSlot(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2007, 7, 1, 9, 0, 0)
    fixtureEnds = mx.DateTime.DateTime(2007, 7, 1, 10, 0, 0)

    def initPost(self):
        self.fixtureSession = self.registry.scanningSessions.create(
            starts=self.fixtureStarts,
            ends=self.fixtureEnds,
        )
        jsonString = simplejson.dumps({
            'method': 'updateTimeSlot',
            'params': [{
                'id': self.fixtureSession.getCalendarId(),
                'dtstart': int(self.fixtureSession.starts)+3600,
                'dtend': int(self.fixtureSession.ends)+3600,
            }],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestUpdateTimeSlot, self).test_getResponse()
        message = self.view.message
        self.failUnless(message)
        self.failUnless(message.has_key('id'), message)
        self.failUnless(message.has_key('dtstart'), message)
        self.failUnless(message.has_key('dtend'), message)
        self.failUnless(message.has_key('layer'), message)
        self.failUnless(message.has_key('sessionType'), message)
        self.failUnless(message.has_key('location'), message)
        self.failUnlessEqual(message['dtstart'], int(self.fixtureStarts)+3600)
        self.failUnlessEqual(message['dtend'], int(self.fixtureEnds)+3600)

    def tearDown(self):
        super(TestUpdateTimeSlot, self).tearDown()
        self.fixtureSession.delete()
        self.fixtureSession.purge()


class TestDuplicateTimeSlotEarmarkedTime(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2009, 7, 1, 9, 0, 0)
    fixtureEnds = mx.DateTime.DateTime(2009, 7, 1, 10, 0, 0)
    fixtureSessionType = AdminSessionViewTestCase.registry.sessionTypes['Scanning']
    duplicateFixture = None

    def initPost(self):
        self.fixtureSession = self.registry.earmarkedTimes.create(
            starts=self.fixtureStarts,
            ends=self.fixtureEnds,
            sessionType=self.fixtureSessionType
        )
        self.failUnless(self.fixtureSession.starts, self.fixtureStarts)
        self.failUnless(self.fixtureSession.ends, self.fixtureEnds)
        self.failUnless(self.fixtureSession.sessionType, self.fixtureSessionType)
        jsonString = simplejson.dumps({
            'method': 'duplicateTimeSlot',
            'params': [{
                'id': self.fixtureSession.getCalendarId(),
                'dtstart': int(self.fixtureEnds + mx.DateTime.oneHour)
            }],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestDuplicateTimeSlotEarmarkedTime, self).test_getResponse()
        message = self.view.message
        self.failUnless(message)
        self.failUnless(hasattr(message, 'has_key'), message)
        self.failUnless(message.has_key('id'), message)
        self.failUnless(message.has_key('dtend'), message)
        self.failUnless(message.has_key('dtstart'), message)
        self.failUnless(message.has_key('layer'), message)
        self.failUnless(message.has_key('sessionType'), message)
        self.failUnless(message.has_key('summary'), message)
        duplicateFixtureId = message['id']
        (domainClassName, domainObjectId) = duplicateFixtureId.split('.')
        domainClass = self.registry.getDomainClass(domainClassName)
        domainRegister = domainClass.createRegister()
        self.duplicateFixture = domainRegister[int(domainObjectId)]
        self.failUnlessEqual(self.duplicateFixture.__class__, self.fixtureSession.__class__)
        self.failUnlessEqual(self.duplicateFixture.starts, self.fixtureSession.ends + mx.DateTime.oneHour)
        oldDuration = self.fixtureSession.ends - self.fixtureSession.starts
        newDuration = self.duplicateFixture.ends - self.duplicateFixture.starts
        self.failUnlessEqual(oldDuration, newDuration)
        self.failUnlessEqual(self.duplicateFixture.sessionType, self.fixtureSession.sessionType)

    def tearDown(self):
        super(TestDuplicateTimeSlotEarmarkedTime, self).tearDown()
        self.fixtureSession.delete()
        self.fixtureSession.purge()
        if self.duplicateFixture != None:
            self.duplicateFixture.delete()
            self.duplicateFixture.purge()


class TestDuplicateTimeSlotScanningSession(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2009, 7, 1, 9, 0, 0)
    fixtureEnds = mx.DateTime.DateTime(2009, 7, 1, 10, 0, 0)
    fixtureProject = AdminSessionViewTestCase.registry.projects[1]
    fixtureBookingOwnVolunteers = True
    duplicateFixture = None

    def initPost(self):
        self.fixtureSession = self.registry.scanningSessions.create(
            starts=self.fixtureStarts,
            ends=self.fixtureEnds,
            bookingOwnVolunteers=self.fixtureBookingOwnVolunteers,
            project=self.fixtureProject
        )
        self.failUnless(self.fixtureSession.starts, self.fixtureStarts)
        self.failUnless(self.fixtureSession.ends, self.fixtureEnds)
        self.failUnless(self.fixtureSession.project, self.fixtureProject)
        self.failUnless(self.fixtureSession.bookingOwnVolunteers, self.fixtureBookingOwnVolunteers)
        jsonString = simplejson.dumps({
            'method': 'duplicateTimeSlot',
            'params': [{
                'id': self.fixtureSession.getCalendarId(),
                'dtstart': int(self.fixtureEnds + mx.DateTime.oneHour)
            }],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestDuplicateTimeSlotScanningSession, self).test_getResponse()
        message = self.view.message
        self.failUnless(message)
        self.failUnless(hasattr(message, 'has_key'), message)
        self.failUnless(message.has_key('id'), message)
        self.failUnless(message.has_key('dtend'), message)
        self.failUnless(message.has_key('dtstart'), message)
        self.failUnless(message.has_key('layer'), message)
        self.failUnless(message.has_key('sessionType'), message)
        self.failUnless(message.has_key('summary'), message)
        duplicateFixtureId = message['id']
        (domainClassName, domainObjectId) = duplicateFixtureId.split('.')
        domainClass = self.registry.getDomainClass(domainClassName)
        domainRegister = domainClass.createRegister()
        self.duplicateFixture = domainRegister[int(domainObjectId)]
        self.failUnlessEqual(self.duplicateFixture.__class__, self.fixtureSession.__class__)
        self.failUnlessEqual(self.duplicateFixture.starts, self.fixtureSession.ends + mx.DateTime.oneHour)
        oldDuration = self.fixtureSession.ends - self.fixtureSession.starts
        newDuration = self.duplicateFixture.ends - self.duplicateFixture.starts
        self.failUnlessEqual(oldDuration, newDuration)
        self.failUnlessEqual(oldDuration, newDuration)
        self.failUnlessEqual(self.duplicateFixture.bookingOwnVolunteers, self.fixtureBookingOwnVolunteers)
        self.failUnlessEqual(self.duplicateFixture.project, self.fixtureProject)

    def tearDown(self):
        super(TestDuplicateTimeSlotScanningSession, self).tearDown()
        self.fixtureSession.delete()
        self.fixtureSession.purge()
        if self.duplicateFixture != None:
            self.duplicateFixture.delete()
            self.duplicateFixture.purge()


class TestDuplicateTimeSlotScanningSessionApproval(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2009, 7, 1, 9, 0, 0)
    fixtureEnds = mx.DateTime.DateTime(2009, 7, 1, 10, 0, 0)
    fixtureProject = AdminSessionViewTestCase.registry.projects[1]
    fixtureBookingOwnVolunteers = True
    fixtureApproval = AdminSessionViewTestCase.registry.approvals[1]
    duplicateFixture = None

    def initPost(self):

        self.fixtureSession = self.registry.scanningSessions.create(
            starts=self.fixtureStarts,
            ends=self.fixtureEnds,
            bookingOwnVolunteers=self.fixtureBookingOwnVolunteers,
            project=self.fixtureProject,
            approval=self.fixtureApproval,
        )
        self.failUnlessEqual(self.fixtureSession.approval, self.fixtureApproval)
        jsonString = simplejson.dumps({
            'method': 'duplicateTimeSlot',
            'params': [{
                'id': self.fixtureSession.getCalendarId(),
                'dtstart': int(self.fixtureEnds + mx.DateTime.oneHour)
            }],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestDuplicateTimeSlotScanningSessionApproval, self).test_getResponse()
        message = self.view.message
        self.failUnless(message)
        self.failUnless(hasattr(message, 'has_key'), message)
        duplicateFixtureId = message['id']
        (domainClassName, domainObjectId) = duplicateFixtureId.split('.')
        domainClass = self.registry.getDomainClass(domainClassName)
        domainRegister = domainClass.createRegister()
        self.duplicateFixture = domainRegister[int(domainObjectId)]
        self.failUnlessEqual(self.duplicateFixture.approval, self.fixtureApproval)

    def tearDown(self):
        super(TestDuplicateTimeSlotScanningSessionApproval, self).tearDown()
        self.fixtureSession.delete()
        self.fixtureSession.purge()
        if self.duplicateFixture != None:
            self.duplicateFixture.delete()
            self.duplicateFixture.purge()


class TestDuplicateTimeSlotMaintenanceSession(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2009, 7, 1, 9, 0, 0)
    fixtureEnds = mx.DateTime.DateTime(2009, 7, 1, 10, 0, 0)
    fixtureMaintainer = 'Gary'
    duplicateFixture = None

    def initPost(self):
        self.fixtureSession = self.registry.maintenanceSessions.create(
            starts=self.fixtureStarts,
            ends=self.fixtureEnds,
            comment=self.fixtureMaintainer
        )
        jsonString = simplejson.dumps({
            'method': 'duplicateTimeSlot',
            'params': [{
                'id': self.fixtureSession.getCalendarId(),
                'dtstart': int(self.fixtureEnds + mx.DateTime.oneHour)
            }],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestDuplicateTimeSlotMaintenanceSession, self).test_getResponse()
        message = self.view.message
        self.failUnless(message)
        self.failUnless(hasattr(message, 'has_key'), message)
        self.failUnless(message.has_key('id'), message)
        self.failUnless(message.has_key('dtend'), message)
        self.failUnless(message.has_key('dtstart'), message)
        self.failUnless(message.has_key('layer'), message)
        self.failUnless(message.has_key('sessionType'), message)
        self.failUnless(message.has_key('summary'), message)
        duplicateFixtureId = message['id']
        (domainClassName, domainObjectId) = duplicateFixtureId.split('.')
        domainClass = self.registry.getDomainClass(domainClassName)
        domainRegister = domainClass.createRegister()
        self.duplicateFixture = domainRegister[int(domainObjectId)]
        self.failUnlessEqual(self.duplicateFixture.__class__, self.fixtureSession.__class__)
        self.failUnlessEqual(self.duplicateFixture.starts, self.fixtureSession.ends + mx.DateTime.oneHour)
        oldDuration = self.fixtureSession.ends - self.fixtureSession.starts
        newDuration = self.duplicateFixture.ends - self.duplicateFixture.starts
        self.failUnlessEqual(oldDuration, newDuration)
        self.failUnlessEqual(self.duplicateFixture.comment, self.fixtureMaintainer)

    def tearDown(self):
        super(TestDuplicateTimeSlotMaintenanceSession, self).tearDown()
        self.fixtureSession.delete()
        self.fixtureSession.purge()
        if self.duplicateFixture != None:
            self.duplicateFixture.delete()
            self.duplicateFixture.purge()


class TestDeleteTimeSlot(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2009, 7, 1, 9, 0, 0)
    fixtureEnds = mx.DateTime.DateTime(2009, 7, 1, 10, 0, 0)

    def initPost(self):
        self.fixtureSession = self.registry.scanningSessions.create(
            starts=self.fixtureStarts,
            ends=self.fixtureEnds,
        )
        jsonString = simplejson.dumps({
            'method': 'deleteTimeSlot',
            'params': [{
                'layer': 'session',
                'sessionType': 'scanning',
                'id': self.fixtureSession.getCalendarId(),
            }],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestDeleteTimeSlot, self).test_getResponse()
        message = self.view.message
        self.failUnless(message)
        self.failUnless(message.has_key('id'), message)
        self.failUnless(message.has_key('layer'), message)
        self.failUnless(message.has_key('sessionType'), message)
        self.failUnlessEqual(message['id'], self.fixtureSession.getCalendarId())
        self.failUnlessEqual(self.fixtureSession.state.name, 'deleted')

    def tearDown(self):
        super(TestDeleteTimeSlot, self).tearDown()
        self.fixtureSession.delete()
        self.fixtureSession.purge()


class TestGetEarmarkTemplateNames(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2009, 7, 1, 9, 0, 0)
    fixtureEnds = mx.DateTime.DateTime(2009, 7, 1, 10, 0, 0)

    def initPost(self):
        jsonString = simplejson.dumps({
            'method': 'getEarmarkTemplateNames',
            'params': [],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestGetEarmarkTemplateNames, self).test_getResponse()
        message = self.view.message
        self.failUnless(message)
        self.failUnless(message[0], message)
        self.failUnless('Standard' in message, message)


class TestEarmarkCurrentWeek(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureName = 'Standard'

    def initPost(self):
        jsonString = simplejson.dumps({
            'method': 'earmarkCurrentWeek',
            'params': [
                self.fixtureName,
            ],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestEarmarkCurrentWeek, self).test_getResponse()
        message = self.view.message
        self.failUnless(message, "No message: %s" % message)


class TestCreateEarmarkTemplate(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureName = 'Test Template'

    def setUp(self):
        super(TestCreateEarmarkTemplate, self).setUp()
        earmarkTemplates = self.registry.earmarkedTimeTemplateWeeks
        if self.fixtureName in earmarkTemplates:
            del(earmarkTemplates[self.fixtureName])

    def initPost(self):
        jsonString = simplejson.dumps({
            'method': 'createEarmarkTemplate',
            'params': [
                self.fixtureName,
            ],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        earmarkTemplates = self.registry.earmarkedTimeTemplateWeeks
        self.failIf(self.fixtureName in earmarkTemplates)
        super(TestCreateEarmarkTemplate, self).test_getResponse()
        self.failUnless(self.fixtureName in earmarkTemplates)
        message = self.view.message
        # todo: A positive response, checked by the client.
        #self.failUnless(message)

    def tearDown(self):
        super(TestCreateEarmarkTemplate, self).tearDown()
        earmarkTemplates = self.registry.earmarkedTimeTemplateWeeks
        if self.fixtureName in earmarkTemplates:
            del(earmarkTemplates[self.fixtureName])


class TestDeleteEarmarkTemplate(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureName = 'Test Template'

    def setUp(self):
        super(TestDeleteEarmarkTemplate, self).setUp()
        earmarkTemplates = self.registry.earmarkedTimeTemplateWeeks
        if not self.fixtureName in earmarkTemplates:
            earmarkTemplates = self.registry.earmarkedTimeTemplateWeeks
            earmarkTemplates.create(self.fixtureName)

    def initPost(self):
        jsonString = simplejson.dumps({
            'method': 'deleteEarmarkTemplate',
            'params': [
                self.fixtureName,
            ],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        earmarkTemplates = self.registry.earmarkedTimeTemplateWeeks
        self.failUnless(self.fixtureName in earmarkTemplates)
        super(TestDeleteEarmarkTemplate, self).test_getResponse()
        self.failIf(self.fixtureName in earmarkTemplates)
        message = self.view.message
        # todo: A positive response, checked by the client.
        #self.failUnless(message)

    def tearDown(self):
        super(TestDeleteEarmarkTemplate, self).tearDown()
        earmarkTemplates = self.registry.earmarkedTimeTemplateWeeks
        if self.fixtureName in earmarkTemplates:
            del(earmarkTemplates[self.fixtureName])


class TestGetTimeSlotUpdateFormEarmark(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2009, 7, 1, 9, 0, 0)
    fixtureEnds = mx.DateTime.DateTime(2009, 7, 1, 10, 0, 0)

    def initPost(self):
        self.fixtureSession = self.registry.earmarkedTimes.create(
            starts=self.fixtureStarts,
            ends=self.fixtureEnds,
        )
        jsonString = simplejson.dumps({
            'method': 'getTimeSlotUpdateForm',
            'params': [{
                'id': self.fixtureSession.getCalendarId(),
            }],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestGetTimeSlotUpdateFormEarmark, self).test_getResponse()
        message = self.view.message
        self.failUnless(message.has_key('id'), message)
        self.failUnless(message.has_key('form'), message)
        self.failUnlessEqual(message['id'], self.fixtureSession.getCalendarId())
        self.failUnless('form action' in message['form'], message['form'])

    def tearDown(self):
        super(TestGetTimeSlotUpdateFormEarmark, self).tearDown()
        self.fixtureSession.delete()
        self.fixtureSession.purge()


class TestGetTimeSlotUpdateFormScanning(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2009, 7, 1, 9, 0, 0)
    fixtureEnds = mx.DateTime.DateTime(2009, 7, 1, 10, 0, 0)

    def initPost(self):
        self.fixtureSession = self.registry.scanningSessions.create(
            starts=self.fixtureStarts,
            ends=self.fixtureEnds,
        )
        jsonString = simplejson.dumps({
            'method': 'getTimeSlotUpdateForm',
            'params': [{
                'layer': 'session',
                'sessionType': 'scanning',
                'id': self.fixtureSession.getCalendarId(),
            }],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestGetTimeSlotUpdateFormScanning, self).test_getResponse()
        message = self.view.message
        self.failUnless(message.has_key('id'), message)
        self.failUnless(message.has_key('form'), message)
        self.failUnlessEqual(message['id'], self.fixtureSession.getCalendarId())
        self.failUnless('form action' in message['form'], message['form'])

    def tearDown(self):
        super(TestGetTimeSlotUpdateFormScanning, self).tearDown()
        self.fixtureSession.delete()
        self.fixtureSession.purge()


class GetWeekIsPublishedTestCase(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2008, 1, 7, 0, 0, 0)
    week = None
    weekIsPublished = False

    def initPost(self):
        self.setupWeek()
        jsonString = simplejson.dumps({
            'method': 'getWeekIsPublished',
            'params': [{
            }],
        })
        self.POST[jsonString] = 1

    def getWeek(self):
        self.week = self.registry.weeks.findSingleDomainObject(
            starts=self.fixtureStarts)
        if not self.week:
            self.week = self.registry.weeks.create(starts=self.fixtureStarts)
        return self.week

    def setupWeek(self):
        week = self.getWeek()
        week.isPublished = self.weekIsPublished
        week.save()

    def test_getResponse(self):
        super(GetWeekIsPublishedTestCase, self).test_getResponse()
        self.failUnlessWeekIsPublished()

    def failUnlessWeekIsPublished(self):
        message = self.view.message
        if self.weekIsPublished:
            self.failUnless(message)
        else:
            self.failIf(message)

    def tearDown(self):
        super(GetWeekIsPublishedTestCase, self).tearDown()
        if self.week:
            self.week.delete()

    def initViewSession(self):
        super(GetWeekIsPublishedTestCase, self).initViewSession()
        if self.viewSession:
            self.viewSession.scheduleBookmark = self.fixtureStarts
            self.viewSession.save()


class TestGetWeekIsPublishedTrue(GetWeekIsPublishedTestCase):

    weekIsPublished = True


class TestGetWeekIsPublishedFalse(GetWeekIsPublishedTestCase):

    weekIsPublished = False


class SetWeekIsPublishedTestCase(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2008, 1, 7, 0, 0, 0)
    week = None
    weekIsPublished = ''

    def initPost(self):
        jsonString = simplejson.dumps({
            'method': 'setWeekIsPublished',
            'params': [{
                'isPublished': self.weekIsPublished
            }],
        })
        self.POST[jsonString] = 1

    def getWeek(self):
        return self.registry.weeks.findSingleDomainObject(
            starts=self.fixtureStarts)

    def test_getResponse(self):
        super(SetWeekIsPublishedTestCase, self).test_getResponse()
        self.failUnlessWeekIsPublished()

    def failUnlessWeekIsPublished(self):
        week = self.getWeek()
        if self.weekIsPublished:
            self.failUnless(week.isPublished)
        else:
            self.failIf(week.isPublished)

    def tearDown(self):
        super(SetWeekIsPublishedTestCase, self).tearDown()
        if self.week:
            self.week.delete()

    def initViewSession(self):
        super(SetWeekIsPublishedTestCase, self).initViewSession()
        if self.viewSession:
            self.viewSession.scheduleBookmark = self.fixtureStarts
            self.viewSession.save()


class TestSetWeekIsPublishedTrue(SetWeekIsPublishedTestCase):

    weekIsPublished = True


class TestSetWeekIsPublishedFalse(SetWeekIsPublishedTestCase):

    weekIsPublished = False


class SetWeekNotesTestCase(AdminSessionViewTestCase):

    viewClass = ScheduleService
    fixtureStarts = mx.DateTime.DateTime(2008, 1, 7, 0, 0, 0)
    week = None
    notesPublic = 'do this'
    notesPrivate = 'shh'

    def initPost(self):
        jsonString = simplejson.dumps({
            'method': 'setWeekNotes',
            'params': [{
                'notesPublic': self.notesPublic,
                'notesPrivate': self.notesPrivate,
            }],
        })
        self.POST[jsonString] = 1

    def getWeek(self):
        return self.registry.weeks.findSingleDomainObject(
            starts=self.fixtureStarts)

    def test_getResponse(self):
        super(SetWeekNotesTestCase, self).test_getResponse()
        self.failUnlessWeekNotesPublic()

    def failUnlessWeekNotesPublic(self):
        week = self.getWeek()
        self.failUnlessEqual(self.notesPublic, week.notesPublic)

    def failUnlessWeekNotesPrivate(self):
        week = self.getWeek()
        self.failUnlessEqual(self.notesPrivate, week.notesPrivate)

    def tearDown(self):
        super(SetWeekNotesTestCase, self).tearDown()
        if self.week:
            self.week.delete()

    def initViewSession(self):
        super(SetWeekNotesTestCase, self).initViewSession()
        if self.viewSession:
            self.viewSession.scheduleBookmark = self.fixtureStarts
            self.viewSession.save()


class TestSetWeekNotesPublicTrue(SetWeekNotesTestCase):

    notesPublic = "Blah blah"


class TestSetWeekNotesPublicFalse(SetWeekNotesTestCase):

    notesPublic = ""


class TestGetReportColumns(AdminSessionViewTestCase):

    viewClass = ReportService

    def setUp(self):
        self.report = self.registry.reports.create()
        self.report.columns.create(name='id')
        super(TestGetReportColumns, self).setUp()

    def tearDown(self):
        self.report.delete()
        super(TestGetReportColumns, self).tearDown()

    def initPost(self):
        jsonString = simplejson.dumps({
            'method': 'getReportColumns',
            'params': [self.report.id],
        })
        self.POST[jsonString] = 1

    def test_getResponse(self):
        super(TestGetReportColumns, self).test_getResponse()
        message = self.view.message
        self.failUnless(message)
        self.failUnless(message.has_key('columns'), message)
        columns = message['columns']
        self.failUnlessEqual(len(columns), 1, message)



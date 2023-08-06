from scanbooker.django.apps.sui.views.manipulator import *
import unittest
from dm.view.manipulatortest import ManipulatorTestCase
from django.utils.datastructures import MultiValueDict
import mx.DateTime
import dm.datetimeconvertor

# Todo: Test case for ApprovalManpulator. (Simpler version of AccountM.).
# Todo: Test for ReportCreateManipulator and ReportUpdateManipulator.
# Todo: Check tests for report update RPC methods.

def suite():
    suites = [
        unittest.makeSuite(TestEarmarkedTimeCreate),
        unittest.makeSuite(TestEarmarkedTimeUpdate),
        unittest.makeSuite(TestMaintenanceSessionCreate),
        unittest.makeSuite(TestMaintenanceSessionUpdate),
        unittest.makeSuite(TestMethodsSessionCreate),
        unittest.makeSuite(TestMethodsSessionUpdate),
        unittest.makeSuite(TestDowntimeSessionCreate),
        unittest.makeSuite(TestDowntimeSessionUpdate),
        unittest.makeSuite(TestScanningSessionCreate),
        unittest.makeSuite(TestScanningSessionUpdate1),
        unittest.makeSuite(TestScanningSessionUpdate2),
        unittest.makeSuite(TestScanningSessionUpdate3),
        unittest.makeSuite(TestTrainingSessionCreate),
        unittest.makeSuite(TestTrainingSessionUpdate),
        unittest.makeSuite(TestAccountCreateOK),
        unittest.makeSuite(TestAccountCreateCodeInUse),
        unittest.makeSuite(TestAccountUpdateOK),
        unittest.makeSuite(TestAccountUpdateCodeInUse),
        unittest.makeSuite(TestApprovalCreateOK),
        unittest.makeSuite(TestApprovalCreateCodeInUse),
        unittest.makeSuite(TestApprovalUpdateOK),
        unittest.makeSuite(TestApprovalUpdateCodeInUse),
        unittest.makeSuite(TestApprovalExpires),
        unittest.makeSuite(TestProjectCreateOK),
        unittest.makeSuite(TestProjectCreateTitleInUse),
        unittest.makeSuite(TestProjectUpdateOK),
        unittest.makeSuite(TestProjectUpdateTitleInUse),
        unittest.makeSuite(TestVolunteerCreateOK),
        unittest.makeSuite(TestVolunteerCreateRealnameInUse),
        unittest.makeSuite(TestVolunteerCreatePanelIdInUse),
        unittest.makeSuite(TestVolunteerUpdateOK),
        unittest.makeSuite(TestVolunteerUpdateRealnameInUse),
        unittest.makeSuite(TestVolunteerUpdatePanelIdInUse),
        #unittest.makeSuite(TestReportManipulator),

    #    These cases are for manipulators that are not imported into views. Delete?    
    #    unittest.makeSuite(TestScanningSessionManipulator_Update),
    #    unittest.makeSuite(TestSessionTimeManipulator),
    #    unittest.makeSuite(TestPersonManipulator),
    #    unittest.makeSuite(TestPrincipalInvestigatorCreateManipulator),
    #    unittest.makeSuite(TestResearcherCreateManipulator),
    #    unittest.makeSuite(TestPersonCreateManipulator),
    #    unittest.makeSuite(TestPersonUpdateManipulator),
    #    unittest.makeSuite(TestPersonApproveManipulator),
    #    unittest.makeSuite(TestPersonUpdateManipulatorAdmin),
    #    unittest.makeSuite(TestResearcherManipulator_Create),
    #    unittest.makeSuite(TestResearcherManipulator_Update),
    ]
    return unittest.TestSuite(suites)

    
class ManipulatorTestCase(ManipulatorTestCase):

    manipulatorClass = None
    updatedObject = None
    createdObject = None
    dateTimeConvertor = dm.datetimeconvertor.DateTimeConvertor()
    requiredFieldNames = None

    def buildManipulator(self):
        objectRegister = self.mockObjectRegister()
        domainObject = self.mockDomainObject()
        fieldNames = self.mockFieldNames()
        client = self.mockClient()
        args = [objectRegister, domainObject, fieldNames, client]
        return self.manipulatorClass(*args)

    def mockObjectRegister(self):
        return None

    def mockDomainObject(self):
        return None

    def mockFieldNames(self):
        return None

    def mockClient(self):
        return self

    def mockCreateRequestParams(self):
        return MultiValueDict()

    def failUnlessCreate(self):
        self.failIf(self.manipulator.domainObject, "Existing object before.")
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failIf(errors, "Validation errors: %s" % errors)
        self.manipulator.decodeHtml(requestParams)
        self.manipulator.create(requestParams)
        self.createdObject = self.manipulator.domainObject
        self.failUnless(self.manipulator.domainObject, "Missing object after.")
    
    def setupUpdatedObject(self):
        register = self.mockObjectRegister()
        kwds = self.mockUpdateConstructorParams()
        self.updatedObject = register.create(**kwds)

    def mockUpdateConstructorParams(self):
        return {}
        
    def mockUpdateRequestParams(self):
        return self.updatedObject.asRequestParams()

    def failUnlessUpdate(self):
        self.failUnless(self.manipulator.domainObject, "Object missing before.")
        requestParams = self.mockUpdateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failIf(len(errors), "Validation errors: %s <<----->> Request params: %s" % (errors, requestParams))
        self.manipulator.update(requestParams)
        self.failUnless(self.manipulator.domainObject, "Object missing after.")

    def failUnlessValidationError(self, errorMsg):
        self.failUnless(self.manipulator.domainObject, "Object missing before.")
        requestParams = self.mockUpdateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failUnless(len(errors), "No validation errors were raised.")
        self.failUnless(
            errorMsg in str(errors),
            "Error '%s' not in validation errors: %s" % (errorMsg, errors)
        )

    def tearDown(self):
        self.teardownCreatedObject()
        self.teardownUpdatedObject()
        super(ManipulatorTestCase, self).tearDown()
    
    def teardownCreatedObject(self):
        if self.createdObject:
            self.createdObject.delete()

    def teardownUpdatedObject(self):
        if self.updatedObject:
            self.updatedObject.delete()

    def setStartsKwd(self, kwds):
        kwds['starts'] = self.timeToHTML(self.getNowTime())

    def setEndsKwd(self, kwds):
        kwds['ends'] = self.timeToHTML(self.getNowTimePlusThirtyMinutes())

    def setStartEndDateParams(self, params):
        params['date'] = self.getNowTime().strftime("%d-%m-%Y")
        params['start'] = self.getNowTime().strftime("%H:%M")
        params['end'] = self.getNowTimePlusThirtyMinutes().strftime("%H:%M")

    def setStartsParam(self, params):
        params['starts'] = self.getNowTime()

    def setEndsParam(self, params):
        params['ends'] = self.getNowTimePlusThirtyMinutes()

    def getNowTime(self):
        return mx.DateTime.now()

    def getNowTimePlusThirtyMinutes(self):
        return self.getNowTime() + mx.DateTime.DateTimeDelta(0,0,30)
        
    def timeToHTML(self, dateTime):
        return self.dateTimeConvertor.toHTML(dateTime)

    def test_fieldNames(self):
        if self.requiredFieldNames == None: 
            return
        r = self.requiredFieldNames
        m = self.manipulator.fieldNames
        self.failUnlessEqual(len(r), len(m), (r, m))
        for n in r:
            self.failUnless(n in m, (n, r, m))


class EarmarkedTimeManipulatorTestCase(ManipulatorTestCase):

    requiredFieldNames = ['sessionType', 'comment']
    
    def mockObjectRegister(self):
        return self.registry.earmarkedTimes

    def mockCreateRequestParams(self):
        params = super(EarmarkedTimeManipulatorTestCase, self
            ).mockCreateRequestParams()
        params['date'] = '07-08-2008'
        params['start'] = '10:00'
        params['end'] = '11:45'
        params['sessionType'] = 'Reserved' 
        return params

    def mockUpdateConstructorParams(self):
        params = super(EarmarkedTimeManipulatorTestCase, self
            ).mockUpdateConstructorParams()
        params['sessionType'] = self.registry.sessionTypes['Reserved']
        return params

    def isSlaveView(self): # Mocks the behaviour of the inline form 'client'.
        return True


class TestEarmarkedTimeCreate(EarmarkedTimeManipulatorTestCase):

    manipulatorClass = EarmarkedTimeCreateManipulator

    def test_create(self):
        self.failUnlessCreate()


class TestEarmarkedTimeUpdate(EarmarkedTimeManipulatorTestCase):

    manipulatorClass = EarmarkedTimeUpdateManipulator

    def mockUpdateRequestParams(self):
        params = self.updatedObject.asRequestParams()
        params['sessionType'] = 'Scanning'
        params['comment'] = 'Alice?'
        return params
        
    def test_update(self):
        self.failUnlessEqual(self.updatedObject.sessionType.name, 'Reserved')
        self.failUnlessEqual(self.updatedObject.comment, '')
        self.failUnlessUpdate()
        self.failUnlessEqual(self.updatedObject.sessionType.name, 'Scanning')
        self.failUnlessEqual(self.updatedObject.comment, 'Alice?')

    def mockDomainObject(self):
        self.setupUpdatedObject()
        return self.updatedObject


class TestMaintenanceSessionCreate(ManipulatorTestCase):

    manipulatorClass = MaintenanceSessionManipulator

    def mockObjectRegister(self):
        return self.registry.maintenanceSessions

    def test_create(self):
        self.failUnlessCreate()

    def mockCreateRequestParams(self):
        kwds = super(TestMaintenanceSessionCreate, self).mockCreateRequestParams()
        self.setStartsKwd(kwds)
        self.setEndsKwd(kwds)
        return kwds


class TestMaintenanceSessionUpdate(ManipulatorTestCase):

    manipulatorClass = MaintenanceSessionManipulator

    def mockObjectRegister(self):
        return self.registry.maintenanceSessions

    def mockDomainObject(self):
        self.setupUpdatedObject()
        return self.updatedObject
        
    def test_update(self):
        self.failUnlessUpdate()

    def mockUpdateConstructorParams(self):
        params = super(TestMaintenanceSessionUpdate, self).mockUpdateConstructorParams()
        self.setStartsParam(params) 
        self.setEndsParam(params) 
        return params


class TestMethodsSessionCreate(ManipulatorTestCase):

    manipulatorClass = MethodsSessionManipulator

    def mockObjectRegister(self):
        return self.registry.methodsSessions

    def test_create(self):
        self.failUnlessCreate()

    def mockCreateRequestParams(self):
        kwds = super(TestMethodsSessionCreate, self).mockCreateRequestParams()
        self.setStartsKwd(kwds)
        self.setEndsKwd(kwds)
        return kwds


class TestMethodsSessionUpdate(ManipulatorTestCase):

    manipulatorClass = MethodsSessionManipulator

    def mockObjectRegister(self):
        return self.registry.methodsSessions

    def mockDomainObject(self):
        self.setupUpdatedObject()
        return self.updatedObject
        
    def test_update(self):
        self.failUnlessUpdate()

    def mockUpdateConstructorParams(self):
        params = super(TestMethodsSessionUpdate, self).mockUpdateConstructorParams()
        self.setStartsParam(params) 
        self.setEndsParam(params) 
        return params


class TestDowntimeSessionCreate(ManipulatorTestCase):

    manipulatorClass = DowntimeSessionManipulator

    def mockObjectRegister(self):
        return self.registry.downtimeSessions

    def test_create(self):
        self.failUnlessCreate()

    def mockCreateRequestParams(self):
        kwds = super(TestDowntimeSessionCreate, self).mockCreateRequestParams()
        self.setStartsKwd(kwds)
        self.setEndsKwd(kwds)
        return kwds


class TestDowntimeSessionUpdate(ManipulatorTestCase):

    manipulatorClass = DowntimeSessionManipulator

    def mockObjectRegister(self):
        return self.registry.downtimeSessions

    def mockDomainObject(self):
        self.setupUpdatedObject()
        return self.updatedObject
        
    def test_update(self):
        self.failUnlessUpdate()

    def mockUpdateConstructorParams(self):
        params = super(TestDowntimeSessionUpdate, self).mockUpdateConstructorParams()
        self.setStartsParam(params) 
        self.setEndsParam(params) 
        return params


class TrainingSessionManipulatorTestCase(ManipulatorTestCase):

    requiredFieldNames = ['type', 'capacity', 'date', 'start', 'end',
        'location', 'presenter', 'researchers', 'comment', 'notes']

    def mockObjectRegister(self):
        return self.registry.trainingSessions

    def mockCreateRequestParams(self):
        params = super(TrainingSessionManipulatorTestCase, self
            ).mockCreateRequestParams()
        params['type'] = 'AED'
        params['date'] = '07-07-2008'
        params['start'] = '10:00'
        params['end'] = '11:45'
        params['capacity'] = '10'
        return params

    def mockUpdateConstructorParams(self):
        params = super(TrainingSessionManipulatorTestCase, self
            ).mockUpdateConstructorParams()
        params['type'] = self.registry.trainingSessionTypes['AED']
        params['starts'] = mx.DateTime.DateTime(2008,  7,  7, 10,  0,  0)
        params['ends'] = mx.DateTime.DateTime(2008,  7,  7, 11, 45,  0)
        return params

    def mockUpdateRequestParams(self):
        params = super(TrainingSessionManipulatorTestCase, self
            ).mockUpdateRequestParams()
        params['type'] = 'Oxygen'
        params['date'] = '08-07-2008'
        params['start'] = '11:00'
        params['end'] = '12:45'
        params['capacity'] = '10'
        return params


class TestTrainingSessionCreate(TrainingSessionManipulatorTestCase):

    manipulatorClass = TrainingSessionCreateManipulator

    def test_create(self):
        self.failUnlessCreate()
        self.failUnlessEqual(self.createdObject.type.name, 'AED')
        time = mx.DateTime.DateTime(2008,  7,  7, 10,  0,  0)
        self.failUnlessEqual(self.createdObject.starts, time)
        time = mx.DateTime.DateTime(2008,  7,  7, 11, 45,  0)
        self.failUnlessEqual(self.createdObject.ends, time)


class TestTrainingSessionUpdate(TrainingSessionManipulatorTestCase):

    manipulatorClass = TrainingSessionUpdateManipulator

    def test_update(self):
        self.failUnlessEqual(self.updatedObject.type.name, 'AED')
        time = mx.DateTime.DateTime(2008,  7,  7, 10,  0,  0)
        self.failUnlessEqual(self.updatedObject.starts, time)
        time = mx.DateTime.DateTime(2008,  7,  7, 11, 45,  0)
        self.failUnlessEqual(self.updatedObject.ends, time)
        self.failUnlessUpdate()
        self.failUnlessEqual(self.updatedObject.type.name, 'Oxygen')
        time = mx.DateTime.DateTime(2008,  7,  8, 11,  0,  0)
        self.failUnlessEqual(self.updatedObject.starts, time)
        time = mx.DateTime.DateTime(2008,  7,  8, 12, 45,  0)

    def mockDomainObject(self):
        self.setupUpdatedObject()
        return self.updatedObject
        

class ScanningSessionManipulatorTestCase(ManipulatorTestCase):

    def mockObjectRegister(self):
        return self.registry.scanningSessions

    def mockCreateRequestParams(self):
        params = super(ScanningSessionManipulatorTestCase, self
            ).mockCreateRequestParams()
        params['date'] = '07-08-2008'
        params['start'] = '10:00'
        params['end'] = '11:45'
        return params

    def mockUpdateConstructorParams(self):
        params = super(ScanningSessionManipulatorTestCase, self
            ).mockUpdateConstructorParams()
        self.setStartsParam(params) 
        self.setEndsParam(params) 
        self.setProjectParam(params) 
        return params

    def setProjectParam(self, params):
        params['project'] = self.registry.projects[1]

    def setApprovalParam(self, params):
        params['approval'] = self.registry.approvals[1]

    def setVolunteerParam(self, params):
        params['volunteer'] = self.registry.volunteers[1]

    def isSlaveView(self): # Mocks the behaviour of the inline form 'client'.
        return True


class TestScanningSessionCreate(ScanningSessionManipulatorTestCase):

    manipulatorClass = ScanningSessionCreateManipulator
    requiredFieldNames = ['start', 'end', 'date', 'scanId', 'project',
        'outcome', 'approval', 'volunteer']

    def test_create(self):
        self.failUnlessCreate()


class TestScanningSessionUpdate1(ScanningSessionManipulatorTestCase):

    manipulatorClass = ScanningSessionUpdateManipulator
    requiredFieldNames = ['project', 'leader', 'bookingOwnVolunteers',
        'approval']

    def test_update(self):
        self.failUnlessEqual(self.updatedObject.project.id, 1)
        self.failUnlessEqual(self.updatedObject.leader, None)
        self.failUnlessEqual(self.updatedObject.approval, None)
        researchers = self.manipulator.listProjectResearchers()
        self.failUnlessEqual(researchers[0].realname, u'Sonia Bishop \xf3')
        self.failUnlessEqual(researchers[1].realname, u'Alexandra Woogar \xf3')
        self.failUnlessUpdate()
        self.failUnlessEqual(self.updatedObject.leader.id, 3)
        self.failUnlessEqual(self.updatedObject.approval.id, 1)

    def mockDomainObject(self):
        self.setupUpdatedObject()
        return self.updatedObject
        
    def mockUpdateRequestParams(self):
        params = self.updatedObject.asRequestParams()
        params['approval'] = '1'
        params['leader'] = '3'
        return params


class TestScanningSessionUpdate2(TestScanningSessionUpdate1):

    manipulatorClass = ScanningSessionUpdateManipulator
    requiredFieldNames = ['project', 'leader', 'approval',
        'bookingOwnVolunteers', 'volunteer', 'outcome', 'scanId']

    def test_update(self):
        self.failUnlessEqual(self.updatedObject.project.id, 1)
        self.failUnlessEqual(self.updatedObject.approval.id, 1)
        self.failUnlessEqual(self.updatedObject.volunteer, None)
        self.failUnlessUpdate()
        self.failUnlessEqual(self.updatedObject.volunteer.id, 1)

    def mockUpdateConstructorParams(self):
        params = super(TestScanningSessionUpdate2, self
            ).mockUpdateConstructorParams()
        self.setApprovalParam(params) 
        return params

    def mockUpdateRequestParams(self):
        params = self.updatedObject.asRequestParams()
        params['volunteer'] = '1'
        return params


class TestScanningSessionUpdate3(TestScanningSessionUpdate2):

    manipulatorClass = ScanningSessionUpdateManipulator
    requiredFieldNames = ['project', 'leader', 'approval', 'outcome',
        'bookingOwnVolunteers', 'volunteer', 'scanId']

    def test_update(self):
        self.failUnlessEqual(self.updatedObject.project.id, 1)
        self.failUnlessEqual(self.updatedObject.approval.id, 1)
        self.failUnlessEqual(self.updatedObject.volunteer.id, 1)
        self.failUnlessUpdate()

    def mockUpdateConstructorParams(self):
        params = super(TestScanningSessionUpdate2, self
            ).mockUpdateConstructorParams()
        self.setApprovalParam(params)
        self.setVolunteerParam(params)
        return params

    def mockUpdateRequestParams(self):
        params = self.updatedObject.asRequestParams()
        return params


class TestApprovalExpires(TestScanningSessionUpdate1):

    def setSetting(self, settingName, value):
        settings = self.registry.settings['default']
        setattr(settings, settingName, value)
        settings.save()
    
    def getSetting(self, settingName):
        settings = self.registry.settings['default']
        return getattr(settings, settingName)

    def test_update(self):
        self.setSetting('requireEthicsApprovalInDate', False)
        try:
            self.failIf(self.getSetting('requireEthicsApprovalInDate'))
            self.failUnlessEqual(self.updatedObject.project.id, 4)
            self.failUnlessEqual(self.updatedObject.approval, None)
            self.failUnlessUpdate()
            self.failUnlessEqual(self.updatedObject.approval.id, 4)
        finally:
            self.setSetting('requireEthicsApprovalInDate', True)

    def test_update_on(self):
        self.setSetting('requireEthicsApprovalInDate', True)
        self.failUnless(self.getSetting('requireEthicsApprovalInDate'))
        self.failUnlessEqual(self.updatedObject.project.id, 4)
        self.failUnlessEqual(self.updatedObject.approval, None)
        self.failUnlessValidationError(
            "Ethics approval expires before session ends."
        )

    def setProjectParam(self, params):
        params['project'] = self.registry.projects[4]

    def mockUpdateRequestParams(self):
        params = self.updatedObject.asRequestParams()
        params['approval'] = '4'
        return params


class ApprovalManipulatorTestCase(ManipulatorTestCase):

    manipulatorClass = ApprovalManipulator

    def mockObjectRegister(self):
        return self.registry.approvals

    def mockCreateRequestParams(self):
        params = super(
            ApprovalManipulatorTestCase, self
        ).mockCreateRequestParams()
        self.setCodeParam(params) 
        return params

    def setCodeParam(self, params):
        params['code'] = 'test-999'

    def tearDown(self):
        r = self.registry.approvals
        [i.delete() for i in r.findDomainObjects(code='test-888')]
        [i.delete() for i in r.findDomainObjects(code='test-999')]
        super(ApprovalManipulatorTestCase, self).tearDown()


class TestApprovalCreateOK(ApprovalManipulatorTestCase):

    def test_create(self):
        self.failUnlessCreate()


class TestApprovalCreateCodeInUse(ApprovalManipulatorTestCase):

    def test_create(self):
        self.failIf(self.manipulator.domainObject, "Existing object before.")
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failUnless(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.approval1 = self.registry.approvals.create(code='test-999')
        super(TestApprovalCreateCodeInUse, self).setUp()

    def tearDown(self):
        self.approval1.delete()
        super(TestApprovalCreateCodeInUse, self).tearDown()


class TestApprovalUpdateOK(ApprovalManipulatorTestCase):

    def test_create(self):
        self.failUnless(self.manipulator.domainObject)
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failIf(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.approval1 = self.registry.approvals.create(code='test-999')
        super(TestApprovalUpdateOK, self).setUp()

    def tearDown(self):
        self.approval1.delete()
        super(TestApprovalUpdateOK, self).tearDown()

    def mockDomainObject(self):
        return self.approval1


class TestApprovalUpdateCodeInUse(ApprovalManipulatorTestCase):

    def test_create(self):
        self.failUnless(self.manipulator.domainObject)
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failUnless(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.approval1 = self.registry.approvals.create(code='test-888')
        self.approval2 = self.registry.approvals.create(code='test-999')
        super(TestApprovalUpdateCodeInUse, self).setUp()

    def tearDown(self):
        self.approval2.delete()
        self.approval1.delete()
        super(TestApprovalUpdateCodeInUse, self).tearDown()

    def mockDomainObject(self):
        return self.approval1


class ProjectManipulatorTestCase(ManipulatorTestCase):

    manipulatorClass = ProjectManipulator
    requiredFieldNames = ['title', 'nickname', 'leader', 'account', 'researchers', 'approvals', 'funding', 'status', 'outcome', 'preparationMinutes', 'volunteerBookingMethod', 'IIGPresentation', 'IMCApproval', 'numberSubjects', 'numberPilots', 'slotMinutes', 'volunteerType', 'startDate', 'completionDate', 'notes']

    def tearDown(self):
        r = self.registry.projects
        [i.delete() for i in r.findDomainObjects(title='test-888')]
        [i.delete() for i in r.findDomainObjects(title='test-999')]
        super(ProjectManipulatorTestCase, self).tearDown()

    def mockObjectRegister(self):
        return self.registry.projects

    def mockCreateRequestParams(self):
        params = super(
            ProjectManipulatorTestCase, self
        ).mockCreateRequestParams()
        self.setTitleParam(params) 
        params['preparationMinutes'] = '1'
        params['slotMinutes'] = '1'
        return params

    def setTitleParam(self, params):
        params['title'] = 'test-999'


class TestProjectCreateOK(ProjectManipulatorTestCase):

    def test_create(self):
        self.failUnlessCreate()


class TestProjectCreateTitleInUse(ProjectManipulatorTestCase):

    def test_create(self):
        self.failIf(self.manipulator.domainObject, "Existing object before.")
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failUnless(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.project1 = self.registry.projects.create(title='test-999')
        super(TestProjectCreateTitleInUse, self).setUp()

    def tearDown(self):
        self.project1.delete()
        super(TestProjectCreateTitleInUse, self).tearDown()


class TestProjectUpdateOK(ProjectManipulatorTestCase):

    def test_create(self):
        self.failUnless(self.manipulator.domainObject)
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failIf(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.project1 = self.registry.projects.create(title='test-999')
        super(TestProjectUpdateOK, self).setUp()

    def tearDown(self):
        self.project1.delete()
        super(TestProjectUpdateOK, self).tearDown()

    def mockDomainObject(self):
        return self.project1


class TestProjectUpdateTitleInUse(ProjectManipulatorTestCase):

    def test_create(self):
        self.failUnless(self.manipulator.domainObject)
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failUnless(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.project1 = self.registry.projects.create(
            title='test-888', preparationMinutes=1, slotMinutes=1)
        self.project2 = self.registry.projects.create(
            title='test-999', preparationMinutes=1, slotMinutes=1)
        super(TestProjectUpdateTitleInUse, self).setUp()

    def tearDown(self):
        self.project2.delete()
        self.project1.delete()
        super(TestProjectUpdateTitleInUse, self).tearDown()

    def mockDomainObject(self):
        return self.project1


class VolunteerManipulatorTestCase(ManipulatorTestCase):

    manipulatorClass = VolunteerManipulator

    def tearDown(self):
        r = self.registry.volunteers
        [i.delete() for i in r.findDomainObjects(realname='test-888')]
        [i.delete() for i in r.findDomainObjects(realname='test-999')]
        super(VolunteerManipulatorTestCase, self).tearDown()

    def mockObjectRegister(self):
        return self.registry.volunteers

    def mockCreateRequestParams(self):
        params = super(
            VolunteerManipulatorTestCase, self
        ).mockCreateRequestParams()
        self.setRealnameParam(params) 
        self.setPanelIdParam(params) 
        return params

    def setRealnameParam(self, params):
        params['realname'] = 'test-999'

    def setPanelIdParam(self, params):
        params['panelId'] = 'test-999'


class TestVolunteerCreateOK(VolunteerManipulatorTestCase):

    def test_create(self):
        self.failUnlessCreate()


class TestVolunteerCreateRealnameInUse(VolunteerManipulatorTestCase):

    def test_create(self):
        self.failIf(self.manipulator.domainObject, "Existing object before.")
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failUnless(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.volunteer1 = self.registry.volunteers.create(realname='test-999')
        super(TestVolunteerCreateRealnameInUse, self).setUp()

    def tearDown(self):
        self.volunteer1.delete()
        super(TestVolunteerCreateRealnameInUse, self).tearDown()


class TestVolunteerCreatePanelIdInUse(VolunteerManipulatorTestCase):

    def test_create(self):
        self.failIf(self.manipulator.domainObject, "Existing object before.")
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failUnless(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.volunteer1 = self.registry.volunteers.create(
            realname='test', panelId='test-999')
        super(TestVolunteerCreatePanelIdInUse, self).setUp()

    def tearDown(self):
        self.volunteer1.delete()
        super(TestVolunteerCreatePanelIdInUse, self).tearDown()


class TestVolunteerUpdateOK(VolunteerManipulatorTestCase):

    def test_create(self):
        self.failUnless(self.manipulator.domainObject)
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failIf(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.volunteer1 = self.registry.volunteers.create(
            realname='test', panelId='test-888')
        super(TestVolunteerUpdateOK, self).setUp()

    def tearDown(self):
        self.volunteer1.delete()
        super(TestVolunteerUpdateOK, self).tearDown()

    def mockDomainObject(self):
        return self.volunteer1


class TestVolunteerUpdateRealnameInUse(VolunteerManipulatorTestCase):

    def test_create(self):
        self.failUnless(self.manipulator.domainObject)
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failUnless(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.volunteer1 = self.registry.volunteers.create(realname='test-888')
        self.volunteer2 = self.registry.volunteers.create(realname='test-999')
        super(TestVolunteerUpdateRealnameInUse, self).setUp()

    def tearDown(self):
        self.volunteer2.delete()
        self.volunteer1.delete()
        super(TestVolunteerUpdateRealnameInUse, self).tearDown()

    def mockDomainObject(self):
        return self.volunteer1


class TestVolunteerUpdatePanelIdInUse(VolunteerManipulatorTestCase):

    def test_create(self):
        self.failUnless(self.manipulator.domainObject)
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failUnless(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.volunteer1 = self.registry.volunteers.create(
            realname='test-888-8', panelId='test-888-8')
        self.volunteer2 = self.registry.volunteers.create(
            realname='test-999-9', panelId='test-999')
        super(TestVolunteerUpdatePanelIdInUse, self).setUp()

    def tearDown(self):
        self.volunteer2.delete()
        self.volunteer1.delete()
        super(TestVolunteerUpdatePanelIdInUse, self).tearDown()

    def mockDomainObject(self):
        return self.volunteer1


class AccountManipulatorTestCase(ManipulatorTestCase):

    manipulatorClass = AccountManipulator

    def tearDown(self):
        r = self.registry.accounts
        [i.delete() for i in r.findDomainObjects(code='test-888')]
        [i.delete() for i in r.findDomainObjects(code='test-999')]
        super(AccountManipulatorTestCase, self).tearDown()

    def mockObjectRegister(self):
        return self.registry.accounts

    def mockCreateRequestParams(self):
        params = super(
            AccountManipulatorTestCase, self
        ).mockCreateRequestParams()
        self.setCodeParam(params) 
        return params

    def setCodeParam(self, params):
        params['code'] = 'test-999'


class TestAccountCreateOK(AccountManipulatorTestCase):

    def test_create(self):
        self.failUnlessCreate()


class TestAccountCreateCodeInUse(AccountManipulatorTestCase):

    def test_create(self):
        self.failIf(self.manipulator.domainObject, "Existing object before.")
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failUnless(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.account1 = self.registry.accounts.create(code='test-999')
        super(TestAccountCreateCodeInUse, self).setUp()

    def tearDown(self):
        self.account1.delete()
        super(TestAccountCreateCodeInUse, self).tearDown()


class TestAccountUpdateOK(AccountManipulatorTestCase):

    def test_create(self):
        self.failUnless(self.manipulator.domainObject)
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failIf(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.account1 = self.registry.accounts.create(code='test')
        super(TestAccountUpdateOK, self).setUp()

    def tearDown(self):
        self.account1.delete()
        super(TestAccountUpdateOK, self).tearDown()

    def mockDomainObject(self):
        return self.account1


class TestAccountUpdateCodeInUse(AccountManipulatorTestCase):

    def test_create(self):
        self.failUnless(self.manipulator.domainObject)
        requestParams = self.mockCreateRequestParams()
        errors = self.manipulator.getValidationErrors(requestParams)
        self.failUnless(errors, "Validation errors: %s" % errors)

    def setUp(self):
        self.account1 = self.registry.accounts.create(code='test-888')
        self.account2 = self.registry.accounts.create(code='test-999')
        super(TestAccountUpdateCodeInUse, self).setUp()

    def tearDown(self):
        self.account2.delete()
        self.account1.delete()
        super(TestAccountUpdateCodeInUse, self).tearDown()

    def mockDomainObject(self):
        return self.account1


#class TestResearcherManipulator_Create(ManipulatorTestCase):
#
#    manipulatorClass = ResearcherManipulator
#
#    def mockObjectRegister(self):
#        return self.registry.researchers
#
#    def test_create(self):
#        self.failUnlessCreate()
#
#
#class TestResearcherManipulator_Update(ManipulatorTestCase):
#
#    manipulatorClass = ResearcherManipulator
#
#    def mockDomainObject(self):
#        self.setupUpdatedObject()
#        return self.updatedObject
#        
#    def mockObjectRegister(self):
#        return self.registry.researchers
#
#    def test_update(self):
#        self.failUnlessUpdate()
#
#
#
#
#class TestSessionTimeManipulator(ManipulatorTestCase):
#
#    manipulatorClass = SessionTimeManipulator
#
#    def mockObjectRegister(self):
#        return self.registry.scanningSessions
#
#
#class TestPersonManipulator(ManipulatorTestCase):
#
#    manipulatorClass = PersonManipulator
#
#    def mockObjectRegister(self):
#        return self.registry.persons
#
#
#class TestPrincipalInvestigatorCreateManipulator(ManipulatorTestCase):
#
#    manipulatorClass = PrincipalInvestigatorCreateManipulator
#
#    def mockObjectRegister(self):
#        return self.registry.researchers
#
#
#class TestResearcherCreateManipulator(ManipulatorTestCase):
#
#    manipulatorClass = ResearcherCreateManipulator
#
#    def mockObjectRegister(self):
#        return self.registry.researchers
#
#
#class TestPersonCreateManipulator(ManipulatorTestCase):
#
#    manipulatorClass = PersonCreateManipulator
#
#    def mockObjectRegister(self):
#        return self.registry.persons
#
#
#class TestPersonApproveManipulator(ManipulatorTestCase):
#
#    manipulatorClass = PersonApproveManipulator
#
#    def mockObjectRegister(self):
#        return self.registry.persons
#
#
#class TestPersonUpdateManipulator(ManipulatorTestCase):
#
#    manipulatorClass = PersonUpdateManipulator
#
#    def mockObjectRegister(self):
#        return self.registry.persons
#
#
#class TestPersonUpdateManipulatorAdmin(ManipulatorTestCase):
#
#    manipulatorClass = PersonUpdateManipulatorAdmin
#
#    def mockObjectRegister(self):
#        return self.registry.persons
#
#
#class TestReportManipulator(ManipulatorTestCase):
#
#    manipulatorClass = ReportManipulator
#
#    def mockObjectRegister(self):
#        return self.registry.reports
#
#

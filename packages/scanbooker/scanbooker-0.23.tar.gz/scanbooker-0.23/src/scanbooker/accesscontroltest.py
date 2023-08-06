import unittest
import scanbooker.accesscontrol
from scanbooker.testunit import TestCase
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestRoles),
        unittest.makeSuite(TestRoleAccess),
        unittest.makeSuite(TestAccessController),
        unittest.makeSuite(TestScanningSessionAccess),
        unittest.makeSuite(TestApprovalAccess),
        unittest.makeSuite(TestGroupAccess),
        unittest.makeSuite(TestProjectAccess),
        unittest.makeSuite(TestReportAccess),
    ]
    return unittest.TestSuite(suites)

class TestRoles(TestCase):

    def testRoleRecords(self):
        self.failUnless(self.registry.roles)
        self.failUnlessEqual(len(self.registry.roles), 5)
        self.failUnless(self.registry.roles['Administrator'])
        self.failUnless(self.registry.roles['PrincipalInvestigator'])
        self.failUnless(self.registry.roles['Researcher'])
        self.failUnless(self.registry.roles['Staff'])
        self.failUnless(self.registry.roles['Visitor'])


class AccessControllerTestCase(TestCase):

    def setUp(self):
        super(AccessControllerTestCase, self).setUp()
        self.ac = scanbooker.accesscontrol.AccessController()
        self.person = None
        self.actionName = ''
        self.object = None

    def isAuthorised(self):
        return self.ac.isAuthorised(
            person=self.person,
            actionName=self.actionName,
            protectedObject=self.protectedObject,
        )

    def isPermissionSet(self, role):
        return self.ac.isPermissionSet(role.grants, 'authorised', 'test case')

    def getDomainClass(self, className):
        return self.registry.getDomainClass(className)
        

class TestRoleAccess(AccessControllerTestCase):

    def setUp(self):
        super(TestRoleAccess, self).setUp()

    def testAdminAccess(self):
        adminRole = self.registry.roles['Administrator']
        
        self.ac.setProtectedObject(self.getDomainClass('System'))
        self.ac.setAction('Create')
        self.failUnless(self.isPermissionSet(adminRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(adminRole))
        self.ac.setAction('Update')
        self.failUnless(self.isPermissionSet(adminRole))
        self.ac.setAction('Delete')
        self.failUnless(self.isPermissionSet(adminRole))
        
        self.ac.setProtectedObject(self.getDomainClass('EarmarkedTime'))
        self.ac.setAction('Create')
        self.failUnless(self.isPermissionSet(adminRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(adminRole))
        self.ac.setAction('Update')
        self.failUnless(self.isPermissionSet(adminRole))
        self.ac.setAction('Delete')
        self.failUnless(self.isPermissionSet(adminRole))
        
        self.ac.setProtectedObject(self.getDomainClass('MaintenanceSession'))
        self.ac.setAction('Create')
        self.failUnless(self.isPermissionSet(adminRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(adminRole))
        self.ac.setAction('Update')
        self.failUnless(self.isPermissionSet(adminRole))
        self.ac.setAction('Delete')
        self.failUnless(self.isPermissionSet(adminRole))

        self.ac.setProtectedObject(self.getDomainClass('ScanningSession'))
        self.ac.setAction('Create')
        self.failUnless(self.isPermissionSet(adminRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(adminRole))
        self.ac.setAction('Update')
        self.failUnless(self.isPermissionSet(adminRole))
        self.ac.setAction('Delete')
        self.failUnless(self.isPermissionSet(adminRole))

    def testPrincipalInvestigatorAccess(self):
        piRole = self.registry.roles['PrincipalInvestigator']

        self.ac.setProtectedObject(self.getDomainClass('System'))
        self.ac.setAction('Create')
        self.failIf(self.isPermissionSet(piRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Update')
        self.failIf(self.isPermissionSet(piRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(piRole))
 
        self.ac.setProtectedObject(self.getDomainClass('EarmarkedTime'))
        self.ac.setAction('Create')
        self.failIf(self.isPermissionSet(piRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Update')
        self.failIf(self.isPermissionSet(piRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(piRole))

        self.ac.setProtectedObject(self.getDomainClass('MaintenanceSession'))
        self.ac.setAction('Create')
        self.failIf(self.isPermissionSet(piRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Update')
        self.failIf(self.isPermissionSet(piRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(piRole))

        self.ac.setProtectedObject(self.getDomainClass('ScanningSession'))
        self.ac.setAction('Create')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Update')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Delete')
        self.failUnless(self.isPermissionSet(piRole))

        self.ac.setProtectedObject(self.getDomainClass('Approval'))
        self.ac.setAction('Create')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Update')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(piRole))

        self.ac.setProtectedObject(self.getDomainClass('Project'))
        self.ac.setAction('Create')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Update')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(piRole))

        self.ac.setProtectedObject(self.getDomainClass('Group'))
        self.ac.setAction('Create')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Update')
        self.failUnless(self.isPermissionSet(piRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(piRole))

    
    def testResearcherAccess(self):
        researcherRole = self.registry.roles['Researcher']

        self.ac.setProtectedObject(self.getDomainClass('System'))
        self.ac.setAction('Create')
        self.failIf(self.isPermissionSet(researcherRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(researcherRole))
        self.ac.setAction('Update')
        self.failIf(self.isPermissionSet(researcherRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(researcherRole))
 
        self.ac.setProtectedObject(self.getDomainClass('EarmarkedTime'))
        self.ac.setAction('Create')
        self.failIf(self.isPermissionSet(researcherRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(researcherRole))
        self.ac.setAction('Update')
        self.failIf(self.isPermissionSet(researcherRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(researcherRole))

        self.ac.setProtectedObject(self.getDomainClass('MaintenanceSession'))
        self.ac.setAction('Create')
        self.failIf(self.isPermissionSet(researcherRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(researcherRole))
        self.ac.setAction('Update')
        self.failIf(self.isPermissionSet(researcherRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(researcherRole))

        self.ac.setProtectedObject(self.getDomainClass('ScanningSession'))
        self.ac.setAction('Create')
        self.failUnless(self.isPermissionSet(researcherRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(researcherRole))
        self.ac.setAction('Update')
        self.failIf(self.isPermissionSet(researcherRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(researcherRole))

    def testStaffAccess(self):
        staffRole = self.registry.roles['Staff']

        self.ac.setProtectedObject(self.getDomainClass('System'))
        self.ac.setAction('Create')
        self.failIf(self.isPermissionSet(staffRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(staffRole))
        self.ac.setAction('Update')
        self.failIf(self.isPermissionSet(staffRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(staffRole))
 
        self.ac.setProtectedObject(self.getDomainClass('EarmarkedTime'))
        self.ac.setAction('Create')
        self.failIf(self.isPermissionSet(staffRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(staffRole))
        self.ac.setAction('Update')
        self.failIf(self.isPermissionSet(staffRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(staffRole))

        self.ac.setProtectedObject(self.getDomainClass('ScanningSession'))
        self.ac.setAction('Create')
        self.failIf(self.isPermissionSet(staffRole))
        self.ac.setAction('Read')
        self.failUnless(self.isPermissionSet(staffRole))
        self.ac.setAction('Update')
        self.failIf(self.isPermissionSet(staffRole))
        self.ac.setAction('Delete')
        self.failIf(self.isPermissionSet(staffRole))


class TestAccessController(AccessControllerTestCase):

    def test_isAdminAuthorised(self):
        self.person = self.registry.persons['lmurby']
        self.failUnlessEqual(self.person.role.name, 'Administrator')
        self.protectedObject = self.registry.getDomainClass('System')
        self.actionName = 'Create'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Delete'
        self.failUnless(self.isAuthorised())
        self.protectedObject = self.registry.getDomainClass('EarmarkedTime')
        self.actionName = 'Create'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Delete'
        self.failUnless(self.isAuthorised())
        self.protectedObject = self.registry.getDomainClass('ScanningSession')
        self.actionName = 'Create'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Delete'
        self.failUnless(self.isAuthorised())

    def test_isResearcherAuthorised(self):
        self.person = self.registry.persons['sbishop']
        self.failUnlessEqual(self.person.role.name, 'Researcher')
        self.protectedObject = self.registry.getDomainClass('System')
        self.actionName = 'Create'
        self.failIf(self.isAuthorised())
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())
        self.protectedObject = self.registry.getDomainClass('EarmarkedTime')
        self.actionName = 'Create'
        self.failIf(self.isAuthorised())
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())
        self.protectedObject = self.registry.getDomainClass('ScanningSession')
        self.actionName = 'Create'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())

    def test_isStaffAuthorised(self):
        self.person = self.registry.persons['rcusack']
        self.failUnlessEqual(self.person.role.name, 'Staff')
        self.protectedObject = self.registry.getDomainClass('System')
        self.actionName = 'Create'
        self.failIf(self.isAuthorised())
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())
        self.protectedObject = self.registry.getDomainClass('EarmarkedTime')
        self.actionName = 'Create'
        self.failIf(self.isAuthorised())
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())
        self.protectedObject = self.registry.getDomainClass('ScanningSession')
        self.actionName = 'Create'
        self.failIf(self.isAuthorised())
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())

        
class TestScanningSessionAccess(AccessControllerTestCase):

    def setUp(self):
        super(TestScanningSessionAccess, self).setUp()
        self.person = self.registry.persons['sbishop']
        self.failUnlessEqual(self.person.role.name, 'Researcher')
        
        self.protectedObject = self.registry.scanningSessions.create(
            starts=mx.DateTime.DateTime(2007, 6, 6, 12, 0, 0),
            ends = mx.DateTime.DateTime(2007, 6, 6, 13, 0, 0),
            createdBy = self.person
        )

    def tearDown(self):
        super(TestScanningSessionAccess, self).tearDown()
        self.protectedObject.delete()
        
    def test_isOwnProjectAuthorised(self):
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Delete'
        self.failUnless(self.isAuthorised())
        
    def test_AdminAccessToResearcherCreatedProject(self):
        self.person = self.registry.persons['lmurby']
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Delete'
        self.failUnless(self.isAuthorised())

    def test_ResearcherAccessToResearcherCreatedProject(self):
        self.person = self.registry.persons['aowen']
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())

    def test_StaffAccessToResearcherCreatedProject(self):
        self.person = self.registry.persons['rcusack']
        self.failIf(self.isAuthorised())
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())


class ObjectAccessTestCase(AccessControllerTestCase):

    def failUnlessValidActionNames(self, acProfile):
        for actionName in acProfile['allowedActionNames']:
            self.actionName = actionName
            self.failUnless(self.isAuthorised(), "Person '%s' NOT authorised to '%s' protected object %s." % (
                self.person.name,
                self.actionName,
                self.protectedObject,
            ))
        for actionName in acProfile['deniedActionNames']:
            self.actionName = actionName
            self.failIf(self.isAuthorised(), "Person '%s' IS authorised to '%s' protected object %s." % (
                self.person.name,
                self.actionName,
                self.protectedObject,
            ))
        
    def failUnlessValidAccessProfile(self, acProfile):
        registryAttributeName = acProfile['registryName']
        register = getattr(self.registry, registryAttributeName)
        objectAttributeName = acProfile['attributeName']
        for objectProfile in acProfile['domainObjects']:
            objectAttributeValue = objectProfile['attributeValue']
            kwds = {objectAttributeName: objectAttributeValue}
            self.protectedObject = register.findSingleDomainObject(**kwds)
            for personProfile in objectProfile['persons']:
                personName = personProfile['name']
                self.person = self.registry.persons[personName]
                self.failUnlessValidActionNames(personProfile)
            

class TestApprovalAccess(ObjectAccessTestCase):
    
    def test_isAuthorised(self):
        self.failUnlessValidAccessProfile({
            'registryName':                'approvals',
            'attributeName':               'code',
            'domainObjects': [{
                'attributeValue':          '456-654-1',
                'persons': [{
                    'name':                'aowen',
                    'allowedActionNames': ['Read'],
                    'deniedActionNames':  ['Update', 'Delete'],
                 }, {
                    'name':                'rcusack',
                    'allowedActionNames': [],
                    'deniedActionNames':  ['Read', 'Update', 'Delete'],
                 }]
             }, {
                'attributeValue':          '456-654-2',
                'persons': [{
                    'name':                'aowen',
                    'allowedActionNames': ['Read'],
                    'deniedActionNames':  ['Update', 'Delete'],
                 }, {
                    'name':                'rcusack',
                    'allowedActionNames': [],
                    'deniedActionNames':  ['Read', 'Update', 'Delete'],
                 }]
             }, {
                'attributeValue':          '456-654-3',
                'persons': [{
                    'name':                'aowen',
                    'allowedActionNames': ['Read', 'Update'],
                    'deniedActionNames':  ['Delete'],
                 }, {
                    'name':                'rcusack',
                    'allowedActionNames': ['Read'],
                    'deniedActionNames':  ['Update', 'Delete'],
                 }]
             }]
        })

        
class TestGroupAccess(AccessControllerTestCase):

    def test_isAuthorised(self):
        self.protectedObject = self.registry.groups.findSingleDomainObject(
            abbreviation='EMO'
        )
        self.person = self.registry.persons['aowen']
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())
        
        self.person = self.registry.persons['rcusack']
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())
        
        self.protectedObject = self.registry.groups.findSingleDomainObject(
            abbreviation='ATT'
        )
        self.person = self.registry.persons['aowen']
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())
        
        self.person = self.registry.persons['rcusack']
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())
        

class TestProjectAccess(AccessControllerTestCase):
 
    def test_isAuthorised(self):
        self.protectedObject = self.registry.projects.findSingleDomainObject(
            title="My First Project"
        )
        # project leader
        self.person = self.registry.persons['sbishop']
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())
        
        # project researcher
        self.person = self.registry.persons['awoogar']
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())
        
        # group principal
        self.person = self.registry.persons['aowen']
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())
        
        # group researcher
        self.person = self.registry.persons['rcusack']
        self.actionName = 'Read'
        self.failIf(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())
        

class TestReportAccess(AccessControllerTestCase):
 
    def setUp(self):
        super(TestReportAccess, self).setUp()
        self.protectedObject = self.registry.reports.create(title='Access Control Test')

    def tearDown(self):
        super(TestReportAccess, self).tearDown()
        self.protectedObject.delete()
        self.protectedObject.purge()
 
    def test_AdminAccess(self):
        self.person = self.registry.persons['lmurby']
        self.actionName = 'Read'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Update'
        self.failUnless(self.isAuthorised())
        self.actionName = 'Delete'
        self.failUnless(self.isAuthorised())

    def test_ResearcherAccess(self):
        self.person = self.registry.persons['aowen']
        self.actionName = 'Read'
        self.failIf(self.isAuthorised())
        self.actionName = 'Update'
        self.failIf(self.isAuthorised())
        self.actionName = 'Delete'
        self.failIf(self.isAuthorised())


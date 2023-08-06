from scanbooker.django.apps.sui.test.base import CuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestReadPackages),
        unittest.makeSuite(TestPackageCRUD),
    ]
    return unittest.TestSuite(suites)


class TestReadPackages(CuiTestCase):
  
    packageName = 'administration'
  
    def testPackageIndex(self):
        self.getAssertContent('/package/', 'Registered packages')
        self.getAssertContent('/package/search/', 'Search packages')

    def testPackageSearch(self):
        params = {'userQuery': 'z'}
        self.postAssertNotContent('/package/search/', params, self.packageName)
        params = {'userQuery': 'a'}
        self.postAssertContent('/package/search/', params, self.packageName)
        
    def testPackageRead(self):
        self.getAssertContent(
            '/package/%s/' % self.packageName,
            'Short name:'
        )
        self.getAssertContent(
            '/package/%s/' % self.packageName,
            self.packageName
        )
        
    def testMembersRead(self):
        self.getAssertContent(
            '/package/%s/members/' % self.packageName, 
            'Here are all the members'
        )
        self.getAssertContent(
            '/package/%s/members/' % self.packageName, 
            self.packageName
        )
        self.getAssertContent(
            '/package/%s/members/' % self.packageName, 
            'Administrator'
        )
        self.getAssertContent(
            '/package/%s/members/' % self.packageName, 
            'Visitor'
        )
        
    def testServicesRead(self):
        self.getAssertContent(
            '/package/%s/services/' % self.packageName, 
            self.packageName
        )


class TestPackageCRUD(CuiTestCase):

    def setUp(self):
        super(TestPackageCRUD, self).setUp()
        self.registerPerson()
        self.loginPerson()

    def tearDown(self):
        self.deletePerson()
        if self.suiPackageName in self.system.registry.packages:
            package = self.system.registry.packages[self.cuiPackageName]
            package.delete()
            package.purge()


    def testCRUD(self):
        # Create
        self.failIf(self.cuiPackageName in self.system.registry.packages)
        requiredContent = 'Register a new package'
        self.getAssertContent('/package/create/', requiredContent)
        requiredContent = 'Please enter the details of your new package below'
        self.getAssertContent('/package/create/', requiredContent)
        params = {}
        params['title'] = self.cuiPackageFullname
        params['purpose'] = self.cuiPackagePurpose
        params['licenses'] = self.cuiPackageLicense
        params['description'] = self.cuiPackageDescription
        params['name'] = self.cuiPackageName
        self.post('/package/create/', params)
        self.failUnless(self.cuiPackageName in self.system.registry.packages)
        package = self.system.registry.packages[self.cuiPackageName]
        person = self.system.registry.persons[self.cuiPersonName]
        self.failUnless(person in package.members)
        membership = package.members[person]
        self.failUnlessEqual(membership.role.name, 'Administrator')

        # Read
        self.failUnless(self.cuiPackageName in self.system.registry.packages)
        testLocation = '/package/%s/' % self.cuiPackageName
        requiredContent = 'Edit'
        self.getAssertContent(testLocation, requiredContent)
        requiredContent = 'Delete'
        self.getAssertContent(testLocation, requiredContent)
        requiredContent = '%s' % self.cuiPackageName
        self.getAssertContent(testLocation, requiredContent)
        requiredContent = '%s' % self.cuiPackageDescription
        self.getAssertContent(testLocation, requiredContent)
        requiredContent = '%s' % self.cuiPackageFullname
        self.getAssertContent(testLocation, requiredContent)
        
        # Update
        self.failUnless(self.cuiPackageName in self.system.registry.packages)
        requiredContent = 'Edit package' 
        self.getAssertContent('/package/%s/edit/' % self.cuiPackageName, requiredContent)
        self.getAssertContent('/package/%s/edit/' % self.cuiPackageName, self.cuiPackageName)
        self.getAssertContent('/package/%s/edit/' % self.cuiPackageName, self.cuiPackageFullname)
        self.getAssertContent('/package/%s/edit/' % self.cuiPackageName, self.cuiPackageDescription)

        # Delete
        self.failUnless(self.cuiPackageName in self.system.registry.packages)
        params = {}
        params['submit'] = 'submit'
        self.post('/package/%s/delete/' % self.cuiPackageName, params)
        self.failIf(self.cuiPackageName in self.system.registry.packages)


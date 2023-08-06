import unittest
from scanbooker.django.apps.sui.views.test.base import AdminSessionViewTestCase
from scanbooker.django.apps.sui.views.registry import ScanBookerRegistryListView
from scanbooker.django.apps.sui.views.registry import ScanBookerRegistryUpdateView
from scanbooker.django.apps.sui.views.registry import ScanBookerRegistryReadView
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestMaintenanceListView),
        unittest.makeSuite(TestSessionUpdateView),
        unittest.makeSuite(TestApprovalReadView),
        unittest.makeSuite(TestApprovalUpdateView),
        unittest.makeSuite(TestGroupReadView),
        unittest.makeSuite(TestGroupUpdateView),
        unittest.makeSuite(TestGroupListView),
        unittest.makeSuite(TestOrganisationReadView),
        unittest.makeSuite(TestOrganisationUpdateView),
        unittest.makeSuite(TestOrganisationListView),
        unittest.makeSuite(TestAccountReadView),
        unittest.makeSuite(TestAccountUpdateView),
        unittest.makeSuite(TestAccountListView),
    ]
    return unittest.TestSuite(suites)


# Todo: Extract to domainmodel.
class ScanBookerRegistryViewTestCase(AdminSessionViewTestCase):

    def createViewKwds(self):
        viewKwds = super(ScanBookerRegistryViewTestCase, self).createViewKwds()
        viewKwds['registryPath'] = self.registryPath
        return viewKwds


class TestMaintenanceListView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryListView
    registryPath = 'maintenanceSessions'


class TestApprovalListView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryListView
    registryPath = 'approvals'


class TestApprovalReadView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryReadView
    registryPath = 'approvals/1'


class TestApprovalUpdateView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryUpdateView
    registryPath = 'approvals/1'


class TestGroupListView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryListView
    registryPath = 'groups'


class TestGroupReadView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryReadView
    registryPath = 'groups/1'


class TestGroupUpdateView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryUpdateView
    registryPath = 'groups/1'


class TestOrganisationListView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryListView
    registryPath = 'organisations'


class TestOrganisationReadView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryReadView
    registryPath = 'organisations/1'


class TestOrganisationUpdateView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryUpdateView
    registryPath = 'organisations/1'


class TestAccountListView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryListView
    registryPath = 'accounts'


class TestAccountReadView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryReadView
    registryPath = 'accounts/1'


class TestAccountUpdateView(ScanBookerRegistryViewTestCase):

    viewClass = ScanBookerRegistryUpdateView
    registryPath = 'accounts/1'


class SessionUpdateTestCase(ScanBookerRegistryViewTestCase):

    sessionKey = None
    
    def setUp(self):
        self.sessions = self.registry.scanningSessions
        self.createSession()
        try:
            self.createRegistryPath()
            super(SessionUpdateTestCase, self).setUp()
        except:
            self.session.delete()
            raise

    def tearDown(self):
        super(SessionUpdateTestCase, self).tearDown()
        if self.sessionKey:
            session = self.sessions[self.sessionKey]
            session.delete()
            session.purge()

    def createRegistryPath(self):
        self.registryPath = '%s/%s' % (
            self.session.getRegistryAttrName(),
            self.session.getRegisterKeyValue()
        )

    def createSession(self):
        self.starts = mx.DateTime.Date(2007, 6, 14,  8, 30, 0)
        self.ends   = mx.DateTime.Date(2007, 6, 14, 10,  0, 0)
        self.organisation = self.registry.organisations[1]
        self.scanner = self.registry.scanners['MRI']
        self.session = self.sessions.create(
            scanner=self.scanner, starts=self.starts, ends=self.ends
        )
        self.sessionKey = self.session.getRegisterKeyValue()

    def test_getResponse(self):
        session = self.sessions[self.sessionKey]
        self.failIfSessionIsChanged(session)
        self.view.getResponse()
        session = self.sessions[self.sessionKey]
        self.failUnlessSessionIsChanged(session)

    def failIfSessionIsChanged(self, session):
        self.fail("Test not implemented.")

    def failUnlessSessionIsChanged(self, session):
        self.fail("Test not implemented.")


class TestSessionUpdateView(SessionUpdateTestCase):

    viewClass = ScanBookerRegistryUpdateView

    def initPost(self):
        self.POST['organisation'] = 1

    def failIfSessionIsChanged(self, session):
        self.assertEqual(session.starts, self.starts)
        self.assertEqual(session.ends, self.ends)
        self.assertEqual(session.organisation, None)

    def failUnlessSessionIsChanged(self, session):
        self.assertEqual(session.starts, self.starts)
        self.assertEqual(session.ends, self.ends)
        #self.assertEqual(session.organisation, self.organisation)
        self.assertEqual(session.organisation, None)
        # Todo: Resolve whether or not organisations are recorded here.

    def test_view_internals(self):
        p = self.view.getViewPosition()
        self.failUnlessEqual(p, 'scanningSessions/update')
        c = self.view.manipulators['scanningSessions/update']
        self.failUnlessEqual(c.__name__, 'ScanningSessionUpdateManipulator') 
        m = self.view.getManipulator()
        mClassName = m.__class__.__name__
        self.failUnlessEqual(mClassName, 'ScanningSessionUpdateManipulator')


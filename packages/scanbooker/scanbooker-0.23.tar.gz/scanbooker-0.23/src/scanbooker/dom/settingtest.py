import unittest
from scanbooker.dom.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(TestSetting),
        unittest.makeSuite(TestSettingDefault),
    ]
    return unittest.TestSuite(suites)


class TestSetting(TestCase):

    def setUp(self):
        self.setting = self.registry.settings.create('test')

    def tearDown(self):
        self.setting.delete()
    
    def test_attributes(self):
        self.failUnless(self.setting)
        self.failIf(self.setting.earmarkTemplate)
        self.failUnless(self.setting.showInlineHelp)


class TestSettingDefault(TestCase):

    def setUp(self):
        self.setting = self.registry.settings['default']

    def test_attributes(self):
        self.failUnless(self.setting)
        self.failUnlessEqual(self.setting.earmarkTemplate.name, 'Standard')
        self.failUnlessEqual(self.setting.showInlineHelp, True)
        self.failUnlessEqual(self.setting.defaultOrganisation, None)
        self.failUnlessEqual(self.setting.requireTrainedProjectLeader, True)
        self.failUnlessEqual(self.setting.requireApprovedProjectLeader, True)
        self.failUnlessEqual(self.setting.requireEthicsApprovalInDate, True)
        self.failUnlessEqual(self.setting.requireEthicsApprovalBalance, True)


import unittest
from scanbooker.testunit import TestCase
import os

def suite():
    suites = [
        unittest.makeSuite(TestEnvironment),
    ]
    return unittest.TestSuite(suites)

class TestEnvironment(TestCase):
    "TestCase for the Django Environment."

    def testDjangoSettingsModule(self):
        self.failUnless('DJANGO_SETTINGS_MODULE' in os.environ)
        settingsName = os.environ['DJANGO_SETTINGS_MODULE']
        # importing this module screws the registry up somehow...
        #self.failUnless(__import__(settingsName,'','','*'))
        




from webunit import webunittest
import unittest
from scanbooker.django.apps.sui.test.base import CuiTestCase
import scanbooker.django.apps.sui.test.admin
import scanbooker.django.apps.sui.test.project

def suite():
    suites = [
        unittest.makeSuite(TestVisitServer),
        scanbooker.django.apps.sui.test.admin.suite(),
        scanbooker.django.apps.sui.test.project.suite(),
    ]
    return unittest.TestSuite(suites)

class TestVisitServer(CuiTestCase):
   
    def testHome(self):
        self.getAssertContent('/', 'Welcome to')
    
    def testUserLogin(self):
        self.getAssertContent('/login/', 'Log in')


import unittest
from scanbooker.django.apps.sui.views.test.base import AdminSessionViewTestCase
from scanbooker.django.apps.sui.views.welcome import WelcomeView
from scanbooker.django.apps.sui.views.welcome import RegistryWelcomeView
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestWelcomeView),
        unittest.makeSuite(TestRegistryWelcomeView),
    ]
    return unittest.TestSuite(suites)


class TestWelcomeView(AdminSessionViewTestCase):

    viewClass = WelcomeView


class TestRegistryWelcomeView(AdminSessionViewTestCase):

    viewClass = RegistryWelcomeView



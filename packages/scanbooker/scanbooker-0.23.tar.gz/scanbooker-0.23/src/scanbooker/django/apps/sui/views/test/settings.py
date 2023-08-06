import unittest
from scanbooker.django.apps.sui.views.test.base import AdminSessionViewTestCase
from scanbooker.django.apps.sui.views.settings import SettingsUpdateView

def suite():
    suites = [
        unittest.makeSuite(TestSettings),
    ]
    return unittest.TestSuite(suites)


class TestSettings(AdminSessionViewTestCase):

    viewClass = SettingsUpdateView


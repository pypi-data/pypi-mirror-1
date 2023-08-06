import unittest
from dm.view.basetest import ViewTestCase
from dm.view.basetest import AdminSessionViewTestCase
from scanbooker.django.apps.sui.views.base import *
from dm.ioc import *

def suite():
    suites = [
    ]
    return unittest.TestSuite(suites)


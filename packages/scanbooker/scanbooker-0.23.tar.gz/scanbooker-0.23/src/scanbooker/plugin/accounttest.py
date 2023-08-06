import unittest
from scanbooker.testunit import TestCase
from scanbooker.plugin.account import Plugin

def suite():
    suites = [
        unittest.makeSuite(TestAccountPlugin),
    ]
    return unittest.TestSuite(suites)


# Todo: More tests.

class TestAccountPlugin(TestCase):

    def setUp(self):
        self.account = self.registry.accounts.create(code='h5h4h3')

    def test_events(self):
        self.account.events.create('AccountedSession.99')


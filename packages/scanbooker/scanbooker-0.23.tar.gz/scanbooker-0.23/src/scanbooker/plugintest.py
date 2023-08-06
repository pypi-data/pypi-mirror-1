import unittest
from scanbooker.testunit import TestCase
import scanbooker.plugin.accounttest

def suite():
    suites = [
        scanbooker.plugin.accounttest.suite(),
    ]
    return unittest.TestSuite(suites)


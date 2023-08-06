import unittest
from scanbooker.testunit import TestCase
import scanbooker.command.initialisetest
from scanbooker.exceptions import *

def suite():
    "Return a TestSuite of scanbooker.command TestCases."
    suites = [
        scanbooker.command.initialisetest.suite(),
    ]
    return unittest.TestSuite(suites)


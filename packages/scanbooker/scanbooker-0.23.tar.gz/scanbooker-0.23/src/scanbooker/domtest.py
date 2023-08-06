import unittest
from scanbooker.exceptions import *

from scanbooker.dom.testunit import TestCase

import scanbooker.dom.volunteertest
import scanbooker.dom.persontest
import scanbooker.dom.researchertest
import scanbooker.dom.scheduletest
import scanbooker.dom.reporttest
import scanbooker.dom.weektest
import scanbooker.dom.projecttest
import scanbooker.dom.settingtest
import scanbooker.dom.organisationtest
import scanbooker.dom.accounttest
import scanbooker.dom.settingtest

def suite():
    suites = [
        scanbooker.dom.volunteertest.suite(),
        scanbooker.dom.persontest.suite(),
        scanbooker.dom.researchertest.suite(),
        scanbooker.dom.scheduletest.suite(),
        scanbooker.dom.reporttest.suite(),
        scanbooker.dom.weektest.suite(),
        scanbooker.dom.projecttest.suite(),
        scanbooker.dom.settingtest.suite(),
        scanbooker.dom.organisationtest.suite(),
        scanbooker.dom.accounttest.suite(),
        scanbooker.dom.settingtest.suite(),
    ]
    return unittest.TestSuite(suites)


import unittest
import scanbooker.testunit
import scanbooker.unittesttest
import scanbooker.applicationtest
import scanbooker.djangotest
import scanbooker.commandtest
import scanbooker.domtest
import scanbooker.accesscontroltest
import scanbooker.migratetest
import scanbooker.django.apps.sui.views.test

def suite():
    suites = [
        scanbooker.unittesttest.suite(),
        scanbooker.applicationtest.suite(),
        scanbooker.djangotest.suite(),
        scanbooker.commandtest.suite(),
        scanbooker.domtest.suite(),
        scanbooker.accesscontroltest.suite(),
        scanbooker.migratetest.suite(),
        scanbooker.django.apps.sui.views.test.suite(),
    ]
    return unittest.TestSuite(suites)


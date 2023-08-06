from scanbooker.django.apps.sui.test.base import KuiTestCase
import scanbooker.django.apps.sui.test.admin.domainObject
import scanbooker.django.apps.sui.test.admin.hasMany
import unittest

def suite():
    suites = [
        scanbooker.django.apps.sui.test.admin.domainObject.suite(),
        scanbooker.django.apps.sui.test.admin.hasMany.suite(),
    ]
    return unittest.TestSuite(suites)


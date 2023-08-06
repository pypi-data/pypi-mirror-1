import scanbooker.django.apps.sui.views.test.welcome
import scanbooker.django.apps.sui.views.test.settings
import scanbooker.django.apps.sui.views.test.registry
import scanbooker.django.apps.sui.views.test.volunteer
import scanbooker.django.apps.sui.views.test.schedule
import scanbooker.django.apps.sui.views.test.rpc2
import scanbooker.django.apps.sui.views.test.manipulator
import unittest

def suite():
    suites = [
        scanbooker.django.apps.sui.views.test.welcome.suite(),
        scanbooker.django.apps.sui.views.test.settings.suite(),
        scanbooker.django.apps.sui.views.test.registry.suite(),
        scanbooker.django.apps.sui.views.test.volunteer.suite(),
        scanbooker.django.apps.sui.views.test.schedule.suite(),
        scanbooker.django.apps.sui.views.test.rpc2.suite(),
        scanbooker.django.apps.sui.views.test.manipulator.suite(),
    ]
    return unittest.TestSuite(suites)


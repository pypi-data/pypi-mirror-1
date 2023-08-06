import unittest
from scanbooker.exceptions import *
from scanbooker.dom.testunit import TestCase
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestWeek),
    ]
    return unittest.TestSuite(suites)

class TestWeek(TestCase):

    starts = mx.DateTime.DateTime(2007, 4, 2, 0, 0, 0)

    def setUp(self):
        self.week = self.registry.weeks.create(
            starts=self.starts,
        )

    def tearDown(self):
        self.week.delete()
    
    def test_attributes(self):
        self.failUnlessEqual(self.week.starts.year, 2007)
        self.failUnlessEqual(self.week.starts.month, 4)
        self.failUnlessEqual(self.week.starts.day, 2)
        self.failUnlessEqual(self.week.isPublished, False)

    def test_isPublished(self):
        self.failUnlessEqual(self.week.isPublished, False)
        self.week.isPublished = True
        self.week.save()
        week = self.registry.weeks[self.starts]
        self.failUnlessEqual(self.week.isPublished, True)


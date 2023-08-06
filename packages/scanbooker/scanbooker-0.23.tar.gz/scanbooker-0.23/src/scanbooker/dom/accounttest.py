import unittest
from scanbooker.exceptions import *
from scanbooker.dom.testunit import TestCase
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestAccountEvent),
        unittest.makeSuite(TestAccountEntry),
        unittest.makeSuite(TestAccount),
    ]
    return unittest.TestSuite(suites)


class TestAccountEvent(TestCase):

    qqrCode = 'aaa-bbb-ccc-ddd'
    amount = 1
    whenOccurred = mx.DateTime.Date(2008, 5, 5)
    whenNotified = mx.DateTime.Date(2008, 5, 5)

    def setUp(self):
        self.account = self.registry.accounts.create(
            qqrCode=self.qqrCode
        )
        self.event = self.registry.accountEvents.create(
            amount=self.amount,
            whenOccurred=self.whenOccurred,
            whenNotified=self.whenNotified,
            account=self.account,
        )
        
    def tearDown(self):
        self.event.delete()
        self.account.delete()
    
    def test(self):
        self.failUnlessEqual(self.event.account, self.account)
        self.failUnlessEqual(self.event.amount, self.amount)
        self.failUnlessEqual(self.event.whenOccurred, self.whenOccurred)
        self.failUnlessEqual(self.event.whenNotified, self.whenNotified)


class TestAccountEntry(TestCase):

    qqrCode = 'aaa-bbb-ccc-ddd'
    amount = 1
    whenOccurred = mx.DateTime.Date(2008, 5, 5)
    whenNotified = mx.DateTime.Date(2008, 5, 5)
    bookingDate = mx.DateTime.Date(2008, 5, 5)

    def setUp(self):
        self.account = self.registry.accounts.create(
            qqrCode=self.qqrCode
        )
        self.event = self.registry.accountEvents.create(
            amount=self.amount,
            whenOccurred=self.whenOccurred,
            whenNotified=self.whenNotified,
            account=self.account,
        )
        self.entry = self.registry.accountEntries.create(
            amount=self.amount,
            bookingDate=self.bookingDate,
            account=self.account,
            event=self.event,
        )
        
    def tearDown(self):
        self.entry.delete()
        self.account.delete()
    
    def test(self):
        self.failUnlessEqual(self.entry.account, self.account)
        self.failUnlessEqual(self.entry.amount, self.amount)
        self.failUnlessEqual(self.entry.bookingDate, self.bookingDate)


class TestAccount(TestCase):

    qqrCode = 'eee-fff-ggg-hhh'
    whenOccurred = mx.DateTime.Date(2008, 5, 5)
    whenNotified = mx.DateTime.Date(2008, 5, 5)
    amount = 90
    researcherId = 1

    def setUp(self):
        self.account = self.registry.accounts.create(
            qqrCode=self.qqrCode
        )
        self.account.researchers.create(
            self.registry.researchers[self.researcherId]
        )
        self.event = self.registry.accountEvents.create(
            amount=self.amount,
            whenOccurred=self.whenOccurred,
            whenNotified=self.whenNotified,
            account=self.account,
        )

    def tearDown(self):
        self.account.delete()
        self.event.delete()
    
    def test(self):
        self.failUnlessEqual(self.account.qqrCode, self.qqrCode)
        self.failUnlessEqual(self.account.getLabelValue(), self.qqrCode)
        self.account.getRate(self.whenOccurred)
        self.account.getPostingRule(self.whenOccurred)
        self.failUnless(self.registry.researchers[self.researcherId] \
            in self.account.researchers)
        self.failUnless(self.event in [i for i in self.account.events])
        self.failIf(self.account.entries)
        self.event.process()
        self.failUnless(self.account.entries)
        entry = self.account.entries.findLastDomainObject()
        self.failUnlessEqual(entry.amount, self.amount)


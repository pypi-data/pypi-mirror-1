"""
Account domain model.
"""
from dm.dom.stateful import *
from dm.ioc import RequiredFeature
import mx.DateTime
import dm.times

class Account(DatedStatefulObject):

    isUnique = False

    code = String(isRequired=True)
    comment = String()
    qqrCode = String()  # For Lucille.
    wbsCode = String()  # For Lucille.
    projects = HasMany('Project', 'id')
    researchers = AggregatesMany('ResearcherAccount', 'researcher')
    organisations = AggregatesMany('OrganisationAccount', 'organisation')
    notes = Text(isRequired=False)
    entries = AggregatesMany('AccountEntry', 'id')
    events = AggregatesMany('AccountEvent', 'id')
    rate = Integer(default=1, isTemporal=True)
    startsWithAttributeName = 'code'
    searchAttributeNames = ['code', 'qqrCode', 'wbsCode', 'comment', 'notes']

    entriesUnadjusted = None

    def getLabelValue(self):
        return self.code or self.qqrCode or self.wbsCode

    def getRate(self, effectiveDate):
        # Todo: Fix create kwds to accept temporal values.
        # Todo: Reinstantiate 'rate isTemporal' attribute property.
        # Todo: Make rate temporal-editable.
        return self.rate

    def getPostingRule(self, effectiveDate):
        return PostingRule()

    def getEntriesUnadjusted(self):
        if self.entriesUnadjusted == None:
            self.entriesUnadjusted = self.entries.clone()
            self.entriesUnadjusted.filter = {
                'account': self, 
                'isReversal': False,
                'isReversed': False,
            }
        return self.entriesUnadjusted

    def calculateBalance(self):
        balance = 0
        for entry in self.getEntriesUnadjusted():
            balance += entry.amount
        return balance


class AccountEvent(DatedStatefulObject):

    isUnique = False

    subjectName = String()     # Link to event subject.
    amount = Integer(default=0)
    whenOccurred = DateTime()
    whenNotified = DateTime()
    account = HasA('Account')
    entries = AggregatesMany('AccountEntry', 'id', 'event')
    #type = HasA('AccountEventType')
    hasBeenAdjusted = Boolean(default=False)
    adjusted = HasA('AccountEvent', isRequired=False)
    replacement = HasA('AccountEvent', isRequired=False)
    comment = String()

    sortOnName = 'whenNotified'

    isProcessed = False

    def process(self):
        if self.isProcessed:
            raise Exception, "Cannot process event twice (%s)." % str(self)
        if self.adjusted != None:
            self.adjusted.reverse(self)
        rule = self.getPostingRule()
        rule.process(self)
        self.isProcessed = True
        self.save()

    def reverse(self, replacement=None):
        self.replacement = replacement
        self.hasBeenAdjusted = True
        self.save()
        for entry in self.entries.findDomainObjects():
            if entry.isReversed or entry.isReversal:
                continue
            if self.replacement:
                bookingDate = self.replacement.whenNotified
            else:
                bookingDate = dm.times.getLocalNow()
            self.entries.create(
                bookingDate=bookingDate,
                amount=-entry.amount,
                account=entry.account,
                isReversal=True,
                comment=entry.comment
            )
            entry.isReversed = True
            entry.save()

    def getPostingRule(self):
        return self.account.getPostingRule(self.whenOccurred)

    def getUsage(self):
        return self.amount

    def getRate(self):
        return self.account.getRate(self.whenOccurred)


class IsReversed(Boolean):

    def createLabelRepr(self, domainObject):
        attrValue = getattr(domainObject, self.name)
        if attrValue:
            return 'C'
        else:
            return ''


class IsReversal(Boolean):

    def createLabelRepr(self, domainObject):
        attrValue = getattr(domainObject, self.name)
        if attrValue:
            return 'R'
        else:
            return ''


class AccountEntry(DatedStatefulObject):

    isUnique = False

    amount = Integer(default=0)
    bookingDate = DateTime()
    account = HasA('Account')
    event = HasA('AccountEvent')
    isReversed = IsReversed(default=False)
    isReversal = IsReversal(default=False)
    comment = String()

    sortOnName = 'bookingDate'

    
class PostingRule(object):

    registry = RequiredFeature('DomainRegistry')

    def process(self, event):
        self.registry.accountEntries.create(
            bookingDate = event.whenNotified,
            amount = event.getUsage() * event.getRate(),
            account = event.account,
            event=event,
            comment=event.comment,
        )


class ResearcherAccount(DatedStatefulObject):

    researcher = HasA('Researcher')
    account = HasA('Account')


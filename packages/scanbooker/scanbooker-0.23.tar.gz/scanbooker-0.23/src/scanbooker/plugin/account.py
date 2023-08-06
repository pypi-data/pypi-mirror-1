"""
Plugin for cost accounting.

Generates cost accounting events from scanning session changes.

"""
import dm.plugin.base
from dm.strategy import MakeProtectedName
import dm.times
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS 

# Todo: Fix for case where session drops the project.
# Todo: Fix for case where session is deleted.

class Plugin(dm.plugin.base.PluginBase):
    "Acccount plugin."

    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        name = 'account'

    def onScanningSessionCreate(self, scanningSession):
        self.handleScanningSession(scanningSession)

    def onScanningSessionDelete(self, scanningSession):
        self.reverseLastAccountEvent(scanningSession)
    
    def onScanningSessionUpdate(self, scanningSession):
        self.handleScanningSession(scanningSession)

    def onProjectUpdate(self, project):
        for scanningSession in project.scanningSessions:
            self.handleScanningSession(scanningSession)

    def handleScanningSession(self, scanningSession):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        if not self.hasAccount(scanningSession):
            self.reverseLastAccountEvent(scanningSession)
        elif self.hasAccountingDifference(scanningSession):
            self.makeNewAccountEvent(scanningSession)

    def hasAccount(self, scanningSession):
        p = scanningSession.project
        return p and p.account
   
    def hasAccountingDifference(self, scanningSession):
        comment = self.makeComment(scanningSession)
        amount = self.makeAmount(scanningSession)
        account = scanningSession.project.account
        lastEvent = self.findLastAccountEvent(scanningSession)
        if lastEvent and (lastEvent.comment == comment) and (lastEvent.amount == amount) and (lastEvent.account == account):
            return False
        return True

    def reverseLastAccountEvent(self, scanningSession):
        lastEvent = self.findLastAccountEvent(scanningSession)
        if lastEvent:
            lastEvent.reverse()

    def makeNewAccountEvent(self, scanningSession):
        account = scanningSession.project.account
        subjectName = self.makeSubjectName(scanningSession)
        amount = self.makeAmount(scanningSession)
        whenOccurred = scanningSession.starts
        whenNotified = dm.times.getLocalNow()
        lastEvent = self.findLastAccountEvent(scanningSession)
        comment = self.makeComment(scanningSession)
        nextEvent = self.registry.accountEvents.create(
            account=account,
            subjectName=subjectName,
            amount=amount,
            whenOccurred=whenOccurred,
            whenNotified=whenNotified,
            hasBeenAdjusted=False,
            adjusted=lastEvent,
            comment=comment,
        )
        nextEvent.process()

    def findLastAccountEvent(self, scanningSession):
        subjectName = self.makeSubjectName(scanningSession)
        lastEvent = self.registry.accountEvents.findSingleDomainObject(
            subjectName=subjectName,
            hasBeenAdjusted=False
        )
        return lastEvent

    def makeSubjectName(self, scanningSession):
        return MakeProtectedName(scanningSession).make()

    def makeAmount(self, scanningSession):
        return scanningSession.getMinutes()

    def makeComment(self, scanningSession):
        comment = ''
        comment += ' %s' % scanningSession.asDictLabels()['starts']
        if scanningSession.outcome:
            comment += ' (%s)' % scanningSession.outcome.getLabelValue()
        if scanningSession.scanId:
            comment += ' scan %s' % scanningSession.scanId
        return comment



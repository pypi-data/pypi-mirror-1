from dm.dom.stateful import *

# todo: rename as EthicalApproval
class Approval(DatedStatefulObject):

    code = String()
    description = String(isRequired=False)
    projects = AggregatesMany('ProjectApproval', 'project')
    principalInvestigators = AggregatesMany('ApprovalPrincipal', 'researcher')
    additionalResearchers = AggregatesMany('ApprovalMembership', 'researcher')
    numberAllocated = Integer(default=0, isRequired=False)
    numberUsedAdjustment = Integer(default=0, isRequired=False)
    scanningSessions = AggregatesMany('ScanningSession', 'id')
    notes = Text(isRequired=False)
    expires = RDate(isRequired=False)

    startsWithAttributeName = 'code'
    searchAttributeNames = ['code', 'description', 'notes']

    sortOnName = 'code'

    def getLabelValue(self):
        label = ''
       #firstPrincipalship = self.principalInvestigators.findFirstDomainObject()
       #if firstPrincipalship:
        #    label += firstPrincipalship.researcher.realname
        #    label += " "
        label += self.code
        return label

    def numberRemaining(self):
        return self.numberAllocated - self.numberUsed()
        
    def numberUsed(self):
        count = self.numberUsedAdjustment
        for scanningSession in self.scanningSessions:
            if scanningSession.ethicsUsed:
                count += 1
        return count


class ApprovalMembership(DatedStatefulObject):
    
    approval = HasA('Approval')
    researcher = HasA('Researcher')
    
    def getLabelValue(self):
        return "%s-%s" % (
            self.approval.code,
            self.researcher.realname
        )


class ApprovalPrincipal(ApprovalMembership):

    sortOnName = 'dateCreated'


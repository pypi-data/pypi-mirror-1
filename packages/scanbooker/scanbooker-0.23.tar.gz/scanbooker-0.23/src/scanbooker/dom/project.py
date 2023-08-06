from dm.dom.stateful import *
import mx.DateTime

class ProjectStatus(StandardObject):

    isConstant = True 


class ProjectOutcome(StandardObject):

    isConstant = True


class Project(DatedStatefulObject):

    title = String(default='')
    nickname = String(default='', isRequired=False)
    leader = HasA('Researcher', isRequired=False)
    researchers = AggregatesMany('ProjectResearcher', 'researcher')
    approvals = AggregatesMany('ProjectApproval', 'approval')
    # Todo: Remove this in 0.19.
    # Todo: Also remove from scanbooker.cli.admin::touchMigratedDomainModel().
    approval = HasA('Approval', isRequired=False)
    funding = HasA('FundingStatus', isRequired=False, isSimpleOption=True)
    status = HasA('ProjectStatus', default='Active', isRequired=False,
        isSimpleOption=True)  
    preparationMinutes = Integer(default=30)
    scanningSessions = AggregatesMany('ScanningSession', 'id')
    volunteerBookingMethod = HasA('VolunteerBookingMethod',
        default='BrainScan', isRequired=False, isSimpleOption=True)
    IIGPresentation = RDate(isRequired=False, default=None)
    IMCApproval = RDate(isRequired=False, default=None)
    numberSubjects = Integer(isRequired=False)
    numberPilots = Integer(isRequired=False)
    slotMinutes = Integer(default=90)
    volunteerType = HasA('VolunteerType', default='Volunteer',
        isSimpleOption=True, isRequired=False)
    startDate = RDate(isRequired=False, default=None)
    completionDate = RDate(isRequired=False, default=None)
    notes = Text(default='', isRequired=False)
    costCode = Text(default='', isRequired=False)
    account = HasA('Account', isRequired=False)
    outcome = HasA('ProjectOutcome', isRequired=False, isSimpleOption=True)
     
    searchAttributeNames = ['title', 'notes']
    startsWithAttributeName = 'title'

    def getLabelValue(self):
        if self.nickname.strip() != '':
            return self.nickname.strip()
        elif self.title.strip():
            return self.title.strip()
        else:
            return "#%s" % self.id

    def listGroups(self):
        groups = {}
        if self.leader:
            for group in self.leader.principalships.keys():
                groups[group] = 1
            for group in self.leader.memberships.keys():
                groups[group] = 1
        for researcher in self.researchers.keys():
            for group in researcher.principalships.keys():
                groups[group] = 1
            for group in researcher.memberships.keys():
                groups[group] = 1
        return groups.keys()

    def lastScan(self):
        return self.scanningSessions.findLastDomainObject()

    def isInactive(self):
        return not self.status or self.status.name != 'Active'


class ProjectResearcher(DatedStatefulObject):

    project = HasA('Project')
    researcher = HasA('Researcher')

    def getLabelValue(self):
        return "%s-%s" % (
            self.project.getLabelValue(),
            self.researcher.getLabelValue()
        )


class ProjectApproval(DatedStatefulObject):

    project = HasA('Project')
    approval = HasA('Approval')

    def getLabelValue(self):
        return "%s-%s" % (
            self.project.getLabelValue(),
            self.approval.getLabelValue()
        )


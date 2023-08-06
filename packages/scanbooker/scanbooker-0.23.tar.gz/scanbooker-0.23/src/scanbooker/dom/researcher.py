from dm.dom.stateful import *
from scanbooker.dom.base import PersonExtn
import re

class Researcher(PersonExtn):

    isUnique = False

    # Todo: initials must be unique
    initials = String(default='', isRequired=False)
    external = Boolean(default=False)
    principalships = AggregatesMany('GroupPrincipalship', 'group')
    memberships = AggregatesMany('GroupMembership', 'group')
    principalApprovals = AggregatesMany('ApprovalPrincipal', 'approval')
    additionalApprovals = AggregatesMany('ApprovalMembership', 'approval')
    trainingSessions = AggregatesMany('ResearcherTrainingAppointment', 'trainingSession')
    theory = Boolean(default=False)
    practical = Boolean(default=False)
    AED = Boolean(default=False, isRequired=False)
    telephoneInternal = String(isRequired=False, title='internal telephone')
    telephoneExternal = String(isRequired=False, title='external telephone')
    mriAccessStatus = HasA('AccessStatus', default='Unauthorised',
        isSimpleOption=True, title='MRI access status')
    leadingProjects = AggregatesMany('Project', 'id', 'leader')
    projects = AggregatesMany('ProjectResearcher', 'project')
    notes = Text(isRequired=False)
    #status = HasA('ResearcherStatus', default='Active Researcher', isRequired=False, isSimpleOption=True)
    status = HasA('ResearcherStatus', isRequired=False, isSimpleOption=True)

    def isTrained(self):
        return self.practical and self.theory

    def getSafetyTrainingCertificateId(self):
        register = self.registry.safetyTrainingCertificates
        mostRecentCertificate = register.findFirstDomainObject(researcher=self)
        return mostRecentCertificate.id

    def getPerson(self):
        register = self.registry.persons
        person = register.findFirstDomainObject(researcher=self)
        if not person:
            register = self.registry.persons.getPending()
            person = register.findFirstDomainObject(researcher=self)
        return person

    def onCreate(self):
        super(Researcher, self).onCreate()
        self.coerceInitials()

    def onUpdate(self):
        super(Researcher, self).onUpdate()
        self.coerceInitials()

    def coerceInitials(self):
        if self.initials.upper() != self.initials:
            self.initials = self.initials.upper()
            self.save()
        if self.initials == '' or self.hasCollidingInitials():
            candidateInitials = self.increaseInitials(self.initials)
            while(self.findResearchersWithInitials(candidateInitials)):
                candidateInitials = self.increaseInitials(candidateInitials)
            self.initials = candidateInitials
            self.save()

    def hasCollidingInitials(self):
        match = self.findResearchersWithInitials(self.initials)
        return (len(match) > 1) and (self in match)

    def findResearchersWithInitials(self, initials):
        return self.registry.researchers.findDomainObjects(initials=initials)

    def makeRawInitials(self):
        if not self.realname:
            return 'ANO'
        return "".join([name[0].upper() for name in self.realname.split(' ')])

    def increaseInitials(self, oldInitials):
        rawInitials = self.makeRawInitials()
        if not oldInitials:
            newInitials = rawInitials
            return newInitials
        parts = re.split('(\d*$)', oldInitials)
        initialsStart = parts[0]
        if len(parts) > 1:
            initialsPostfix = parts[1]
            postfixInteger = int(initialsPostfix)
            postfixInteger += 1
            initialsPostfix = str(postfixInteger)
        else:
            initialsPostfix = "1"
        newInitials = initialsStart + initialsPostfix
        return newInitials


class ResearcherStatus(StandardObject):

    isConstant = True


class AccessStatus(StandardObject):

    isConstant = True



class ResearcherTrainingAppointment(DatedStatefulObject):

    researcher    = HasA('Researcher')
    trainingSession = HasA('TrainingSession')

    def getSortOnValue(self):
        return self.trainingSession.starts


class ResearcherTheorySuccess(DatedStatefulObject):

    researcher    = HasA('Researcher')
    theorySession = HasA('TheorySession')


class ResearcherPracticalSuccess(DatedStatefulObject):

    researcher       = HasA('Researcher')
    practicalSession = HasA('PracticalSession')


class ResearcherScanningAppointment(DatedStatefulObject):

    researcher      = HasA('Researcher')
    scanningSession = HasA('ScanningSession')


class SafetyTrainingCertificate(DatedStatefulObject):

    isUnique = False

    researcher = HasA('Researcher')
    content = Pickle(default=None, isRequired=False)
    contentType = String(default='', isRequired=False)
    file = ImageFile(maxWidth=620)

    sortOnName = 'dateCreated'
    sortAscending = False

    def getPerson(self):
        return self.researcher.getPerson()


import dm.dom.builder

class ModelBuilder(dm.dom.builder.ModelBuilder):

    def construct(self):
        super(ModelBuilder, self).construct()
        self.loadFundingStatus()
        self.loadOrganisation()
        self.loadGroup()
        self.loadScanner()
        self.loadRadiographer()
        self.loadResearcher()
        self.loadVolunteer()
        self.loadApproval()
        self.loadProject()
        self.loadWeek()
        self.loadSchedule()
        self.loadReport()
        self.loadSetting()
        self.loadAccount()
        #self.loadBackgroundObjects()

    def loadPerson(self):
        from scanbooker.dom.person import Person
        self.registry.registerDomainClass(Person)
        self.registry.persons = Person.createRegister()

    def loadFundingStatus(self):
        from scanbooker.dom.funding import FundingStatus
        self.registry.registerDomainClass(FundingStatus)
        self.registry.fundingStatuses = FundingStatus.createRegister()

    def loadOrganisation(self):
        from scanbooker.dom.organisation import Organisation
        from scanbooker.dom.organisation import OrganisationGroup
        from scanbooker.dom.organisation import OrganisationAccount
        self.registry.registerDomainClass(Organisation)
        self.registry.registerDomainClass(OrganisationGroup)
        self.registry.registerDomainClass(OrganisationAccount)
        self.registry.organisations = Organisation.createRegister()

    def loadGroup(self):
        from scanbooker.dom.group import Group
        self.registry.registerDomainClass(Group)
        self.registry.groups = Group.createRegister()
        from scanbooker.dom.group import GroupMembership
        self.registry.registerDomainClass(GroupMembership)
        from scanbooker.dom.group import GroupPrincipalship
        self.registry.registerDomainClass(GroupPrincipalship)

    def loadSession(self):
        from scanbooker.dom.session import Session
        self.registry.registerDomainClass(Session)
        self.registry.sessions = Session.createRegister()

    def loadScanner(self):
        from scanbooker.dom.scanner import Scanner
        self.registry.registerDomainClass(Scanner)
        self.registry.scanners = Scanner.createRegister()
    
    def loadResearcher(self):
        from scanbooker.dom.researcher import Researcher
        from scanbooker.dom.researcher import ResearcherStatus
        from scanbooker.dom.researcher import AccessStatus
        from scanbooker.dom.researcher import ResearcherTrainingAppointment
        from scanbooker.dom.researcher import ResearcherTheorySuccess
        from scanbooker.dom.researcher import ResearcherPracticalSuccess
        from scanbooker.dom.researcher import ResearcherScanningAppointment
        from scanbooker.dom.researcher import SafetyTrainingCertificate
        self.registry.registerDomainClass(Researcher)
        self.registry.registerDomainClass(ResearcherStatus)
        self.registry.registerDomainClass(AccessStatus)
        self.registry.registerDomainClass(ResearcherTrainingAppointment)
        self.registry.registerDomainClass(ResearcherTheorySuccess)
        self.registry.registerDomainClass(ResearcherPracticalSuccess)
        self.registry.registerDomainClass(ResearcherScanningAppointment)
        self.registry.registerDomainClass(SafetyTrainingCertificate)
        self.registry.researchers = Researcher.createRegister()
        self.registry.accessStatuses = AccessStatus.createRegister()
        self.registry.researcherStatuses = ResearcherStatus.createRegister()
        self.registry.safetyTrainingCertificates = SafetyTrainingCertificate.createRegister()

    def loadVolunteer(self):
        from scanbooker.dom.volunteer import Handedness
        from scanbooker.dom.volunteer import Volunteer
        from scanbooker.dom.volunteer import VolunteerRecruitmentMethod
        from scanbooker.dom.volunteer import VolunteerStatus
        from scanbooker.dom.volunteer import VolunteerType
        from scanbooker.dom.volunteer import VolunteerScanningAppointment
        from scanbooker.dom.volunteer import VolunteerScreening
        from scanbooker.dom.volunteer import StructuralScan
        from scanbooker.dom.volunteer import FunctionalScan
        self.registry.registerDomainClass(Handedness)
        self.registry.registerDomainClass(Volunteer)
        self.registry.registerDomainClass(VolunteerRecruitmentMethod)
        self.registry.registerDomainClass(VolunteerStatus)
        self.registry.registerDomainClass(VolunteerType)
        self.registry.registerDomainClass(VolunteerScanningAppointment)
        self.registry.registerDomainClass(VolunteerScreening)
        self.registry.registerDomainClass(StructuralScan)
        self.registry.registerDomainClass(FunctionalScan)
        self.registry.handednesses = Handedness.createRegister()
        self.registry.volunteers = Volunteer.createRegister()
        self.registry.volunteerRecruitmentMethods = VolunteerRecruitmentMethod.createRegister()
        self.registry.volunteerTypes = VolunteerType.createRegister()
        self.registry.volunteerStatuses = VolunteerStatus.createRegister()

    def loadRadiographer(self):
        from scanbooker.dom.radiographer import Radiographer
        from scanbooker.dom.radiographer import RadiographerTheoryAppointment
        from scanbooker.dom.radiographer import RadiographerPracticalAppointment
        from scanbooker.dom.radiographer import RadiographerScanningAppointment
        self.registry.registerDomainClass(Radiographer)
        self.registry.registerDomainClass(RadiographerTheoryAppointment)
        self.registry.registerDomainClass(RadiographerPracticalAppointment)
        self.registry.registerDomainClass(RadiographerScanningAppointment)
        self.registry.radiographers = Radiographer.createRegister()

    def loadWeek(self):
        from scanbooker.dom.week import Week
        self.registry.registerDomainClass(Week)
        self.registry.weeks = Week.createRegister()

    def loadSchedule(self):
        #from scanbooker.dom.schedule import FacilitySchedule 
        from scanbooker.dom.schedule import WeekEarmarkTemplate # old
        from scanbooker.dom.schedule import EarmarkTemplate     # old
        from scanbooker.dom.schedule import EarmarkedTimeTemplate
        from scanbooker.dom.schedule import EarmarkedTimeTemplateWeek
        from scanbooker.dom.schedule import SessionType
        from scanbooker.dom.schedule import EarmarkedTime
        from scanbooker.dom.schedule import MaintenanceSession
        from scanbooker.dom.schedule import MethodsSession
        from scanbooker.dom.schedule import DowntimeSession
        from scanbooker.dom.schedule import TrainingSession
        from scanbooker.dom.schedule import TrainingSessionType
        from scanbooker.dom.schedule import ScanningSession
        from scanbooker.dom.schedule import ScanningSessionType
        from scanbooker.dom.schedule import ScanningSessionOutcome
        from scanbooker.dom.schedule import VolunteerBookingMethod
        #self.registry.registerDomainClass(FacilitySchedule) 
        #self.registry.facilitySchedules = FacilitySchedule.createRegister()
        self.registry.registerDomainClass(EarmarkedTimeTemplate)
        self.registry.registerDomainClass(EarmarkedTimeTemplateWeek)
        self.registry.registerDomainClass(WeekEarmarkTemplate)
        self.registry.registerDomainClass(EarmarkTemplate)
        self.registry.registerDomainClass(SessionType)
        self.registry.registerDomainClass(EarmarkedTime)
        self.registry.registerDomainClass(MaintenanceSession)
        self.registry.registerDomainClass(MethodsSession)
        self.registry.registerDomainClass(DowntimeSession)
        self.registry.registerDomainClass(TrainingSession)
        self.registry.registerDomainClass(TrainingSessionType)
        self.registry.registerDomainClass(ScanningSession)
        self.registry.registerDomainClass(ScanningSessionType)
        self.registry.registerDomainClass(ScanningSessionOutcome)
        self.registry.registerDomainClass(VolunteerBookingMethod)
        self.registry.weekEarmarkTemplates = WeekEarmarkTemplate.createRegister()
        self.registry.sessionTypes = SessionType.createRegister()
        self.registry.earmarkedTimeTemplateWeeks = EarmarkedTimeTemplateWeek.createRegister()
        self.registry.earmarkedTimeTemplates = EarmarkedTimeTemplate.createRegister()
        self.registry.earmarkedTimes = EarmarkedTime.createRegister()
        self.registry.maintenanceSessions = MaintenanceSession.createRegister()
        self.registry.methodsSessions = MethodsSession.createRegister()
        self.registry.downtimeSessions = DowntimeSession.createRegister()
        self.registry.trainingSessions = TrainingSession.createRegister()
        self.registry.trainingSessionTypes = TrainingSessionType.createRegister()
        self.registry.scanningSessions = ScanningSession.createRegister()
        self.registry.scanningSessionTypes = ScanningSessionType.createRegister()
        self.registry.scanningSessionOutcomes = ScanningSessionOutcome.createRegister()
        self.registry.volunteerBookingMethods = VolunteerBookingMethod.createRegister()

    def loadProject(self):
        from scanbooker.dom.project import ProjectStatus
        from scanbooker.dom.project import ProjectOutcome
        from scanbooker.dom.project import Project
        from scanbooker.dom.project import ProjectResearcher
        from scanbooker.dom.project import ProjectApproval
        self.registry.registerDomainClass(ProjectStatus)
        self.registry.registerDomainClass(ProjectOutcome)
        self.registry.registerDomainClass(Project)
        self.registry.registerDomainClass(ProjectResearcher)
        self.registry.registerDomainClass(ProjectApproval)
        self.registry.projectStatuses = ProjectStatus.createRegister()
        self.registry.projectOutcomes = ProjectOutcome.createRegister()
        self.registry.projects = Project.createRegister()

    def loadApproval(self):
        from scanbooker.dom.approval import ApprovalPrincipal
        self.registry.registerDomainClass(ApprovalPrincipal)
        from scanbooker.dom.approval import ApprovalMembership
        self.registry.registerDomainClass(ApprovalMembership)
        from scanbooker.dom.approval import Approval
        self.registry.registerDomainClass(Approval)
        self.registry.approvals = Approval.createRegister()

    def loadReport(self):
        from scanbooker.dom.report import Report
        from scanbooker.dom.report import ReportFilter
        from scanbooker.dom.report import ReportColumn
        self.registry.registerDomainClass(Report)
        self.registry.registerDomainClass(ReportFilter)
        self.registry.registerDomainClass(ReportColumn)
        self.registry.reports = Report.createRegister()
        self.registry.reportFilters = ReportFilter.createRegister()
        self.registry.reportColumns = ReportColumn.createRegister()

    def loadSetting(self):
        from scanbooker.dom.setting import Setting
        self.registry.registerDomainClass(Setting)
        self.registry.settings = Setting.createRegister()

    def loadAccount(self):
        from scanbooker.dom.account import AccountEvent
        from scanbooker.dom.account import AccountEntry
        #from scanbooker.dom.account import PostingRule
        from scanbooker.dom.account import Account
        from scanbooker.dom.account import ResearcherAccount
        self.registry.registerDomainClass(AccountEvent)
        self.registry.registerDomainClass(AccountEntry)
        #self.registry.registerDomainClass(PostingRule)
        self.registry.registerDomainClass(Account)
        self.registry.registerDomainClass(ResearcherAccount)
        self.registry.accountEvents = AccountEvent.createRegister()
        self.registry.accountEntries = AccountEntry.createRegister()
        self.registry.accounts = Account.createRegister()

    def loadBackgroundObjects(self):
        self.registry.loadBackgroundRegister(self.registry.fundingStatuses)
        self.registry.loadBackgroundRegister(self.registry.accessStatuses)
        self.registry.loadBackgroundRegister(self.registry.handednesses)
        self.registry.loadBackgroundRegister(self.registry.volunteerRecruitmentMethods)
        self.registry.loadBackgroundRegister(self.registry.volunteerBookingMethods)
        self.registry.loadBackgroundRegister(self.registry.volunteerStatuses)
        self.registry.loadBackgroundRegister(self.registry.projectStatuses)


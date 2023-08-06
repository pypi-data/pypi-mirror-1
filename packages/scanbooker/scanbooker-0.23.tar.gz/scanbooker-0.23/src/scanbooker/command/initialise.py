from dm.command import Command
from dm.command.state import *
from dm.command.accesscontrol import GrantStandardSystemAccess
from dm.command.person import *
from scanbooker.command.package import *
from scanbooker.dictionarywords import *
import mx.DateTime

# Todo: Integrate this with dm.command.inititalise more.
class InitialiseDomainModel(Command):
    """
    Creates default domain model objects.
    """
    
    def __init__(self):
        super(self.__class__, self).__init__()
 
    def execute(self):
        super(self.__class__, self).execute()
        self.createStates()
        self.createSystem()
        self.createRoles()
        self.createActions()
        self.createProtectionObjects()
        self.createAccessControlPlugin()
        self.createAccountPlugin()
        self.createPersons()
        self.createGrants()
        self.createRefusals()
        self.createAccessStatuses()
        self.createProjectStatuses()
        self.createProjectOutcomes()
        self.createFundingStatuses()
        self.createSessionTypes()
        self.createScanners()
        self.createScanningSessionTypes()
        self.createTrainingSessionTypes()
        self.createResearcherStatuses()
        self.createScanningSessionOutcomes()
        self.createVolunteerStatuses()
        self.createVolunteerTypes()
        self.createVolunteerBookingMethods()
        self.createVolunteerRecruitmentMethods()
        self.createHandednesses()
        if self.dictionary['system_mode'] == 'development':
            self.setUpTestFixtures()
        self.createApproveRegistrationPlugin()
        self.createMetaModelPlugin()
        self.createLinkPersonResearcherPlugin()
        self.createEarmarkedTimeTemplateWeeks()
        self.createSetting()
        self.commitSuccess()

    def createSystem(self):
        self.registry.systems.create(
            mode=self.dictionary[SYSTEM_MODE],
            version=self.dictionary[SYSTEM_VERSION],
        )

    def createStates(self):
        self.registry.states.create('pending')
        self.registry.states.create('active')
        self.registry.states.create('deleted')

    def createRoles(self):
        self.registry.roles.create('Administrator')
        self.registry.roles.create('PrincipalInvestigator')
        self.registry.roles.create('Researcher')
        self.registry.roles.create('Staff')
        self.registry.roles.create('Visitor')

    def createActions(self):
        self.registry.actions.create('Create')
        self.registry.actions.create('Approve')
        self.registry.actions.create('Read')
        self.registry.actions.create('Update')
        self.registry.actions.create('Delete')
        self.registry.actions.create('Purge')
        
    def createProtectionObjects(self):
        self.registry.protectionObjects.create('Session')
        self.registry.protectionObjects.create('System')
        self.registry.protectionObjects.create('AccessStatus')
        self.registry.protectionObjects.create('ProjectStatus')
        self.registry.protectionObjects.create('FundingStatus')
        self.registry.protectionObjects.create('Organisation')
        self.registry.protectionObjects.create('Group')
        self.registry.protectionObjects.create('Person')
        self.registry.protectionObjects.create('Scanner')
        self.registry.protectionObjects.create('Researcher')
        self.registry.protectionObjects.create('Radiographer')
        self.registry.protectionObjects.create('Volunteer')
        self.registry.protectionObjects.create('VolunteerType')
        self.registry.protectionObjects.create('VolunteerStatus')
        self.registry.protectionObjects.create('VolunteerBookingMethod')
        self.registry.protectionObjects.create('VolunteerScanningAppointment')
        self.registry.protectionObjects.create('Handedness')
        self.registry.protectionObjects.create('Approval')
        self.registry.protectionObjects.create('ApprovalMembership')
        self.registry.protectionObjects.create('Project')
        self.registry.protectionObjects.create('EarmarkedTime')
        self.registry.protectionObjects.create('MaintenanceSession')
        self.registry.protectionObjects.create('MethodsSession')
        self.registry.protectionObjects.create('ScanningSession')
        self.registry.protectionObjects.create('DowntimeSession')
        self.registry.protectionObjects.create('TrainingSession')
        self.registry.protectionObjects.create('WeekEarmarkTemplate')
        self.registry.protectionObjects.create('EarmarkedTimeTemplate')
        self.registry.protectionObjects.create('EarmarkedTimeTemplateWeek')
        self.registry.protectionObjects.create('Report')
        self.registry.protectionObjects.create('Setting')
        self.registry.protectionObjects.create('Account') 

    def createAccessControlPlugin(self):
        plugins = self.registry.plugins
        plugins.create('accesscontrol')

    def createLinkPersonResearcherPlugin(self):
        plugins = self.registry.plugins
        plugins.create('linkpersonresearcher')

    def createApproveRegistrationPlugin(self):
        plugins = self.registry.plugins
        plugins.create('registration')

    def createMetaModelPlugin(self):
        plugins = self.registry.plugins
        plugins.create('metamodel')

    def createAccountPlugin(self):
        plugins = self.registry.plugins
        plugins.create('account')

    def createPersons(self):
        adminRole = self.registry.roles['Administrator']
        self.createPerson('admin', adminRole, 'Administrator', 'pass')
        staffRole = self.registry.roles['Staff']
        self.createPerson('staff', staffRole, 'Staff (Anon)', 'pass')
        visitorName = self.dictionary['visitor']
        visitorRoleName = self.dictionary['visitor_role']
        visitorRole = self.registry.roles[visitorRoleName]
        self.createPerson(visitorName, visitorRole, 'Visitor', '')

    def createGrants(self):
        self.grantAdministratorAccess()
        self.grantPrincipalInvestigatorAccess()
        self.grantResearcherAccess()
        self.grantStaffAccess()
        self.grantVisitorAccess()

    def grantAdministratorAccess(self):
        role = self.registry.roles['Administrator']
        for protectionObject in self.registry.protectionObjects:
            disabledNames = ['TrainingSession', 'Settings']
            if protectionObject.name in disabledNames:
                continue
            for permission in protectionObject.permissions:
                if not permission in role.grants:
                    role.grants.create(permission)

    def grantPrincipalInvestigatorAccess(self):
        self.grantToRoleActionsOnNames(
            'PrincipalInvestigator',
            ['Read'],
            ['System', 'EarmarkedTime', 'MaintenanceSession', 
             'MethodsSession', 'DowntimeSession']
        )
        self.grantToRoleActionsOnNames(
            'PrincipalInvestigator',
            ['Create', 'Read', 'Update'],
            ['Researcher', 'Approval', 'Project', 'Group', 'Report']
        )
        self.grantToRoleActionsOnNames(
            'PrincipalInvestigator',
            ['Create', 'Read', 'Update', 'Delete'],
            ['ScanningSession', 'Person']
        )

    def grantResearcherAccess(self):
        self.grantToRoleActionsOnNames(
            'Researcher',
            ['Read'],
            ['System', 'EarmarkedTime', 'MaintenanceSession', 'MethodsSession',
             'DowntimeSession', 'Researcher', 'Approval', 'Group']
        )
        self.grantToRoleActionsOnNames(
            'Researcher',
            ['Create', 'Read'],
            ['ScanningSession', 'Project', 'Approval']
        )
        self.grantToRoleActionsOnNames(
            'Researcher',
            ['Create', 'Read'],
            []
        )

    def grantStaffAccess(self):
        self.grantToRoleActionsOnNames(
            'Staff',
            ['Read'],
            ['System', 'Group', 'Researcher', 'EarmarkedTime',
             'MaintenanceSession', 'DowntimeSession', 'ScanningSession']
        )
 
    def grantVisitorAccess(self):
        if not self.dictionary[INIT_STOP_VISITOR_REGISTRATION]:
            self.grantToRoleActionsOnNames(
                'Visitor',
                ['Create'],
                ['Person']
            )

    def grantToRoleActionsOnNames(self,roleName,actionNames,protectedNames):
        role = self.registry.roles[roleName]
        actions = []
        for actionName in actionNames:
            actions.append(self.registry.actions[actionName])
        for protectedName in protectedNames:
            protectionObject = self.registry.protectionObjects[protectedName]
            for action in actions:
                permission = protectionObject.permissions[action]
                if not permission in role.grants:
                    role.grants.create(permission)

    def createRefusals(self):
        pass

    def createFacilitySchedules(self):
        self.facilitySchedule = self.registry.facilitySchedules.create(
            'MRC - CBSU'
        )

    def createEarmarkedTimeTemplateWeeks(self):
        sessionTypes = self.registry.sessionTypes
        cleaning = sessionTypes['Cleaning']
        closed = sessionTypes['Closed']
        otherUse = sessionTypes['Other Use']
        reserved = sessionTypes['Reserved']
        scanning = sessionTypes['Scanning']
        standardWeek = self.registry.earmarkedTimeTemplateWeeks.create('Standard')
        earmarks = standardWeek.earmarkedTimeTemplates
        earmarks.create(sessionType=cleaning,
            startsDay=0, startsHour=8, startsMinute=0,
            endsDay=0, endsHour=9, endsMinute=15
        )
        earmarks.create(sessionType=scanning,
            startsDay=0, startsHour=9, startsMinute=15,
            endsDay=0, endsHour=12, endsMinute=30
        )
        earmarks.create(sessionType=closed,
            startsDay=0, startsHour=12, startsMinute=30,
            endsDay=0, endsHour=13, endsMinute=0
        )
        earmarks.create(sessionType=scanning,
            startsDay=0, startsHour=13, startsMinute=0,
            endsDay=0, endsHour=18, endsMinute=0
        )
        earmarks.create(sessionType=otherUse,
            startsDay=0, startsHour=18, startsMinute=0,
            endsDay=0, endsHour=20, endsMinute=0
        )
        
        earmarks.create(sessionType=cleaning,
            startsDay=1, startsHour=8, startsMinute=0,
            endsDay=1, endsHour=9, endsMinute=15
        )
        earmarks.create(sessionType=scanning,
            startsDay=1, startsHour=9, startsMinute=15,
            endsDay=1, endsHour=12, endsMinute=30
        )
        earmarks.create(sessionType=closed,
            startsDay=1, startsHour=12, startsMinute=30,
            endsDay=1, endsHour=13, endsMinute=0
        )
        earmarks.create(sessionType=scanning,
            startsDay=1, startsHour=13, startsMinute=0,
            endsDay=1, endsHour=18, endsMinute=0
        )
        earmarks.create(sessionType=otherUse,
            startsDay=1, startsHour=18, startsMinute=0,
            endsDay=1, endsHour=20, endsMinute=0
        )
        
        earmarks.create(sessionType=cleaning,
            startsDay=2, startsHour=8, startsMinute=0,
            endsDay=2, endsHour=9, endsMinute=15
        )
        earmarks.create(sessionType=scanning,
            startsDay=2, startsHour=9, startsMinute=15,
            endsDay=2, endsHour=12, endsMinute=30
        )
        earmarks.create(sessionType=closed,
            startsDay=2, startsHour=12, startsMinute=30,
            endsDay=2, endsHour=13, endsMinute=0
        )
        earmarks.create(sessionType=scanning,
            startsDay=2, startsHour=13, startsMinute=0,
            endsDay=2, endsHour=18, endsMinute=0
        )
        earmarks.create(sessionType=otherUse,
            startsDay=2, startsHour=18, startsMinute=0,
            endsDay=2, endsHour=20, endsMinute=0
        )
        
        earmarks.create(sessionType=cleaning,
            startsDay=3, startsHour=8, startsMinute=0,
            endsDay=3, endsHour=9, endsMinute=15
        )
        earmarks.create(sessionType=scanning,
            startsDay=3, startsHour=9, startsMinute=15,
            endsDay=3, endsHour=12, endsMinute=30
        )
        earmarks.create(sessionType=closed,
            startsDay=3, startsHour=12, startsMinute=30,
            endsDay=3, endsHour=13, endsMinute=0
        )
        earmarks.create(sessionType=scanning,
            startsDay=3, startsHour=13, startsMinute=0,
            endsDay=3, endsHour=18, endsMinute=0
        )
        earmarks.create(sessionType=otherUse,
            startsDay=3, startsHour=18, startsMinute=0,
            endsDay=3, endsHour=20, endsMinute=0
        )
        
        earmarks.create(sessionType=cleaning,
            startsDay=4, startsHour=8, startsMinute=0,
            endsDay=4, endsHour=9, endsMinute=15
        )
        earmarks.create(sessionType=scanning,
            startsDay=4, startsHour=9, startsMinute=15,
            endsDay=4, endsHour=12, endsMinute=30
        )
        earmarks.create(sessionType=closed,
            startsDay=4, startsHour=12, startsMinute=30,
            endsDay=4, endsHour=13, endsMinute=0
        )
        earmarks.create(sessionType=scanning,
            startsDay=4, startsHour=13, startsMinute=0,
            endsDay=4, endsHour=18, endsMinute=0
        )
        earmarks.create(sessionType=otherUse,
            startsDay=4, startsHour=18, startsMinute=0,
            endsDay=4, endsHour=20, endsMinute=0
        )
        
        earmarks.create(sessionType=cleaning,
            startsDay=5, startsHour=8, startsMinute=0,
            endsDay=5, endsHour=9, endsMinute=15
        )
        earmarks.create(sessionType=scanning,
            startsDay=5, startsHour=9, startsMinute=15,
            endsDay=5, endsHour=12, endsMinute=30
        )
        earmarks.create(sessionType=closed,
            startsDay=5, startsHour=12, startsMinute=30,
            endsDay=5, endsHour=13, endsMinute=0
        )
        earmarks.create(sessionType=scanning,
            startsDay=5, startsHour=13, startsMinute=0,
            endsDay=5, endsHour=18, endsMinute=0
        )
        earmarks.create(sessionType=otherUse,
            startsDay=5, startsHour=18, startsMinute=0,
            endsDay=5, endsHour=20, endsMinute=0
        )
        
        earmarks.create(sessionType=cleaning,
            startsDay=6, startsHour=8, startsMinute=0,
            endsDay=6, endsHour=9, endsMinute=15
        )
        earmarks.create(sessionType=scanning,
            startsDay=6, startsHour=9, startsMinute=15,
            endsDay=6, endsHour=12, endsMinute=30
        )
        earmarks.create(sessionType=closed,
            startsDay=6, startsHour=12, startsMinute=30,
            endsDay=6, endsHour=13, endsMinute=0
        )
        earmarks.create(sessionType=scanning,
            startsDay=6, startsHour=13, startsMinute=0,
            endsDay=6, endsHour=18, endsMinute=0
        )
        earmarks.create(sessionType=otherUse,
            startsDay=6, startsHour=18, startsMinute=0,
            endsDay=6, endsHour=20, endsMinute=0
        )
        

    def createWeekEarmarkTemplates(self):  # old class.
        sessionTypes = self.registry.sessionTypes
        standardWeek = self.registry.weekEarmarkTemplates.create('Standard')
        for day in range(0, 6):
            for hour in range(8, 20):
                for minute in range(0, 60, 15):
                    # Sat: before 1:00: other use, otherwise closed
                    # before 9:15: cleaning Tues and Thurs, otherwise other use
                    # after 6:00: closed
                    # after 4:45 before 6:00: other use
                    # otherwise: scanning
                    if day == 5:
                        if hour < 13:
                            sessionType = sessionTypes['Other Use']
                        else:
                            sessionType = sessionTypes['Closed']

                    else:
                        if (hour < 9) or (hour == 9 and minute < 15):
                            if day == 1 or day == 3:
                                sessionType = sessionTypes['Cleaning']
                            else:
                                sessionType = sessionTypes['Other Use']
                        elif hour >= 18:
                            sessionType = sessionTypes['Closed']
                        elif (hour == 16 and minute >= 45) or (hour == 17):
                            sessionType = sessionTypes['Other Use']
                        else:
                            if day == 3:
                                sessionType = sessionTypes['Reserved']
                            else:
                                sessionType = sessionTypes['Scanning']
                    
                    standardWeek.earmarkTemplates.create(
                        day=day,
                        hour=hour,
                        minute=minute,
                        sessionType=sessionType
                    )

    def createScanningSessionTypes(self):
        self.registry.scanningSessionTypes.create('Pilot')
        self.registry.scanningSessionTypes.create('Standard')
        
    def createTrainingSessionTypes(self):
        self.registry.trainingSessionTypes.create('AED')
        self.registry.trainingSessionTypes.create('AED Refresher')
        self.registry.trainingSessionTypes.create('First Aid')
        self.registry.trainingSessionTypes.create('MRI Practical')
        self.registry.trainingSessionTypes.create('MRI Video')
        self.registry.trainingSessionTypes.create('MRI Responsible')
        self.registry.trainingSessionTypes.create('Oxygen')       

    def createScanningSessionOutcomes(self):
        self.registry.scanningSessionOutcomes.create('Successful')
        self.registry.scanningSessionOutcomes.create('No Show')
        self.registry.scanningSessionOutcomes.create('Cancelled - Technical')
        self.registry.scanningSessionOutcomes.create('Cancelled - Researcher')
        self.registry.scanningSessionOutcomes.create('Partial Use')
        self.registry.scanningSessionOutcomes.create('Unsuccessful')

    def createResearcherStatuses(self):
        self.registry.researcherStatuses.create('Active Researcher')
        self.registry.researcherStatuses.create('Permanently Left')
        self.registry.researcherStatuses.create('Temporarily Away')

    def createVolunteerBookingMethods(self):
        self.registry.volunteerBookingMethods.create('BrainScan')
        self.registry.volunteerBookingMethods.create('Panel')
        self.registry.volunteerBookingMethods.create('To be confirmed')

    def createHandednesses(self):
        self.righthanded = self.registry.handednesses.create('Right-handed')
        self.lefthanded = self.registry.handednesses.create('Left-handed')
        self.ambidextrous = self.registry.handednesses.create('Ambidextrous')

    def createVolunteerRecruitmentMethods(self):
        self.registry.volunteerRecruitmentMethods.create('Word of Mouth')
        self.registry.volunteerRecruitmentMethods.create('APU Fresher')
        self.registry.volunteerRecruitmentMethods.create('CUSU Fresher')
        self.registry.volunteerRecruitmentMethods.create('Grafton Advert')
        self.registry.volunteerRecruitmentMethods.create('College Notice Board')
        self.registry.volunteerRecruitmentMethods.create('Don\'t Know')
        self.wordofmouth = self.registry.volunteerRecruitmentMethods['Word of Mouth']

    def createVolunteerStatuses(self):
        self.activeVol = self.registry.volunteerStatuses.create('Active')
        self.registry.volunteerStatuses.create('Inactive')

    def createVolunteerTypes(self):
        self.registry.volunteerTypes.create('Volunteer')
        self.registry.volunteerTypes.create('Patient')

    def createScanners(self):
        self.mriScanner = self.registry.scanners.create('MRI')
        self.registry.scanners.create('MEG')

    def createAccessStatuses(self):
        self.registry.accessStatuses.create('Unauthorised')
        self.registry.accessStatuses.create('Responsible')
        self.registry.accessStatuses.create('Certified')
        self.registry.accessStatuses.create('Radiographer')
    
    def createProjectStatuses(self):
        self.registry.projectStatuses.create('Dormant')
        self.registry.projectStatuses.create('Active')
        self.registry.projectStatuses.create('Completed')
    
    def createProjectOutcomes(self):
        self.registry.projectOutcomes.create('Published')
        self.registry.projectOutcomes.create('In Analysis')
        self.registry.projectOutcomes.create('In Scanning')
        self.registry.projectOutcomes.create('Abandoned')
    
    def createFundingStatuses(self):
        self.fundedMRC = self.registry.fundingStatuses.create(
            title='Fully MRC Funded',
        )
        self.registry.fundingStatuses.create(
            title='Collaborative Study',
        )
        self.fundedSpecialTerms = self.registry.fundingStatuses.create(
            title='Paying [Special Terms]',
        )
        self.registry.fundingStatuses.create(
            title='Paying [Full Cost]',
        )
    
    def createGroups(self):
        self.emotion = self.registry.groups.create(
            abbreviation='EMO',
            title='Emotion',
            funding=self.fundedMRC,
        )
        self.attention = self.registry.groups.create(
            abbreviation='ATT',
            title='Attention',
            funding=self.fundedMRC,
        )
        self.memory = self.registry.groups.create(
            abbreviation='MEM',
            title='Memory',
            funding=self.fundedMRC,
        )
        self.registry.groups.create(
            abbreviation='S&L',
            title='Speech & Language',
            funding=self.fundedMRC,
        )
        self.registry.groups.create(
            abbreviation='WBIC',
            title='WBIC',
            external=True,
            funding=self.fundedSpecialTerms,
        )
        self.registry.groups.create(
            abbreviation='DPY',
            title='Dept. Psychiatry',
            external=True,
            funding=self.fundedSpecialTerms,
        )
        self.registry.groups.create(
            abbreviation='CSL',
            title='CSL',
            external=True,
            funding=self.fundedSpecialTerms,
        )

    def createSessionTypes(self):
        self.registry.sessionTypes.create(name='Scanning', color="FFFF00")
        self.registry.sessionTypes.create(name='Maintenance', color="CCCCCC")
        self.registry.sessionTypes.create(name='Cleaning', color="CCFFFF")
        self.registry.sessionTypes.create(name='Reserved', color="FF6666")
        self.registry.sessionTypes.create(name='Other Use', color="CC66FF")
        self.registry.sessionTypes.create(name='Closed', color="666666")

    def createPerson(self, username, role, fullname, password, researcher=None):
        cmd = PersonCreate(username,
            role=role,
            fullname=fullname,
            researcher=researcher,
            passwordcleartext=password,
        )
        cmd.execute()

    def setUpTestFixtures(self):
        self.createGroups()
        self.registry.organisations.create(formalName='Acme')
        volvok = self.registry.volunteers.create(
            realname=u'Volvok \xf3',
            handedness = self.righthanded,
            recruitment = self.wordofmouth,
            status = self.activeVol,
            dateOfBirth = mx.DateTime.DateTime(1974, 6, 2, 0, 0, 0)
        )
        rapunzel = self.registry.radiographers.create(
            realname=u'Rapunzel \xf3'
        )
        regina = self.registry.researchers.create(
            realname=u'Regina \xf3', initials='RG'
        )
            
        william = self.registry.researchers.create(
            realname=u'William Marslen-Wilson \xf3', initials='WMW'
        )
        sonia = self.registry.researchers.create(
            realname=u'Sonia Bishop \xf3', initials='SB', theory=True, practical=True
        )
        adrian = self.registry.researchers.create(
            realname=u'Adrian Owen \xf3', initials='AO', theory=True, practical=True
        )
        rhodri = self.registry.researchers.create(
            realname=u'Rhodri Cusack \xf3', initials='RC'
        )
        alexandra = self.registry.researchers.create(
            realname=u'Alexandra Woogar \xf3', initials='AW',
            theory=True, practical=True, AED=True,
        )
        william.principalships.create(self.memory)
        regina.memberships.create(self.emotion)
        sonia.memberships.create(self.emotion)
        adrian.principalships.create(self.emotion)
        rhodri.memberships.create(self.emotion)
        alexandra.memberships.create(self.emotion)
        staffRole = self.registry.roles['Staff']
        piRole = self.registry.roles['PrincipalInvestigator']
        researcherRole = self.registry.roles['Researcher']
        adminRole = self.registry.roles['Administrator']
        self.createPerson('wwilson',piRole,'William Marslen-Wilson','pass',william)
        self.createPerson('sbishop',researcherRole,u'Sonia Bishop \xb3','pass',sonia)
        self.createPerson('aowen',researcherRole,u'Adrian Owen \xb3','pass',adrian)
        self.createPerson('rcusack',staffRole,u'Rhodri Cusack \xb3','pass',rhodri)
        self.createPerson('lmurby', adminRole, u'Lucille Murby \xb3', 'pass')
        self.createPerson('awoogar', researcherRole, u'Alexandra Woogar \xb3', 'pass')
        
        starts = mx.DateTime.Date(2005, 6, 13, 10,  0, 0)
        ends   = mx.DateTime.Date(2005, 6, 13, 11, 30, 0)
        self.registry.maintenanceSessions.create(
            scanner=self.mriScanner, starts=starts, ends=ends
        )
        starts = mx.DateTime.Date(2005, 6, 14, 8,  30, 0)
        ends   = mx.DateTime.Date(2005, 6, 14, 10,  0, 0)
        self.registry.maintenanceSessions.create(
            scanner=self.mriScanner, starts=starts, ends=ends
        )
        starts = mx.DateTime.Date(2005, 6, 16, 8,   0, 0)
        ends   = mx.DateTime.Date(2005, 6, 16, 16,  0, 0)
        self.registry.maintenanceSessions.create(
            scanner=self.mriScanner, starts=starts, ends=ends
        )
        approval1 = self.registry.approvals.create(
            code='456-654-1',
            numberAllocated=50,
            expires=mx.DateTime.DateTime(2021, 1, 1, 0, 0, 0),
        )
        approval1.principalInvestigators.create(sonia)
        approval2 = self.registry.approvals.create(
            code='456-654-2',
            numberAllocated=50,
            expires=mx.DateTime.DateTime(2021, 1, 1, 0, 0, 0),
        )
        approval3 = self.registry.approvals.create(
            code='456-654-3',
            numberAllocated=50,
            expires=mx.DateTime.DateTime(2021, 1, 1, 0, 0, 0),
        )
        approval3.principalInvestigators.create(adrian)
        approval3.additionalResearchers.create(rhodri)
        approval4 = self.registry.approvals.create(
            code='000-000-1',
            numberAllocated=50,
            expires=mx.DateTime.DateTime(2001, 1, 1, 0, 0, 0),
        )
        approval4.principalInvestigators.create(sonia)
        project1 = self.registry.projects.create(
            title="My First Project",
            leader = sonia,
        )
        project1.researchers.create(alexandra)
        project1.approvals.create(approval1)
        project1.approvals.create(approval4)
        project2 = self.registry.projects.create(
            title="My Second Project",
        )
        project2.researchers.create(rhodri)
        project3 = self.registry.projects.create(
            title="My Third Project",
        )
        project3.researchers.create(alexandra)
        project4 = self.registry.projects.create(
            title="Approval Expired Project",
            leader=sonia,
        )
        project4.researchers.create(sonia)
        project4.approvals.create(approval4)
        
        self.registry.accounts.create(
            code = "General Account #1"
        )

    def createSetting(self):
        defaultSettings = self.registry.settings.create('default')
        defaultSettings.earmarkTemplate = self.registry.earmarkedTimeTemplateWeeks['Standard']
        defaultSettings.save()

    def tearDownTestFixtures(self):
        pass
        
    def purgePackage(packageName):
        pass


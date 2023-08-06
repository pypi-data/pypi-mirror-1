import scanbooker.django.settings.main
from dm.view.base import SessionView

class ScanBookerView(SessionView):

    # todo: contacts contain researchers etc

    majorNavigation = []

    def __init__(self, *args, **kwds):
        super(ScanBookerView, self).__init__(*args, **kwds)
        self._canCreateEarmarkedTime = None
        self._canReadEarmarkedTime = None
        self._canUpdateEarmarkedTime = None
        self._canDeleteEarmarkedTime = None
        self._canCreateScanningSession = None
        self._canReadScanningSession = None
        self._canUpdateScanningSession = None
        self._canDeleteScanningSession = None
        self._canCreateMaintenanceSession = None
        self._canReadMaintenanceSession = None
        self._canUpdateMaintenanceSession = None
        self._canDeleteMaintenanceSession = None
        self._canCreateDowntimeSession = None
        self._canReadDowntimeSession = None
        self._canUpdateDowntimeSession = None
        self._canDeleteDowntimeSession = None
        self._canReadOrganisation = None
        self._canReadGroup = None
        self._canReadResearcher = None
        self._canReadVolunteer = None
        self._canCreateVolunteerScanningAppointment = None
        self._canReadApproval = None
        self._canReadProject = None
        self._canReadTrainingSession = None
        self._canReadReport = None
        self._canReadSetting = None
        self._canCreateAccount = None
        self._canReadAccount = None
        self._canUpdateAccount = None
        self._canDeleteAccount = None
        self.defaultSettings = None

    def setMajorNavigationItems(self):
        items = []
        if self.canReadSystem():
            items.append({'title': 'Schedule', 'url': '/schedule/'})
        if self.canReadProject():
            items.append({'title': 'Projects', 'url': '/projects/'})
        if self.canReadResearcher():
            items.append({'title': 'Researchers', 'url': '/researchers/'})
        if self.canReadApproval():
            items.append({'title': 'Ethics', 'url': '/approvals/'})
        if self.canReadAccount():
            items.append({'title': 'Accounting', 'url': '/accounts/'})
        if self.canReadVolunteer():
            items.append({'title': 'Volunteers', 'url': '/volunteers/'})
        if self.canReadGroup():
            items.append({'title': 'Groups', 'url': '/groups/'})
        if self.canReadOrganisation():
            items.append({'title': 'Organisations', 'url': '/organisations/'})
        if self.canReadTrainingSession():
            items.append({'title': 'Training', 'url': '/trainingSessions/'})
        if self.canReadReport():
            items.append({'title': 'Reports', 'url': '/reports/'})
        if self.canReadSetting():
            items.append({'title': 'Settings', 'url': '/settings/'})
        if self.canReadSystem():
            items.append({'title': 'Help', 'url': '/help/'})
        if not items:
            items.append({'title': 'Login', 'url': '/login/'})
        self.majorNavigation = items

    def canCreateEarmarkedTime(self):
        if self._canCreateEarmarkedTime == None:
            protectedObject = self.getDomainClass('EarmarkedTime')
            self._canCreateEarmarkedTime = self.canCreate(protectedObject)
        return self._canCreateEarmarkedTime
    
    def canReadEarmarkedTime(self):
        if self._canReadEarmarkedTime == None:
            protectedObject = self.getDomainClass('EarmarkedTime')
            self._canReadEarmarkedTime = self.canRead(protectedObject)
        return self._canReadEarmarkedTime
    
    def canUpdateEarmarkedTime(self):
        if self._canUpdateEarmarkedTime == None:
            protectedObject = self.getDomainClass('EarmarkedTime')
            self._canUpdateEarmarkedTime = self.canUpdate(protectedObject)
        return self._canUpdateEarmarkedTime
    
    def canDeleteEarmarkedTime(self):
        if self._canDeleteEarmarkedTime == None:
            protectedObject = self.getDomainClass('EarmarkedTime')
            self._canDeleteEarmarkedTime = self.canDelete(protectedObject)
        return self._canDeleteEarmarkedTime

    def canCreateScanningSession(self):
        if self._canCreateScanningSession == None:
            protectedObject = self.getDomainClass('ScanningSession')
            self._canCreateScanningSession = self.canCreate(protectedObject)
        return self._canCreateScanningSession

    def canReadScanningSession(self):
        if self._canReadScanningSession == None:
            protectedObject = self.getDomainClass('ScanningSession')
            self._canReadScanningSession = self.canRead(protectedObject)
        return self._canReadScanningSession

    def canUpdateScanningSession(self):
        if self._canUpdateScanningSession == None:
            protectedObject = self.getDomainClass('ScanningSession')
            self._canUpdateScanningSession = self.canUpdate(protectedObject)
        return self._canUpdateScanningSession

    def canDeleteScanningSession(self):
        if self._canDeleteScanningSession == None:
            protectedObject = self.getDomainClass('ScanningSession')
            self._canDeleteScanningSession = self.canDelete(protectedObject)
        return self._canDeleteScanningSession

    def canCreateMaintenanceSession(self):
        if self._canCreateMaintenanceSession == None:
            protectedObject = self.getDomainClass('MaintenanceSession')
            self._canCreateMaintenanceSession = self.canCreate(protectedObject)
        return self._canCreateMaintenanceSession

    def canReadMaintenanceSession(self):
        if self._canReadMaintenanceSession == None:
            protectedObject = self.getDomainClass('MaintenanceSession')
            self._canReadMaintenanceSession = self.canRead(protectedObject)
        return self._canReadMaintenanceSession

    def canUpdateMaintenanceSession(self):
        if self._canUpdateMaintenanceSession == None:
            protectedObject = self.getDomainClass('MaintenanceSession')
            self._canUpdateMaintenanceSession = self.canUpdate(protectedObject)
        return self._canUpdateMaintenanceSession

    def canDeleteMaintenanceSession(self):
        if self._canDeleteMaintenanceSession == None:
            protectedObject = self.getDomainClass('MaintenanceSession')
            self._canDeleteMaintenanceSession = self.canDelete(protectedObject)
        return self._canDeleteMaintenanceSession

    def canCreateDowntimeSession(self):
        if self._canCreateDowntimeSession == None:
            protectedObject = self.getDomainClass('DowntimeSession')
            self._canCreateDowntimeSession = self.canCreate(protectedObject)
        return self._canCreateDowntimeSession
        
    def canReadDowntimeSession(self):
        if self._canReadDowntimeSession == None:
            protectedObject = self.getDomainClass('DowntimeSession')
            self._canReadDowntimeSession = self.canRead(protectedObject)
        return self._canReadDowntimeSession
        
    def canUpdateDowntimeSession(self):
        if self._canUpdateDowntimeSession == None:
            protectedObject = self.getDomainClass('DowntimeSession')
            self._canUpdateDowntimeSession = self.canUpdate(protectedObject)
        return self._canUpdateDowntimeSession
        
    def canDeleteDowntimeSession(self):
        if self._canDeleteDowntimeSession == None:
            protectedObject = self.getDomainClass('DowntimeSession')
            self._canDeleteDowntimeSession = self.canDelete(protectedObject)
        return self._canDeleteDowntimeSession
        
    def canReadOrganisation(self):
        if self._canReadOrganisation == None:
            protectedObject = self.getDomainClass('Organisation')
            self._canReadOrganisation = self.canRead(protectedObject)
        return self._canReadOrganisation
        
    def canReadGroup(self):
        if self._canReadGroup == None:
            protectedObject = self.getDomainClass('Group')
            self._canReadGroup = self.canRead(protectedObject)
        return self._canReadGroup
        
    def canReadResearcher(self):
        if self._canReadResearcher == None:
            protectedObject = self.getDomainClass('Researcher')
            self._canReadResearcher = self.canRead(protectedObject)
        return self._canReadResearcher
    
    def canReadVolunteer(self):
        if self._canReadVolunteer == None:
            protectedObject = self.getDomainClass('Volunteer')
            self._canReadVolunteer = self.canRead(protectedObject)
        return self._canReadVolunteer
        
    def canCreateVolunteerScanningAppointment(self):
        if self._canCreateVolunteerScanningAppointment == None:
            protectedObject = self.getDomainClass(
                'VolunteerScanningAppointment')
            self._canCreateVolunteerScanningAppointment = self.canCreate(
                protectedObject)
        return self._canCreateVolunteerScanningAppointment
        
    def canReadApproval(self):
        if self._canReadApproval == None:
            protectedObject = self.getDomainClass('Approval')
            self._canReadApproval = self.canRead(protectedObject)
        return self._canReadApproval
        
    def canReadProject(self):
        if self._canReadProject == None:
            protectedObject = self.getDomainClass('Project')
            self._canReadProject = self.canRead(protectedObject)
        return self._canReadProject
        
    def canReadTrainingSession(self):
        if self._canReadTrainingSession == None:
            protectedObject = self.getDomainClass('TrainingSession')
            self._canReadTrainingSession = self.canRead(protectedObject)
        return self._canReadTrainingSession
        
    def canReadReport(self):
        if self._canReadReport == None:
            protectedObject = self.getDomainClass('Report')
            self._canReadReport = self.canRead(protectedObject)
        return self._canReadReport
        
    def canReadSetting(self):
        if self._canReadSetting == None:
            protectedObject = self.getDomainClass('Setting')
            self._canReadSetting = self.canRead(protectedObject)
        return self._canReadSetting
        
    def canCreateAccount(self):
        if self._canCreateAccount == None:
            protectedObject = self.getDomainClass('Account')
            self._canCreateAccount = self.canCreate(protectedObject)
        return self._canCreateAccount
    
    def canReadAccount(self):
        if self._canReadAccount == None:
            protectedObject = self.getDomainClass('Account')
            self._canReadAccount = self.canRead(protectedObject)
        return self._canReadAccount
    
    def canUpdateAccount(self):
        if self._canUpdateAccount == None:
            protectedObject = self.getDomainClass('Account')
            self._canUpdateAccount = self.canUpdate(protectedObject)
        return self._canUpdateAccount
    
    def canDeleteAccount(self):
        if self._canDeleteAccount == None:
            protectedObject = self.getDomainClass('Account')
            self._canDeleteAccount = self.canDelete(protectedObject)
        return self._canDeleteAccount

    def isViewerAdministrator(self):
        if self.session and self.session.person and self.session.person.role:
            if self.session.person.role.name == "Administrator":
                return True
        return False

    def showInlineHelp(self):
        return self.getDefaultSettings().showInlineHelp

    def hasListallPage(self):
        return True

    def getDefaultSettings(self):
        if self.defaultSettings == None:
            self.defaultSettings = self.registry.settings['default']
        return self.defaultSettings
 

from scanbooker.django.apps.sui.views.base import ScanBookerView
from scanbooker.django.apps.sui.views.manipulator import EarmarkedTimeCreateManipulator
from scanbooker.django.apps.sui.views.manipulator import EarmarkedTimeUpdateManipulator
from scanbooker.django.apps.sui.views.manipulator import MaintenanceSessionCreateManipulator
from scanbooker.django.apps.sui.views.manipulator import MaintenanceSessionUpdateManipulator
from scanbooker.django.apps.sui.views.manipulator import MethodsSessionCreateManipulator
from scanbooker.django.apps.sui.views.manipulator import MethodsSessionUpdateManipulator
from scanbooker.django.apps.sui.views.manipulator import ScanningSessionCreateManipulator
from scanbooker.django.apps.sui.views.manipulator import ScanningSessionUpdateManipulator
from scanbooker.django.apps.sui.views.manipulator import TrainingSessionCreateManipulator
from scanbooker.django.apps.sui.views.manipulator import TrainingSessionUpdateManipulator
from scanbooker.django.apps.sui.views.manipulator import DowntimeSessionCreateManipulator
from scanbooker.django.apps.sui.views.manipulator import DowntimeSessionUpdateManipulator
from scanbooker.django.apps.sui.views.manipulator import AccountManipulator
from scanbooker.django.apps.sui.views.manipulator import ApprovalManipulator
from scanbooker.django.apps.sui.views.manipulator import ProjectManipulator
from scanbooker.django.apps.sui.views.manipulator import VolunteerManipulator
from scanbooker.django.apps.sui.views.manipulator import ReportCreateManipulator
from scanbooker.django.apps.sui.views.manipulator import ReportUpdateManipulator
from dm.view.registry import RegistryView
from dm.view.registry import RegistryListView
from dm.view.registry import RegistryListallView
from dm.view.registry import RegistryCreateView
from dm.view.registry import RegistryReadView
from dm.view.registry import RegistrySearchView
from dm.view.registry import RegistryFindView
from dm.view.registry import RegistryUpdateView
from dm.view.registry import RegistryDeleteView

class FieldNames(list):

    def __init__(self, *args, **kwds):
        super(FieldNames, self).__init__(*args, **kwds)


class SettingsFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(SettingsFieldNames, self).__init__(*args, **kwds)
        self.append('requireTrainedProjectLeader')
        self.append('requireApprovedProjectLeader')
        self.append('requireEthicsApprovalInDate')
        self.append('requireEthicsApprovalBalance')
        self.append('showInlineHelp')
        self.append('earmarkTemplate')


class ResearcherFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(ResearcherFieldNames, self).__init__(*args, **kwds)
        self.append('realname')
        self.append('initials')
        self.append('external')
        self.append('email')
        self.append('principalships')
        self.append('memberships')
        self.append('telephoneInternal')
        self.append('telephoneExternal')
        self.append('trainingSessions')
        self.append('theory')
        self.append('practical')
        self.append('AED')
        self.append('mriAccessStatus')
        self.append('leadingProjects')
        self.append('projects')
        self.append('principalApprovals')
        self.append('additionalApprovals')
        self.append('notes')
        self.append('status')


class RadiographerFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(RadiographerFieldNames, self).__init__(*args, **kwds)
        self.append('realname')


class VolunteerFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(VolunteerFieldNames, self).__init__(*args, **kwds)
        self.append('realname')
        self.append('dateOfBirth')
        self.append('language')
        self.append('panelId')
        self.append('status')
        self.append('onHitlist')
        self.append('handedness')
        self.append('homeAddress')
        self.append('recruitment')
        self.append('email')
        self.append('workTelephone')
        self.append('homeTelephone')
        self.append('mobileTelephone')
        self.append('doctorAddress')
        self.append('doctorName')
        self.append('doctorTelephone')
        self.append('notes')


class OrganisationFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(OrganisationFieldNames, self).__init__(*args, **kwds)
        self.append('formalName')
        self.append('nickname')
        self.append('streetAddress')
        self.append('mainContact')
        self.append('telephone')
        self.append('email')
        self.append('fax')
        self.append('reference')
        self.append('accounts')
        self.append('groups')
        self.append('billingContact')
        self.append('notes')


class GroupFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(GroupFieldNames, self).__init__(*args, **kwds)
        self.append('abbreviation')
        self.append('title')
        self.append('funding')
        self.append('description')
        self.append('principals')
        self.append('researchers')
        self.append('organisations')
        self.append('external')
        self.append('notes')


class GroupFieldNamesRead(GroupFieldNames):

    def __init__(self, *args, **kwds):
        super(GroupFieldNamesRead, self).__init__(*args, **kwds)
        #self.append('researchers')


class EarmarkedTimeFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(EarmarkedTimeFieldNames, self).__init__(*args, **kwds)
        # see manipulator
        #self.append('sessionType')
        #self.append('comment')


class DowntimeSessionFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(DowntimeSessionFieldNames, self).__init__(*args, **kwds)
        # see manipulator


class MaintenanceSessionFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(MaintenanceSessionFieldNames, self).__init__(*args, **kwds)
        self.append('comment')


class MethodsSessionFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(MethodsSessionFieldNames, self).__init__(*args, **kwds)
        self.append('comment')


class TrainingSessionFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(TrainingSessionFieldNames, self).__init__(*args, **kwds)
        self.append('start')
        self.append('end')
        self.append('type')
        self.append('date')
        self.append('location')
        self.append('presenter')
        self.append('researchers')


class ApprovalFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(ApprovalFieldNames, self).__init__(*args, **kwds)
        self.append('code')
        self.append('description')
        #self.append('projects')
        self.append('principalInvestigators')
        self.append('additionalResearchers')
        self.append('numberAllocated')
        self.append('numberUsedAdjustment')
        self.append('expires')
        self.append('notes')


class ProjectFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(ProjectFieldNames, self).__init__(*args, **kwds)
        self.append('title')
        self.append('nickname')
        self.append('leader')
        self.append('account')
        self.append('researchers')
        self.append('approvals')
        self.append('funding')
        self.append('status')
        self.append('outcome')
        self.append('preparationMinutes')
        self.append('volunteerBookingMethod')
        self.append('IIGPresentation')
        self.append('IMCApproval')
        self.append('numberSubjects')
        self.append('numberPilots')
        self.append('slotMinutes')
        self.append('volunteerType')
        self.append('startDate')
        self.append('completionDate')
        self.append('notes')


class ScannerFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(ScannerFieldNames, self).__init__(*args, **kwds)
        self.append('name')
        self.append('description')


# Old class.
class WeekEarmarkTemplateFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(WeekEarmarkTemplateFieldNames, self).__init__(
            *args, **kwds)
        self.append('name')


class EarmarkedTimeTemplateWeekFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(EarmarkedTimeTemplateWeekFieldNames, self).__init__(
            *args, **kwds)
        self.append('name')


class ReportFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(ReportFieldNames, self).__init__(*args, **kwds)
        self.append('title')
        self.append('against')


class AccountFieldNames(FieldNames):

    def __init__(self, *args, **kwds):
        super(AccountFieldNames, self).__init__(*args, **kwds)
        self.append('code')
        self.append('comment')
        self.append('notes')
        self.append('researchers')
        #self.append('qqrCode')  # For Lucille.
        #self.append('wbsCode')  # For Lucille.
        #self.append('projects')
        self.append('organisations')


class SettingsManipulateRedirector(object):

    def __init__(self, view):
        self.view = view

    def createLocationPath(self):
        return '/settings/'


class SessionManipulateRedirector(object):

    def __init__(self, view):
        self.view = view

    def createLocationPath(self):
        session = self.view.domainObject
        year = str(session.starts.year)
        month = str(session.starts.month)
        day = str(session.starts.day)
        location = '/schedule/week/%s/%s/%s/' % (year, month, day)
        return location


# Old class.
class WeekEarmarkTemplateManipulateRedirector(object):

    def __init__(self, view):
        self.view = view

    def createLocationPath(self):
        weekEarmarkTemplate = self.view.domainObject
        return '/weekEarmarkTemplates/%s/' % (
            weekEarmarkTemplate.name
        )


class EarmarkedTimeTemplateWeekManipulateRedirector(object):

    def __init__(self, view):
        self.view = view

    def createLocationPath(self):
        earmarkedTimeTemplateWeek = self.view.domainObject
        return '/earmarkedTimeTemplateWeeks/%s/' % (
            earmarkedTimeTemplateWeek.name
        )


class ReportCreatedRedirector(object):

    def __init__(self, view):
        self.view = view

    def createLocationPath(self):
        return '/reports/%s/update/' % self.view.domainObject.id


class SettingsManipulateNavigation(object):

    def __init__(self, view):
        self.view = view

    def createMajorItem(self):
        return '/settings/'
    
    def createMinorItem(self):
        return '/settings/'
    
    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Default', 'url': '/settings/'}
        )
        return items


class SessionManipulateNavigation(object):

    def __init__(self, view):
        self.view = view

    def createMajorItem(self):
        return '/schedule/'
    
    def createMinorItem(self):
        #return '/schedule/week/'
        return ''
    
    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Week', 'url': '/schedule/week/'}
        )
        if self.view.canCreateScanningSession():
            items.append(
                {'title': 'Quick entry', 'url': '/scanningSessions/create/'}
            )
        return items
 

class RegistryManipulateNavigation(object):

    def __init__(self, view):
        self.view = view

    def createMajorItem(self):
        return self.createMinorItem()
    
    def createMinorItem(self):
        return ''
    
    def createMinorItems(self):
        items = []
        return items
 

class ScannerManipulateNavigation(RegistryManipulateNavigation):
    
    def createMinorItem(self):
        return '/scanners/'


# Old class.
class WeekEarmarkTemplateManipulateNavigation(RegistryManipulateNavigation):
    
    def createMinorItem(self):
        return '/weekEarmarkTemplates/'


class EarmarkedTimeTemplateWeekManipulateNavigation(RegistryManipulateNavigation):
    
    def createMinorItem(self):
        return '/earmarkedTimeTemplateWeeks/'

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/earmarkedTimeTemplateWeeks/'}
        )
        items.append(
            {'title': 'Search', 'url': '/earmarkedTimeTemplateWeeks/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/earmarkedTimeTemplateWeeks/create/'}
        )
        return items


#class ResearcherManipulateNavigation(RegistryManipulateNavigation):
#    
#    def createMinorItem(self):
#        return '/researchers/'


class RadiographerManipulateNavigation(RegistryManipulateNavigation):
 
    def createMinorItem(self):
        return '/radiographers/'


class VolunteerManipulateNavigation(RegistryManipulateNavigation):
    
    def createMajorItem(self):
        return '/volunteers/'

    def createMinorItem(self):
        return ''
    
    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/volunteers/'}
        )
        items.append(
            {'title': 'Search', 'url': '/volunteers/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/volunteers/create/'}
        )
        if self.view.canCreateVolunteerScanningAppointment():
            items.append(
                {'title': 'Booking', 'url': '/volunteers/booking/'}
            )
            items.append(
                {'title': 'Cancellation', 'url': '/volunteers/cancellation/'}
            )
            items.append(
                {'title': 'Hitlist', 'url': '/volunteers/hitlist/'}
            )
        return items


class VolunteerFindNavigation(VolunteerManipulateNavigation):

    def createMinorItem(self):
        return '/volunteers/search/'


class VolunteerBookingNavigation(VolunteerManipulateNavigation):

    def createMinorItem(self):
        return '/volunteers/booking/'


class VolunteerCancellationNavigation(VolunteerManipulateNavigation):

    def createMinorItem(self):
        return '/volunteers/cancellation/'


class VolunteerHitlistNavigation(VolunteerManipulateNavigation):

    def createMinorItem(self):
        return '/volunteers/hitlist/'


class ResearcherManipulateNavigation(RegistryManipulateNavigation):
    
    def createMajorItem(self):
        return '/researchers/'

    def createMinorItem(self):
        return ''
    
    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/researchers/'}
        )
        items.append(
            {'title': 'Search', 'url': '/researchers/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/researchers/create/'}
        )
        return items


class ResearcherFindNavigation(ResearcherManipulateNavigation):

    def createMinorItem(self):
        return '/researchers/search/'


class OrganisationManipulateNavigation(RegistryManipulateNavigation):
    
    def createMajorItem(self):
        return '/organisations/'

    def createMinorItem(self):
        return ''
    
    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/organisations/'}
        )
        items.append(
            {'title': 'Search', 'url': '/organisations/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/organisations/create/'}
        )
        return items


class GroupManipulateNavigation(RegistryManipulateNavigation):
    
    def createMajorItem(self):
        return '/groups/'

    def createMinorItem(self):
        return ''
    
    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/groups/'}
        )
        items.append(
            {'title': 'Search', 'url': '/groups/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/groups/create/'}
        )
        return items


class TrainingSessionManipulateNavigation(RegistryManipulateNavigation):
    
    def createMajorItem(self):
        return '/trainingSessions/'

    def createMinorItem(self):
        return ''
    
    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/trainingSessions/'}
        )
        items.append(
            {'title': 'New', 'url': '/trainingSessions/create/'}
        )
        return items


class OrganisationFindNavigation(OrganisationManipulateNavigation):

    def createMinorItem(self):
        return '/organisations/search/'


class GroupFindNavigation(GroupManipulateNavigation):

    def createMinorItem(self):
        return '/groups/search/'


class ApprovalManipulateNavigation(RegistryManipulateNavigation):
    
    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/approvals/'}
        )
        items.append(
            {'title': 'Search', 'url': '/approvals/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/approvals/create/'}
        )
        return items

    def createMajorItem(self):
        return '/approvals/'
        
    def createMinorItem(self):
        return ''
    

class ApprovalFindNavigation(ApprovalManipulateNavigation):

    def createMinorItem(self):
        return '/approvals/search/'


class ProjectManipulateNavigation(RegistryManipulateNavigation):
    
    def createMajorItem(self):
        return '/projects/'

    def createMinorItem(self):
        return ''
    
    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/projects/'}
        )
        items.append(
            {'title': 'Search', 'url': '/projects/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/projects/create/'}
        )
        return items


class ProjectFindNavigation(ProjectManipulateNavigation):

    def createMinorItem(self):
        return '/projects/search/'


class AccountManipulateNavigation(RegistryManipulateNavigation):
    
    def createMajorItem(self):
        return '/accounts/'

    def createMinorItem(self):
        return ''
    
    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/accounts/'}
        )
        items.append(
            {'title': 'Search', 'url': '/accounts/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/accounts/create/'}
        )
        return items


class AccountFindNavigation(AccountManipulateNavigation):

    def createMinorItem(self):
        return '/accounts/search/'


class ReportManipulateNavigation(RegistryManipulateNavigation):
    
    def createMajorItem(self):
        return '/reports/'

    def createMinorItem(self):
        return ''
    
    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/reports/'}
        )
        items.append(
            {'title': 'Search', 'url': '/reports/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/reports/create/'}
        )
        return items


class ReportFindNavigation(ReportManipulateNavigation):

    def createMinorItem(self):
        return '/reports/search/'


class ScanBookerRegistryView(RegistryView, ScanBookerView):

    domainClassName = ''
    manipulatedFieldNames = {
        'settings/update': SettingsFieldNames(),
        'radiographers/create': RadiographerFieldNames(),
        'radiographers/read'  : RadiographerFieldNames(),
        'radiographers/update': RadiographerFieldNames(),
        'radiographers/delete': RadiographerFieldNames(),
        #'volunteers/create': VolunteerFieldNames(),
        'volunteers/read'  : VolunteerFieldNames(),
        #'volunteers/update': VolunteerFieldNames(),
        'volunteers/delete': VolunteerFieldNames(),
        'researchers/create': ResearcherFieldNames(),
        'researchers/read'  : ResearcherFieldNames(),
        'researchers/update': ResearcherFieldNames(),
        'researchers/delete': ResearcherFieldNames(),
        'organisations/create': OrganisationFieldNames(),
        'organisations/read':   OrganisationFieldNames(),
        'organisations/update': OrganisationFieldNames(),
        'organisations/delete': OrganisationFieldNames(),
        'groups/create': GroupFieldNames(),
        'groups/read':   GroupFieldNamesRead(),
        'groups/update': GroupFieldNames(),
        'groups/delete': GroupFieldNames(),
        'earmarkedTimes/create': EarmarkedTimeFieldNames(),
        'earmarkedTimes/read'  : EarmarkedTimeFieldNames(),
        'earmarkedTimes/update': EarmarkedTimeFieldNames(),
        'earmarkedTimes/delete': EarmarkedTimeFieldNames(),
        'downtimeSessions/create': DowntimeSessionFieldNames(),
        'downtimeSessions/read'  : DowntimeSessionFieldNames(),
        'downtimeSessions/update': DowntimeSessionFieldNames(),
        'downtimeSessions/delete': DowntimeSessionFieldNames(),
        'maintenanceSessions/create': MaintenanceSessionFieldNames(),
        'maintenanceSessions/read'  : MaintenanceSessionFieldNames(),
        'maintenanceSessions/update': MaintenanceSessionFieldNames(),
        'maintenanceSessions/delete': MaintenanceSessionFieldNames(),
        'methodsSessions/create': MethodsSessionFieldNames(),
        'methodsSessions/read'  : MethodsSessionFieldNames(),
        'methodsSessions/update': MethodsSessionFieldNames(),
        'methodsSessions/delete': MethodsSessionFieldNames(),
        'trainingSessions/create': TrainingSessionFieldNames(),
        'trainingSessions/read'  : TrainingSessionFieldNames(),
        'trainingSessions/update': TrainingSessionFieldNames(),
        'trainingSessions/delete': TrainingSessionFieldNames(),
        'approvals/create': ApprovalFieldNames(),
        'approvals/read'  : ApprovalFieldNames(),
        'approvals/update': ApprovalFieldNames(),
        'approvals/delete': ApprovalFieldNames(),
        'projects/create': ProjectFieldNames(),
        'projects/read'  : ProjectFieldNames(),
        'projects/update': ProjectFieldNames(),
        'projects/delete': ProjectFieldNames(),
        'scanners/create': ScannerFieldNames(),
        'scanners/read'  : ScannerFieldNames(),
        'scanners/update': ScannerFieldNames(),
        'scanners/delete': ScannerFieldNames(),
        'weekEarmarkTemplates/create': WeekEarmarkTemplateFieldNames(), # Old class.
        'weekEarmarkTemplates/read'  : WeekEarmarkTemplateFieldNames(), # Old class.
        'weekEarmarkTemplates/update': WeekEarmarkTemplateFieldNames(), # Old class.
        'weekEarmarkTemplates/delete': WeekEarmarkTemplateFieldNames(), # Old class.
        'earmarkedTimeTemplateWeeks/list': EarmarkedTimeTemplateWeekFieldNames(),
        'earmarkedTimeTemplateWeeks/create': EarmarkedTimeTemplateWeekFieldNames(),
        'earmarkedTimeTemplateWeeks/read'  : EarmarkedTimeTemplateWeekFieldNames(),
        'earmarkedTimeTemplateWeeks/update': EarmarkedTimeTemplateWeekFieldNames(),
        'earmarkedTimeTemplateWeeks/delete': EarmarkedTimeTemplateWeekFieldNames(),
        'reports/read'  : ReportFieldNames(),
        'reports/delete': ReportFieldNames(),
        'accounts/create': AccountFieldNames(),
        'accounts/read'  : AccountFieldNames(),
        'accounts/update': AccountFieldNames(),
        'accounts/delete': AccountFieldNames(),
    }
    manipulators = {
        'earmarkedTimes/create': EarmarkedTimeCreateManipulator,
        'earmarkedTimes/update': EarmarkedTimeUpdateManipulator,
        'maintenanceSessions/create': MaintenanceSessionCreateManipulator,
        'maintenanceSessions/update': MaintenanceSessionUpdateManipulator,
        'methodsSessions/create': MethodsSessionCreateManipulator,
        'methodsSessions/update': MethodsSessionUpdateManipulator,
        'trainingSessions/create': TrainingSessionCreateManipulator,
        'trainingSessions/read': TrainingSessionUpdateManipulator,
        'trainingSessions/update': TrainingSessionUpdateManipulator,
        'trainingSessions/delete': TrainingSessionCreateManipulator,
        'scanningSessions/read': ScanningSessionUpdateManipulator,
        'scanningSessions/create': ScanningSessionCreateManipulator,
        'scanningSessions/update': ScanningSessionUpdateManipulator,
        'scanningSessions/delete': ScanningSessionUpdateManipulator,
        'downtimeSessions/create': DowntimeSessionCreateManipulator,
        'downtimeSessions/update': DowntimeSessionUpdateManipulator,
        'accounts/create': AccountManipulator,
        'accounts/update': AccountManipulator,
        'approvals/create': ApprovalManipulator,
        'approvals/update': ApprovalManipulator,
        'projects/create': ProjectManipulator,
        'projects/update': ProjectManipulator,
        'volunteers/create': VolunteerManipulator,
        'volunteers/update': VolunteerManipulator,
        'reports/create': ReportCreateManipulator,
        'reports/update': ReportUpdateManipulator,
    }
    redirectors = {
        'settings/update': SettingsManipulateRedirector,
        'earmarkedTimes/create': SessionManipulateRedirector,
        'earmarkedTimes/update': SessionManipulateRedirector,
        'earmarkedTimes/delete': SessionManipulateRedirector,
        'maintenanceSessions/create': SessionManipulateRedirector,
        'maintenanceSessions/update': SessionManipulateRedirector,
        'maintenanceSessions/delete': SessionManipulateRedirector,
        'methodsSessions/create': SessionManipulateRedirector,
        'methodsSessions/update': SessionManipulateRedirector,
        'methodsSessions/delete': SessionManipulateRedirector,
        'scanningSessions/create': SessionManipulateRedirector,
        'scanningSessions/update': SessionManipulateRedirector,
        'scanningSessions/delete': SessionManipulateRedirector,
        'downtimeSessions/create': SessionManipulateRedirector,
        'downtimeSessions/update': SessionManipulateRedirector,
        'downtimeSessions/delete': SessionManipulateRedirector,
        'weekEarmarkTemplates/update': WeekEarmarkTemplateManipulateRedirector, # Old class.
        'earmarkedTimeTemplateWeeks/update': EarmarkedTimeTemplateWeekManipulateRedirector,
        'reports/create': ReportCreatedRedirector,
    }
    navigation = {
        'settings/update': SettingsManipulateNavigation,
        'earmarkedTimes/list':   SessionManipulateNavigation,
        'earmarkedTimes/create': SessionManipulateNavigation,
        'earmarkedTimes/read':   SessionManipulateNavigation,
        'earmarkedTimes/update': SessionManipulateNavigation,
        'earmarkedTimes/delete': SessionManipulateNavigation,
        'trainingSessions/list':   TrainingSessionManipulateNavigation,
        'trainingSessions/create': TrainingSessionManipulateNavigation,
        'trainingSessions/read':   TrainingSessionManipulateNavigation,
        'trainingSessions/update': TrainingSessionManipulateNavigation,
        'trainingSessions/delete': TrainingSessionManipulateNavigation,
        'maintenanceSessions/list':   SessionManipulateNavigation,
        'maintenanceSessions/create': SessionManipulateNavigation,
        'maintenanceSessions/read':   SessionManipulateNavigation,
        'maintenanceSessions/update': SessionManipulateNavigation,
        'maintenanceSessions/delete': SessionManipulateNavigation,
        'methodsSessions/list':   SessionManipulateNavigation,
        'methodsSessions/create': SessionManipulateNavigation,
        'methodsSessions/read':   SessionManipulateNavigation,
        'methodsSessions/update': SessionManipulateNavigation,
        'methodsSessions/delete': SessionManipulateNavigation,
        'scanningSessions/list':   SessionManipulateNavigation,
        'scanningSessions/create': SessionManipulateNavigation,
        'scanningSessions/read':   SessionManipulateNavigation,
        'scanningSessions/update': SessionManipulateNavigation,
        'scanningSessions/delete': SessionManipulateNavigation,
        'downtimeSessions/list':   SessionManipulateNavigation,
        'downtimeSessions/create': SessionManipulateNavigation,
        'downtimeSessions/read':   SessionManipulateNavigation,
        'downtimeSessions/update': SessionManipulateNavigation,
        'downtimeSessions/delete': SessionManipulateNavigation,
        'scanners/list':   ScannerManipulateNavigation,
        'scanners/create': ScannerManipulateNavigation,
        'scanners/read':   ScannerManipulateNavigation,
        'scanners/update': ScannerManipulateNavigation,
        'scanners/delete': ScannerManipulateNavigation,
        'weekEarmarkTemplates/list':   WeekEarmarkTemplateManipulateNavigation,
        'weekEarmarkTemplates/create': WeekEarmarkTemplateManipulateNavigation,
        'weekEarmarkTemplates/read':   WeekEarmarkTemplateManipulateNavigation,
        'weekEarmarkTemplates/update': WeekEarmarkTemplateManipulateNavigation,
        'weekEarmarkTemplates/delete': WeekEarmarkTemplateManipulateNavigation,
        'earmarkedTimeTemplateWeeks/list':   EarmarkedTimeTemplateWeekManipulateNavigation,
        'earmarkedTimeTemplateWeeks/create': EarmarkedTimeTemplateWeekManipulateNavigation,
        'earmarkedTimeTemplateWeeks/read':   EarmarkedTimeTemplateWeekManipulateNavigation,
        'earmarkedTimeTemplateWeeks/update': EarmarkedTimeTemplateWeekManipulateNavigation,
        'earmarkedTimeTemplateWeeks/delete': EarmarkedTimeTemplateWeekManipulateNavigation,
        'radiographers/list':   RadiographerManipulateNavigation,
        'radiographers/create': RadiographerManipulateNavigation,
        'radiographers/read':   RadiographerManipulateNavigation,
        'radiographers/update': RadiographerManipulateNavigation,
        'radiographers/delete': RadiographerManipulateNavigation,
        'volunteers/list':   VolunteerManipulateNavigation,
        'volunteers/create': VolunteerManipulateNavigation,
        'volunteers/read':   VolunteerManipulateNavigation,
        'volunteers/search': VolunteerManipulateNavigation,
        'volunteers/find':   VolunteerFindNavigation,
        'volunteers/update': VolunteerManipulateNavigation,
        'volunteers/delete': VolunteerManipulateNavigation,
        'volunteers/booking': VolunteerBookingNavigation,
        'volunteers/cancellation': VolunteerCancellationNavigation,
        'volunteers/hitlist': VolunteerHitlistNavigation,
        'researchers/list':   ResearcherManipulateNavigation,
        'researchers/create': ResearcherManipulateNavigation,
        'researchers/read':   ResearcherManipulateNavigation,
        'researchers/search': ResearcherManipulateNavigation,
        'researchers/find':   ResearcherFindNavigation,
        'researchers/update': ResearcherManipulateNavigation,
        'researchers/delete': ResearcherManipulateNavigation,
        'organisations/list':   OrganisationManipulateNavigation,
        'organisations/create': OrganisationManipulateNavigation,
        'organisations/read':   OrganisationManipulateNavigation,
        'organisations/search': OrganisationManipulateNavigation,
        'organisations/find':   OrganisationFindNavigation,
        'organisations/update': OrganisationManipulateNavigation,
        'organisations/delete': OrganisationManipulateNavigation,
        'groups/list':   GroupManipulateNavigation,
        'groups/create': GroupManipulateNavigation,
        'groups/read':   GroupManipulateNavigation,
        'groups/search': GroupManipulateNavigation,
        'groups/find':   GroupFindNavigation,
        'groups/update': GroupManipulateNavigation,
        'groups/delete': GroupManipulateNavigation,
        'groups/researchers/list':   GroupManipulateNavigation,
        'groups/researchers/create': GroupManipulateNavigation,
        'groups/researchers/read':   GroupManipulateNavigation,
        'groups/researchers/search': GroupManipulateNavigation,
        'groups/researchers/find':   GroupFindNavigation,
        'groups/researchers/update': GroupManipulateNavigation,
        'groups/researchers/delete': GroupManipulateNavigation,
        'approvals/list':   ApprovalManipulateNavigation,
        'approvals/create': ApprovalManipulateNavigation,
        'approvals/read':   ApprovalManipulateNavigation,
        'approvals/search': ApprovalManipulateNavigation,
        'approvals/find':   ApprovalFindNavigation,
        'approvals/update': ApprovalManipulateNavigation,
        'approvals/delete': ApprovalManipulateNavigation,
        'projects/list':   ProjectManipulateNavigation,
        'projects/create': ProjectManipulateNavigation,
        'projects/read':   ProjectManipulateNavigation,
        'projects/search': ProjectManipulateNavigation,
        'projects/find': ProjectFindNavigation,
        'projects/update': ProjectManipulateNavigation,
        'projects/delete': ProjectManipulateNavigation,
        'reports/list':   ReportManipulateNavigation,
        'reports/create': ReportManipulateNavigation,
        'reports/read':   ReportManipulateNavigation,
        'reports/search': ReportManipulateNavigation,
        'reports/find': ReportFindNavigation,
        'reports/update': ReportManipulateNavigation,
        'reports/delete': ReportManipulateNavigation,
        'accounts/list':   AccountManipulateNavigation,
        'accounts/create': AccountManipulateNavigation,
        'accounts/read':   AccountManipulateNavigation,
        'accounts/search': AccountManipulateNavigation,
        'accounts/find': AccountFindNavigation,
        'accounts/update': AccountManipulateNavigation,
        'accounts/delete': AccountManipulateNavigation,
    }


class ScanBookerRegistryListView(ScanBookerRegistryView, RegistryListView):
    pass

class ScanBookerRegistryListallView(ScanBookerRegistryView, RegistryListallView):
    pass

class ScanBookerRegistryCreateView(ScanBookerRegistryView, RegistryCreateView):
    pass

class ScanBookerRegistryReadView(ScanBookerRegistryView, RegistryReadView):
    pass

class ScanBookerRegistrySearchView(ScanBookerRegistryView, RegistrySearchView):
    pass

class ScanBookerRegistryFindView(ScanBookerRegistryView, RegistryFindView):
    pass

class ScanBookerRegistryUpdateView(ScanBookerRegistryView, RegistryUpdateView):
    
    def defaultPostManipulateLocation(self):
        registryPath = '/'.join(self.getRegistryPathNames())
        # For Lucille (MRC), redirect to list after update.
        #registryPath = '/'.join(self.getRegistryPathNames()[0:-1])  
        return '/' + registryPath + '/'


class ScanBookerRegistryDeleteView(ScanBookerRegistryView, RegistryDeleteView):
    pass


def view(request, registryPath, actionName='', actionValue=''):
    pathNames = registryPath.split('/')
    pathLen = len(pathNames)
    if not actionName:
        if pathLen % 2:
            actionName = 'list'
        else:
            actionName = 'read'
    if actionName == 'list':
        viewClass = ScanBookerRegistryListView
    elif actionName == 'listall':
        viewClass = ScanBookerRegistryListallView
        actionName = 'list'
    elif actionName == 'create':
        viewClass = ScanBookerRegistryCreateView
    elif actionName == 'read':
        viewClass = ScanBookerRegistryReadView
    elif actionName == 'search':
        viewClass = ScanBookerRegistrySearchView
    elif actionName == 'find':
        viewClass = ScanBookerRegistryFindView
    elif actionName == 'update':
        viewClass = ScanBookerRegistryUpdateView
    elif actionName == 'delete':
        viewClass = ScanBookerRegistryDeleteView
    elif actionName == 'undelete':
        viewClass = ScanBookerRegistryUndeleteView
    elif actionName == 'purge':
        viewClass = ScanBookerRegisryPurgeView
    else:
        raise Exception("No view class for actionName '%s'." % actionName)
    view = viewClass(
        request=request,
        registryPath=registryPath,
        actionName=actionName,
        actionValue=actionValue
    )
    return view.getResponse()


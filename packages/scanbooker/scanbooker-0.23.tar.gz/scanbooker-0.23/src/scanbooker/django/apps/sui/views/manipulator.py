import dm.webkit as webkit
from dm.webkit import *
from dm.view.manipulator import DomainObjectManipulator
from dm.view.manipulator import HasManyManipulator
from scanbooker.dictionarywords import *
import scanbooker.workingHours
import scanbooker.regexps
from scanbooker.exceptions import KforgeCommandError
import re
import mx.DateTime

# Todo: Create Person manipulators (update and create, a la KForge).
# Todo: Validate selected options is contained with given options.

DomainObjectManipulator.sizeSelectMultiple = 12

# Todo: Move validation errors to separate module.
class ApprovalExpiresBeforeSessionEnds(ValidationError):
    pass


# Todo: Move fields to separate module.
if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':

    class ProjectTitleField(webkit.ManipulatedField, webkit.CharField):

        def clean(self, value):
            value = super(ProjectTitleField, self).clean(value)
            if self.isProjectTitleUsed(value):
                message = "Project title is already being used by another project."
                raise webkit.ValidationError(message)
            return value

        def isProjectTitleUsed(self, title):
            domainObjects = self.manipulator.registry.projects.findDomainObjects(title=title)
            if self.manipulator.domainObject != None:
                if self.manipulator.domainObject in domainObjects:
                    domainObjects.remove(self.manipulator.domainObject)
            return bool(len(domainObjects))


    class ApprovalCodeField(webkit.ManipulatedField, webkit.CharField):

        def clean(self, value):
            value = super(ApprovalCodeField, self).clean(value)
            if self.isApprovalCodeUsed(value):
                message = "Approval code '%s' is already is use." % value
                raise webkit.ValidationError(message)
            return value

        def isApprovalCodeUsed(self, code):
            domainObjects = self.manipulator.registry.approvals.findDomainObjects(code=code)
            if self.manipulator.domainObject != None:
                if self.manipulator.domainObject in domainObjects:
                    domainObjects.remove(self.manipulator.domainObject)
            return bool(len(domainObjects))


    class AccountCodeField(webkit.ManipulatedField, webkit.CharField):

        def clean(self, value):
            value = super(AccountCodeField, self).clean(value)
            if self.isAccountCodeUsed(value):
                message = "Account code '%s' is already is use." % value
                raise webkit.ValidationError(message)
            return value

        def isAccountCodeUsed(self, code):
            domainObjects = self.manipulator.registry.accounts.findDomainObjects(code=code)
            if self.manipulator.domainObject != None:
                if self.manipulator.domainObject in domainObjects:
                    domainObjects.remove(self.manipulator.domainObject)
            return bool(len(domainObjects))


    class ApprovalField(ManipulatedField, ChoiceField):

        def clean(self, value):
            value = super(ApprovalField, self).clean(value)
            if value:
                self.assertApprovalValid(value)
            return value

        def assertApprovalValid(self, approvalKey):
            registry = self.manipulator.registry
            # Todo: Change to use given choices.
            if not approvalKey in registry.approvals:
                message = "Selected approval isn't in approvals register."
                raise ValidationError(message)
            approval = registry.approvals[approvalKey]
            project = None
            projectKey = self.manipulator.data['project']
            if projectKey in registry.projects:
                project = registry.projects[projectKey]
            # Check session approval against session project.
            if approval:
                # Check approval listed on project.
                if not project:
                    message = "No project to check approval."
                    raise ValidationError(message)
                elif not approval in project.approvals:
                    message = "Approval not for selected project."
                    raise ValidationError(message)
            settings = registry.settings['default']
            if project:
                # Check project leader named on approval.
                if settings.requireApprovedProjectLeader:
                    if not project.leader:
                        message = "Project has no leader."
                        raise ValidationError(message)
                    leader = project.leader
                    isLeaderNamedOnApproval = False
                    if leader not in approval.principalInvestigators.keys() \
                    and leader not in approval.additionalResearchers.keys():
                        message = "Project leader '%s' not associated with approval '%s'." % (
                            leader.getLabelValue(), approval.getLabelValue()
                        )
                        raise ValidationError(message)
            approvalNumberRemaining = approval.numberRemaining()
            if self.manipulator.domainObject == None:  # creating session
                # Check approval balance.
                if settings.requireEthicsApprovalBalance:
                    if approvalNumberRemaining <= 0:
                        message = "Selected approval is fully-used."
                        raise ValidationError(message)
            else:                          # updating session
                # Check approval balance.
                oldApproval = self.manipulator.domainObject.approval
                if settings.requireEthicsApprovalBalance:
                    if oldApproval != approval:  # changing approval
                        if approvalNumberRemaining <= 0:
                            message = "Selected approval is fully used."
                            raise ValidationError(message)
                    elif approvalNumberRemaining < 0:  # approval unchanged
                        message = "Selected approval is over-used."
                        raise ValidationError(message)
        
                # Check approval expires after session ends.
                if settings.requireEthicsApprovalInDate:
                    if not approval.expires:
                        message = "Ethics approval has no expires date."
                        # Todo: Rename exception.
                        raise ApprovalExpiresBeforeSessionEnds(message)
                    if approval.expires <= self.manipulator.domainObject.ends:
                        message = "Ethics approval expires before session ends."
                        raise ApprovalExpiresBeforeSessionEnds(message)
                # Todo: Check all_data['ends'] < approval.expires
                #  - session ends could be set beyond select approval expires?


    class VolunteerRealnameField(webkit.ManipulatedField, webkit.CharField):

        def clean(self, value):
            value = super(VolunteerRealnameField, self).clean(value)
            if self.isVolunteerRealnameUsed(value):
                message = "Volunteer '%s' is already registered." % value
                raise webkit.ValidationError(message)
            return value

        def isVolunteerRealnameUsed(self, realname):
            domainObjects = self.manipulator.registry.volunteers.findDomainObjects(realname=realname)
            if self.manipulator.domainObject != None:
                if self.manipulator.domainObject in domainObjects:
                    domainObjects.remove(self.manipulator.domainObject)
            return bool(len(domainObjects))


    class VolunteerPanelIdField(webkit.ManipulatedField, webkit.CharField):

        def clean(self, value):
            value = super(VolunteerPanelIdField, self).clean(value)
            if self.isVolunteerPanelIdUsed(value):
                message = "Volunteer '%s' is already registered." % value
                raise webkit.ValidationError(message)
            return value

        def isVolunteerPanelIdUsed(self, panelId):
            domainObjects = self.manipulator.registry.volunteers.findDomainObjects(panelId=panelId)
            if self.manipulator.domainObject != None:
                if self.manipulator.domainObject in domainObjects:
                    domainObjects.remove(self.manipulator.domainObject)
            return bool(len(domainObjects))


class SessionManipulator(HasManyManipulator):
    "Defines fields and field contraints for session manipulation."

    workingStartsHour = scanbooker.workingHours.start
    workingEndsHour = scanbooker.workingHours.end

    def listSortedOptions(self, domainObjectRegister):
        sortedList = domainObjectRegister.getSortedList()
        return self.listSelectOptions(sortedList)

    def listSelectOptions(self, domainObjects):
        return [('', '-- select option --')] + \
        [(i.getRegisterKeyValue(), i.getLabelValue()) for i in domainObjects]

    def listSortedMultipleOptions(self, domainObjectRegister):
        sortedList = domainObjectRegister.getSortedList()
        return self.listSelectMultipleOptions(sortedList)

    def listSelectMultipleOptions(self, domainObjects):
        return [(
            i.getRegisterKeyValue(), i.getLabelValue()
        ) for i in domainObjects]

    def isIntegerValue(self, field_data, all_data):
        try:
            int(field_data)
        except:
            message = "'%s' isn't an integer." % field_data
            raise ValidationError(message)

    def isLeaderValid(self, field_data, all_data):
        researchers = self.listProjectResearchers()
        if str(all_data['leader']) not in [str(r.id) for r in researchers]:
            message = "Leader '%s' is not valid option." % all_data['leader']
            raise ValidationError(message)

    def isApprovalValid(self, field_data, all_data):
        settings = self.registry.settings['default']
        approvalKey = field_data
        if not approvalKey in self.registry.approvals:
            message = "Selected approval isn't in approvals register."
            raise ValidationError(message)
        approval = self.registry.approvals[approvalKey]
        project = None
        projectKey = all_data['project']
        if projectKey in self.registry.projects:
            project = self.registry.projects[projectKey]
        # Check session approval against session project.
        if approval:
            # Check approval listed on project.
            if not project:
                message = "No project to check approval."
                raise ValidationError(message)
            elif not approval in project.approvals:
                message = "Approval not for selected project."
                raise ValidationError(message)
        if project:
            # Check project leader named on approval.
            if settings.requireApprovedProjectLeader:
                if not project.leader:
                    message = "Project has no leader."
                    raise ValidationError(message)
                leader = project.leader
                isLeaderNamedOnApproval = False
                if leader not in approval.principalInvestigators.keys() \
                and leader not in approval.additionalResearchers.keys():
                    message = "Project leader '%s' not on approval '%s'." % (
                        leader.getLabelValue(), approval.getLabelValue()
                    )
                    raise ValidationError(message)
        approvalNumberRemaining = approval.numberRemaining()
        if self.domainObject == None:  # creating session
            # Check approval balance.
            if settings.requireEthicsApprovalBalance:
                if approvalNumberRemaining <= 0:
                    message = "Selected approval is fully-used."
                    raise ValidationError(message)
        else:                          # updating session
            # Check approval balance.
            oldApproval = self.domainObject.approval
            if settings.requireEthicsApprovalBalance:
                if oldApproval != approval:  # changing approval
                    if approvalNumberRemaining <= 0:
                        message = "Selected approval is fully used."
                        raise ValidationError(message)
                elif approvalNumberRemaining < 0:  # approval unchanged
                    message = "Selected approval is over-used."
                    raise ValidationError(message)
    
            # Check approval expires after session ends.
            if settings.requireEthicsApprovalInDate:
                if not approval.expires:
                    message = "Ethics approval has no expires date."
                    raise ApprovalExpiresBeforeSessionEnds(message)
                if approval.expires <= self.domainObject.ends:
                    message = "Ethics approval expires before session ends."
                    raise ApprovalExpiresBeforeSessionEnds(message)
            # Todo: Check all_data['ends'] < approval.expires
            #  - session ends could be set beyond select approval expires?

    def isProjectValid(self, field_data, all_data):
        projectKey = all_data['project']
        if not projectKey in self.registry.projects:
            return
        project = self.registry.projects[projectKey]
        settings = self.registry.settings['default']
        if settings.requireTrainedProjectLeader:
            # Check project has a leader.
            if not project.leader:
                message = "Project has no leader."
                raise ValidationError(message)
            # Check project leader is trained.
            if not project.leader.isTrained():
                message = "Project leader '%s' is not trained." % (
                    project.leader.getLabelValue()
                )
                raise ValidationError(message)

    def endsAfterStarts(self, field_data, all_data):
        starts = mx.DateTime.Parser.DateTimeFromString(all_data['starts'])
        ends = mx.DateTime.Parser.DateTimeFromString(all_data['ends'])
        if not starts < ends:
            message = "Session must end after it starts."
            raise ValidationError(message)

    def endsSameDayStarts(self, field_data, all_data):
        starts = mx.DateTime.Parser.DateTimeFromString(all_data['starts'])
        ends = mx.DateTime.Parser.DateTimeFromString(all_data['ends'])
        if not starts.year == ends.year:
            message = "Session must start and end in same year."
            raise ValidationError(message)
        if not starts.month == ends.month:
            message = "Session must start and end in same month."
            raise ValidationError(message)
        if not starts.day == ends.day:
            message = "Session must start and end on same day."
            raise ValidationError(message)

    def isMinuteOnBlockEdge(self, field_data, all_data):
        dateTime = mx.DateTime.Parser.DateTimeFromString(field_data)
        blockEdges = [0, 15, 30, 45]
        if not dateTime.minute in blockEdges:
            message = "This field on minute that does not match any time block."
            raise ValidationError(message)

    def isSecondZero(self, field_data, all_data):
        dateTime = mx.DateTime.Parser.DateTimeFromString(field_data)
        if dateTime.second:
            message = "This field on different second from '00'."
            raise ValidationError(message)

    def isDuringWorkingHours(self, field_data, all_data):
        dateTime = mx.DateTime.Parser.DateTimeFromString(field_data)
        if dateTime.hour < self.workingStartsHour:
            message = "This field before working hours start."
            raise ValidationError(message)
        if dateTime.hour == self.workingEndsHour and dateTime.minute:
            message = "This field after working hours end."
            raise ValidationError(message)
        if dateTime.hour > self.workingEndsHour:
            message = "This field after working hours end."
            raise ValidationError(message)

    def noScheduleOverlap(self, field_data, all_data):
        starts = mx.DateTime.Parser.DateTimeFromString(all_data['starts'])
        ends = mx.DateTime.Parser.DateTimeFromString(all_data['ends'])
        scanner = self.registry.scanners[all_data['scanner']]
        sessions = self.registry.maintenanceSessions.findDomainObjects(
            scanner=scanner, __startsBefore__=ends, __endsAfter__=starts
        )
        sessions += self.registry.scanningSessions.findDomainObjects(
            scanner=scanner, __startsBefore__=ends, __endsAfter__=starts
        )
        if self.domainObject != None:
            otherSessions = []
            for session in sessions:
                if self.domainObject.id != session.id:
                    otherSessions.append(session)
        else:
            otherSessions = sessions
        if len(otherSessions):
            message = "Session overlaps with other sessions: "
            message +=", ".join(
                ["%s %s" % (s.typeNick, str(s.starts)) for s in otherSessions]
            )
            raise ValidationError(message)

    def listRegisteredScanners(self):
        return [('', '-- select option --')] + [(i.getRegisterKeyValue(), i.getLabelValue()) for i in self.registry.scanners]

    def listOrganisations(self):
        return self.listSortedOptions(self.registry.organisations)
    

class EarmarkedTimeManipulator(SessionManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                #'starts': DateTimeField(
                #    required=False,
                #),
                #'ends': DateTimeField(
                #    required=False,
                #),
                'sessionType': webkit.ChoiceField(
                    label='session type',
                    choices=self.listSessionTypes(),
                ),
                'comment': webkit.CharField(
                    required=False,
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields = (
                SelectField(
                    field_name="sessionType",
                    is_required=True,
                    choices=self.listSessionTypes(),
                    validator_list=[
                    ]
                ),
                TextField(
                    field_name="comment", 
                    is_required=False,
                    validator_list=[
                    ]
                ),
            )

    def listSessionTypes(self):
        return self.listSortedOptions(self.registry.sessionTypes)
    

class EarmarkedTimeCreateManipulator(EarmarkedTimeManipulator):
    pass


class EarmarkedTimeUpdateManipulator(EarmarkedTimeManipulator):
    pass


class MaintenanceSessionManipulator(SessionManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'comment': webkit.CharField(
                    required=False,
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields = (
                TextField(
                    field_name="comment", 
                    is_required=False,
                ),
            )


class MaintenanceSessionCreateManipulator(MaintenanceSessionManipulator):
    pass


class MaintenanceSessionUpdateManipulator(MaintenanceSessionManipulator):
    pass


class MethodsSessionManipulator(SessionManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'comment': webkit.CharField(
                    required=False,
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields = (
                TextField(
                    field_name="comment", 
                    is_required=False,
                ),
            )


class MethodsSessionCreateManipulator(MethodsSessionManipulator):
    pass


class MethodsSessionUpdateManipulator(MethodsSessionManipulator):
    pass


class DowntimeSessionManipulator(SessionManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'reason': webkit.CharField(
                    required=False,
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields = (
                TextField(
                    field_name="reason", 
                    is_required=False,
                    validator_list=[
                    ]
                ),
            )


class DowntimeSessionCreateManipulator(DowntimeSessionManipulator):
    pass


class DowntimeSessionUpdateManipulator(DowntimeSessionManipulator):
    pass


class ScanningSessionManipulator(SessionManipulator):

    def listProjects(self):
        activeStatus = self.registry.projectStatuses['Active']
        kwds = {}
        if (self.client 
            and hasattr(self.client, 'session')
            and self.client.session
            and self.client.session.person
            and self.client.session.person.researcher
            and self.client.session.person.role.name != 'Administrator'):
            activeProjects = []
            associations = self.client.session.person.researcher.projects
            for project in associations.keys():
                if project.status == activeStatus:
                    activeProjects.append(project)
        else:
            register = self.registry.projects
            activeProjects = register.findDomainObjects(status=activeStatus)
        return self.listSelectOptions(activeProjects)
    
    def listRegisteredProjects(self):
        return self.listSortedOptions(self.registry.projects)
        
    def listProjectApprovals(self):
        approvals = []
        if self.domainObject and self.domainObject.project:
            approvals = self.domainObject.project.approvals.keys()
        return self.listSelectOptions(approvals)

    def getLeaderOptions(self):
        return self.listSelectOptions(self.listProjectResearchers())

    def listProjectResearchers(self):
        researchers = []
        if self.domainObject and self.domainObject.project:
            project = self.domainObject.project
            if project.leader:
                researchers.append(project.leader)
            for researcher in project.researchers.keys():
                if researcher != project.leader:
                    researchers.append(researcher)
        return researchers

    def listRegisteredApprovals(self):
        return self.listSortedOptions(self.registry.approvals)
    
    def listRegisteredScanningSessionTypes(self):
        return self.listSortedOptions(self.registry.scanningSessionTypes)

    def listRegisteredVolunteerBookingMethods(self):
        return self.listSortedOptions(self.registry.volunteerBookingMethods)

    def listRegisteredVolunteers(self):
        return self.listSortedOptions(self.registry.volunteers)

    def listRegisteredResearchers(self):
        return self.listSortedOptions(self.registry.researchers)

    def listRegisteredRadiographers(self):
        return self.listSortedOptions(self.registry.radiographers)

    def listRegisteredOutcomes(self):
        return self.listSortedOptions(self.registry.scanningSessionOutcomes)

    def fixSessionLeader(self, data):
        project = None
        if 'project' in data and data['project']:
            projectKey = data['project']
            if projectKey in self.registry.projects:
                project = self.registry.projects[projectKey]
        if not project:
            return
        # If project changed, drop session leader.
        if self.domainObject and self.domainObject.project != project:
            # Changing project....
            data['leader'] = None  # NB Setting '' here.
            #if project.leader:
            #    data['leader'] = project.leader.id
            #else:


class ScanningSessionCreateManipulator(ScanningSessionManipulator):

    def fromDateStartEnd(self, data):
        date = data['date']
        if type(date) == str:
            day, month, year = date.split('-')
            day, month, year = int(day), int(month), int(year)
        else:
            day, month, year = date.day, date.month, date.year
        start = data['start']
        if type(start) == str:
            hour, min = start.split(':')
            hour, min = int(hour), int(min)
        else:
            hour, min = start.hour, start.minute
        starts = mx.DateTime.DateTime(year, month, day, hour, min, 0)
        end = data['end']
        if type(end) == str:
            hour, min = end.split(':')
            hour, min = int(hour), int(min)
        else:
            hour, min = end.hour, end.minute
        ends = mx.DateTime.DateTime(year, month, day, hour, min, 0)
        data.pop('start')
        data.pop('end')
        data.pop('date')
        data['starts'] = starts.strftime('%H:%M %d-%m-%Y')
        data['ends'] = ends.strftime('%H:%M %d-%m-%Y')

    def create(self, data):
        self.fromDateStartEnd(data)
        self.fixSessionLeader(data)
        super(ScanningSessionCreateManipulator, self).create(data)

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'start': webkit.TimeField(
                    required=True,
                    label='start time',
                ),
                'end': webkit.TimeField(
                    required=True,
                    label='end time',
                ),
                'date': webkit.DateField(
                    required=True,
                    label='date of session',
                ),
                'scanId': webkit.CharField(
                    required=False,
                    label='scan ID',
                ),
                'project': webkit.ChoiceField(
                    required=False,
                    choices=self.listProjects(),
                ),
                'outcome': webkit.ChoiceField(
                    required=False,
                    choices=self.listRegisteredOutcomes(),
                ),
                'approval': ApprovalField(
                    required=False,
                    choices=self.listRegisteredApprovals(),
                    manipulator=self,
                ),
                'volunteer': webkit.ChoiceField(
                    required=False,
                    choices=self.listRegisteredVolunteers(),
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = TimeField(
                field_name='start',
                is_required=True,
            )
            field.field_title = 'start time'
            self.fields.append(field)

            field = TimeField(
                field_name='end',
                is_required=True,
            )
            field.field_title = 'end time'
            self.fields.append(field)

            field = RDateField(
                field_name='date',
                is_required=True,
            )
            field.field_title = 'date of session'
            self.fields.append(field)

            field = TextField(
                field_name="scanId", 
                is_required=False,
            )
            field.field_title = 'scan ID'
            self.fields.append(field)

            field = SelectField(
                field_name="project",
                is_required=False,
                choices=self.listProjects(),
                validator_list=[
                    self.isProjectValid,
                ]
            )
            field.field_title = 'project'
            self.fields.append(field)

            field = SelectField(
                field_name="outcome",
                is_required=False,
                choices=self.listRegisteredOutcomes(),
            )
            field.field_title = 'outcome'
            self.fields.append(field)

            field = SelectField(
                field_name="approval",
                is_required=False,
                choices=self.listRegisteredApprovals(),
                validator_list=[
                    self.isApprovalValid,
                ]
            )
            field.field_title = 'approval'
            self.fields.append(field)
            
            field = SelectField(
                field_name="volunteer",
                is_required=False,
                choices=self.listRegisteredVolunteers(),
            )
            field.field_title = 'volunteer'
            self.fields.append(field)



class ScanningSessionUpdateManipulator(ScanningSessionManipulator):

    def update(self, data):
        self.fixSessionLeader(data)
        super(ScanningSessionUpdateManipulator, self).update(data)

    def buildSessionLeaderField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'leader': webkit.ChoiceField(
                    required=False,
                    choices=self.getLeaderOptions(),
                    label='leader',
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = SelectField(
                field_name="leader",
                is_required=False,
                choices=self.getLeaderOptions(),
                validator_list=[
                    self.isLeaderValid,
                ]
            )
            field.field_title = 'session leader'
            self.fields.append(field)

    def buildProjectField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'project': webkit.ChoiceField(
                    required=False,
                    choices=self.listProjects(),
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = SelectField(
                field_name="project",
                is_required=False,
                choices=self.listProjects(),
                validator_list=[
                    self.isProjectValid,
                ]
            )
            field.field_title = 'project'
            self.fields.append(field)

    def buildApprovalField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'approval': ApprovalField(
                    required=False,
                    choices=self.listProjectApprovals(),
                    manipulator=self,
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = SelectField(
                field_name="approval",
                is_required=False,
                choices=self.listProjectApprovals(),
                validator_list=[
                    self.isApprovalValid,
                ]
            )
            field.field_title = 'approval'
            self.fields.append(field)

    def buildBookingOwnVolunteersField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'bookingOwnVolunteers': webkit.BooleanField(
                    label='researcher books volunteers',
                    required=False,
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = CheckboxField(
                field_name="bookingOwnVolunteers",
            )
            field.field_title = 'researcher books volunteers'
            self.fields.append(field)

    def buildVolunteerField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'volunteer': webkit.ChoiceField(
                    required=False,
                    choices=self.listRegisteredVolunteers(),
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = SelectField(
                field_name="volunteer",
                is_required=False,
                choices=self.listRegisteredVolunteers(),
            )
            field.field_title = 'volunteer'
            self.fields.append(field)

    def buildBackupVolunteerField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'backupVolunteer': webkit.ChoiceField(
                    required=False,
                    choices=self.listRegisteredVolunteers(),
                    label='backup volunteer',
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = SelectField(
                field_name="backupVolunteer",
                is_required=False,
                choices=self.listRegisteredVolunteers(),
            )
            field.field_title = 'backup volunteer'
            self.fields.append(field)

    def buildScanIdField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'scanId': webkit.CharField(
                    required=False,
                    label='scan ID',
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = TextField(
                field_name="scanId", 
                is_required=False,
            )
            field.field_title = 'scan ID'
            self.fields.append(field)

    def buildOutcomeField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'outcome': webkit.ChoiceField(
                    required=False,
                    choices=self.listRegisteredOutcomes(),
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = SelectField(
                field_name="outcome",
                is_required=False,
                choices=self.listRegisteredOutcomes(),
            )
            field.field_title = 'outcome'
            self.fields.append(field)

    def buildReplacementField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'replacement': webkit.BooleanField(
                    label='replacement session',
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = CheckboxField(
                field_name="replacement",
            )
            field.field_title = 'replacement session'
            self.fields.append(field)

    def buildVolunteerBookingMethodField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'volunteerBookingMethod': webkit.ChoiceField(
                    required=False,
                    choices=self.listRegisteredVolunteerBookingMethods(),
                    label='volunteer booking method',
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = SelectField(
                field_name="volunteerBookingMethod",
                is_required=False,
                choices=self.listRegisteredVolunteerBookingMethods(),
            )
            field.field_title = 'volunteer booking method'
            self.fields.append(field)

    def buildBuddy1Field(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'buddy1': webkit.ChoiceField(
                    required=False,
                    choices=self.listRegisteredResearchers(),
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = SelectField(
                field_name="buddy1",
                is_required=False,
                choices=self.listRegisteredResearchers(),
            )
            field.field_title = 'buddy1'
            self.fields.append(field)

    def buildBuddy2Field(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'buddy2': webkit.ChoiceField(
                    required=False,
                    choices=self.listRegisteredResearchers(),
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = SelectField(
                field_name="buddy2",
                is_required=False,
                choices=self.listRegisteredResearchers(),
            )
            field.field_title = 'buddy2'
            self.fields.append(field)

    def buildNotesField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'notes': webkit.CharField(
                    required=False,
                    widget=webkit.widgets.Textarea()
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = LargeTextField(field_name="notes", is_required=False)
            field.field_title = 'notes'
            self.fields.append(field)

    def buildEthicsUsedField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'ethicsUsed': webkit.BooleanField(
                    label='ethics was used',
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = CheckboxField(field_name="ethicsUsed")
            field.field_title = 'ethics was used'
            self.fields.append(field)

    def buildVolunteerUsedField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'volunteerUsed': webkit.BooleanField(
                    label='volunteer was used',
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = CheckboxField(field_name="volunteerUsed")
            field.field_title = 'volunteer was used'
            self.fields.append(field)

    def buildUsedMinutesField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'usedMinutes': webkit.IntegerField(
                    label='minutes (used)',
                    required=False,
                    min_value=0,
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = TextField(
                field_name="usedMinutes", 
                is_required=False,
                validator_list=[
                    self.isIntegerValue,
                ]
            )
            field.field_title = 'minutes (used)'
            self.fields.append(field)

    def buildScanningSessionTypeField(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'scanningSessionType': webkit.ChoiceField(
                    required=False,
                    choices=self.listRegisteredScanningSessionTypes(),
                    label='scan type',
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = SelectField(
                field_name="scanningSessionType",
                is_required=False,
                choices=self.listRegisteredScanningSessionTypes(),
            )
            field.field_title = 'scan type'
            self.fields.append(field)

    def buildFields(self):
        if hasattr(self.client, 'isSlaveView') and self.client.isSlaveView():
            self.buildProjectField()
            if not self.domainObject.project:
                return
            self.buildSessionLeaderField()
            self.buildBookingOwnVolunteersField()
            self.buildApprovalField()
            if not self.domainObject.approval:
                return
            self.buildVolunteerField()
            self.buildScanIdField()
            self.buildOutcomeField()
        else:
            self.buildProjectField()
            if not self.domainObject.project:
                self.buildScanningSessionTypeField()
                self.buildNotesField()
                return
            self.buildSessionLeaderField()
            self.buildScanningSessionTypeField()
            self.buildVolunteerBookingMethodField()
            self.buildReplacementField()
            self.buildBookingOwnVolunteersField()
            self.buildBuddy1Field()
            self.buildBuddy2Field()
            self.buildApprovalField()
            if not self.domainObject.approval:
                self.buildNotesField()
                return
            self.buildVolunteerField()
            self.buildEthicsUsedField()
            self.buildVolunteerUsedField()
            self.buildNotesField()
            self.buildScanIdField()
            self.buildUsedMinutesField()
            self.buildOutcomeField()


class TrainingSessionManipulator(SessionManipulator):

    def getTypeOptions(self):
        return self.listSortedOptions(self.registry.trainingSessionTypes)

    def getResearcherOptions(self):
        return self.listSortedMultipleOptions(self.registry.researchers)

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'researchers': webkit.MultipleChoiceField(
                    required=False,
                    label='attendees',
                    choices=self.getResearcherOptions(),
                ),
                'date': webkit.DateField(
                    required=True,
                    label='date of session',
                    help_text='Format: DD-MM-YYYY (e.g. 31-12-2010)',
                ),
                'start': webkit.TimeField(
                    required=True,
                    label='start time',
                    help_text='Format: HH-MM (e.g. 14:45)',
                ),
                'end': webkit.TimeField(
                    required=True,
                    label='end time',
                    help_text='Format: HH-MM (e.g. 14:45)',
                ),
                'type': webkit.ChoiceField(
                    required=True,
                    label='type of session',
                    choices=self.getTypeOptions(),
                ),
                'capacity': webkit.IntegerField(
                    label='number of places',
                    required=True,
                    initial=0,
                    min_value=0,
                ),
                'location': webkit.CharField(
                    required=False,
                ),
                'presenter': webkit.CharField(
                    required=False,
                ),
                'comment': webkit.CharField(
                    required=False,
                ),
                'notes': webkit.CharField(
                    required=False,
                    widget=webkit.widgets.Textarea()
                ),
 
            })
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = SelectMultipleField(
                field_name='researchers',
                is_required=False,
                choices=self.getResearcherOptions(),
                size=self.sizeSelectMultiple,
            )
            field.field_title = 'attendees'
            self.fields.append(field)

            field = RDateField(
                field_name='date',
                is_required=True,
            )
            field.field_title = 'date of session'
            self.fields.append(field)

            field = TimeField(
                field_name='start',
                is_required=True,
            )
            field.field_title = 'start time'
            self.fields.append(field)

            field = TimeField(
                field_name='end',
                is_required=True,
            )
            field.field_title = 'end time'
            self.fields.append(field)

            field = SelectField(
                field_name='type',
                is_required=True,
                choices=self.getTypeOptions(),
            )
            field.field_title = 'type of session'
            self.fields.append(field)

            field = PositiveIntegerField(
                field_name='capacity',
                is_required=False,
            )
            field.field_title = 'places'
            self.fields.append(field)

            field = TextField(
                field_name='location',
                is_required=False,
            )
            field.field_title = 'location'
            self.fields.append(field)

            field = TextField(
                field_name='presenter',
                is_required=False,
            )
            field.field_title = 'presenter'
            self.fields.append(field)

            field = TextField(
                field_name='comment',
                is_required=False,
            )
            field.field_title = 'comment'
            self.fields.append(field)

            field = LargeTextField(
                field_name='notes',
                is_required=False,
            )
            field.field_title = 'notes'
            self.fields.append(field)

    def fromDateStartEnd(self, data):
        date = data['date']
        if type(date) in [str, unicode]:
            day, month, year = date.split('-')
            day, month, year = int(day), int(month), int(year)
        else:
            day, month, year = date.day, date.month, date.year
        start = data['start']
        if type(start) in [str, unicode]:
            hour, min = start.split(':')
            hour, min = int(hour), int(min)
        else:
            hour, min = start.hour, start.minute
        starts = mx.DateTime.DateTime(year, month, day, hour, min, 0)
        end = data['end']
        if type(end) in [str, unicode]:
            hour, min = end.split(':')
            hour, min = int(hour), int(min)
        else:
            hour, min = end.hour, end.minute
        ends = mx.DateTime.DateTime(year, month, day, hour, min, 0)
        data.pop('start')
        data.pop('end')
        data.pop('date')
        data['starts'] = starts.strftime('%H:%M %d-%m-%Y')
        data['ends'] = ends.strftime('%H:%M %d-%m-%Y')

    def create(self, data):
        self.fromDateStartEnd(data)
        super(TrainingSessionManipulator, self).create(data)
        m = self.domainObject.meta.attributeNames['starts']
        m.setAttributeFromMultiValueDict(self.domainObject, data)
        m = self.domainObject.meta.attributeNames['ends']
        m.setAttributeFromMultiValueDict(self.domainObject, data)
        self.domainObject.save()

    def update(self, data):
        self.fromDateStartEnd(data)
        super(TrainingSessionManipulator, self).update(data)
        m = self.domainObject.meta.attributeNames['starts']
        m.setAttributeFromMultiValueDict(self.domainObject, data)
        m = self.domainObject.meta.attributeNames['ends']
        m.setAttributeFromMultiValueDict(self.domainObject, data)
        self.domainObject.save()


class TrainingSessionCreateManipulator(TrainingSessionManipulator):
    pass


class TrainingSessionUpdateManipulator(TrainingSessionManipulator):

    def getUpdateParams(self):  # Todo: getInitialUpdateParams
        prms = super(TrainingSessionUpdateManipulator, self).getUpdateParams()
        starts = prms['starts']
        ends = prms['ends']
        if starts and ends:
            starts = starts.split(' ')
            if len(starts) >= 2:
                prms['date'] = starts[1]
                prms['start'] = starts[0]
            ends = ends.split(' ')
            if len(ends) >= 2:
                prms['end'] = ends[0]
        return prms


class SessionTimeManipulator(SessionManipulator):

    def buildFields(self):
        self.fields = (
            DatetimeField(
                field_name="starts", 
                is_required=True,
                validator_list=[
                    self.isDuringWorkingHours,
                    self.isMinuteOnBlockEdge,
                    self.isSecondZero,
                    self.noScheduleOverlap,
                ]
            ),
            DatetimeField(
                field_name="ends", 
                is_required=True,
                validator_list=[
                    self.endsAfterStarts,
                    self.endsSameDayStarts,
                    self.isDuringWorkingHours,
                    self.isMinuteOnBlockEdge,
                    self.isSecondZero,
                    self.noScheduleOverlap,
                ]
            ),
        )


class PersonManipulator(DomainObjectManipulator):

    def isPersonName(self, field_data, all_data):
        pattern = re.compile('^%s$' % scanbooker.regexps.personName)
        if not pattern.match(field_data):
            msg = "This field can only contain alphanumerics, "
            msg += "underscores, hyphens, and dots."
            raise ValidationError(msg)

    def isReservedPersonName(self, field_data, all_data):
        pattern = re.compile('^%s$' % scanbooker.regexps.reservedPersonName)
        if pattern.match(field_data):
            msg = "This field is reserved and can not be registered."
            raise ValidationError(msg)

    def isAvailablePersonName(self, field_data, all_data):
        command = scanbooker.command.AllPersonRead(field_data)
        try:
            command.execute()
        except KforgeCommandError:
            pass
        else:
            message = "Login name is already being used by another person."
            raise ValidationError(message)

    def isMatchingPassword(self, field_data, all_data):
        password = all_data['password']
        passwordconfirmation = all_data['passwordconfirmation']
        if not (password == passwordconfirmation):
            raise ValidationError("Passwords do not match.")

    def isMatchingEmail(self, field_data, all_data):
        email = all_data['email']
        emailconfirmation = all_data['emailconfirmation']
        if not (email == emailconfirmation):
            raise ValidationError("Emails do not match.")

    def isCaptchaCorrect(self, field_data, all_data):
        if self.dictionary['captcha.enable']:
            word = all_data['captcha']
            hash = all_data['captchahash']
            if not word and not hash:
                raise ValidationError("Captcha failure.")
            read = scanbooker.command.CaptchaRead(hash)
            try:
                read.execute()
            except KforgeCommandError, inst: 
                raise ValidationError("Captcha failure.")
            captcha = read.object
            if not captcha.checkWord(word):
                raise ValidationError("Captcha failure.")

    def listGroups(self):
        return self.listSortedOptions(self.registry.groups)

    def listRoles(self):
        return self.listSortedOptions(self.registry.roles)

    def listResearchers(self):
        return self.listSortedOptions(self.registry.researchers)

    def listSortedOptions(self, domainObjectRegister):
        sortedList = domainObjectRegister.getSortedList()
        return self.listSelectOptions(sortedList)

    def listSelectOptions(self, domainObjects):
        return [('', '-- select option --')] + [(i.getRegisterKeyValue(), i.getLabelValue()) for i in domainObjects]


class PrincipalInvestigatorCreateManipulator(PersonManipulator):

    def buildFields(self):
        self.fields.append(
            TextField(
                field_name="name", 
                is_required=True, 
                validator_list=[
                    self.isPersonName, 
                    self.isReservedPersonName, 
                    self.isAvailablePersonName, 
                    self.isTwoCharsMin,
                    self.isTwentyCharsMax,
                ]
            )
        )
        self.fields.append(
            PasswordField(
                field_name="password", 
                is_required=True, 
                validator_list=[
                    self.isFourCharsMin,
                ]
            )
        )
        self.fields.append(
            PasswordField(
                field_name="passwordconfirmation", 
                is_required=True, 
                validator_list=[
                    self.isMatchingPassword
                ]
            )
        )
        self.fields.append(
            TextField(
                field_name="fullname", 
                is_required=True
            )
        )
        self.fields.append(
            EmailField(
                field_name="email", 
                is_required=True
            )
        )
        self.fields.append(
            EmailField(
                field_name="emailconfirmation", 
                is_required=True, 
                validator_list=[
                    self.isMatchingEmail
                ]
            ) 
        )
        if self.dictionary['captcha.enable']:
            self.fields.append(
                TextField(
                    field_name="captcha", 
                    is_required=isCaptchaEnabled, 
                    validator_list=[
                        self.isCaptchaCorrect
                    ]
                ) 
            )
            self.fields.append(
                HiddenField(
                    field_name="captchahash", 
                    is_required=False,
                )   
            )

# Caution: bad name; for "requested group role", not for Researcher object.
class ResearcherCreateManipulator(PersonManipulator): 

    def buildFields(self):
        self.fields.append(
            SelectField(
                field_name="group", 
                is_required=True,
                choices=self.listGroups(),
            ),
        )
        self.fields.append(
            TextField(
                field_name="name", 
                is_required=True, 
                validator_list=[
                    self.isPersonName, 
                    self.isReservedPersonName, 
                    self.isAvailablePersonName, 
                    self.isTwoCharsMin,
                    self.isTwentyCharsMax,
                ]
            )
        )
        self.fields.append(
            PasswordField(
                field_name="password", 
                is_required=True, 
                validator_list=[
                    self.isFourCharsMin,
                ]
            )
        )
        self.fields.append(
            PasswordField(
                field_name="passwordconfirmation", 
                is_required=True, 
                validator_list=[
                    self.isMatchingPassword
                ]
            )
        )
        self.fields.append(
            TextField(
                field_name="fullname", 
                is_required=True
            )
        )
        self.fields.append(
            EmailField(
                field_name="email", 
                is_required=True
            )
        )
        self.fields.append(
            EmailField(
                field_name="emailconfirmation", 
                is_required=True, 
                validator_list=[
                    self.isMatchingEmail
                ]
            ) 
        )
        if self.dictionary['captcha.enable']:
            self.fields.append(
                TextField(
                    field_name="captcha", 
                    is_required=isCaptchaEnabled, 
                    validator_list=[
                        self.isCaptchaCorrect
                    ]
                ) 
            )
            self.fields.append(
                HiddenField(
                    field_name="captchahash", 
                    is_required=False,
                )   
            )

class PersonCreateManipulator(PersonManipulator):

    def buildFields(self):
        self.fields.append(
            TextField(
                field_name="fullname", 
                is_required=True
            )
        )
        self.fields.append(
            EmailField(
                field_name="email", 
                is_required=True
            )
        )
        self.fields.append(
            EmailField(
                field_name="emailconfirmation", 
                is_required=True, 
                validator_list=[
                    self.isMatchingEmail
                ]
            ) 
        )
        self.fields.append(
            TextField(
                field_name="name", 
                is_required=True, 
                validator_list=[
                    self.isPersonName, 
                    self.isReservedPersonName, 
                    self.isAvailablePersonName, 
                    self.isTwoCharsMin,
                    self.isTwentyCharsMax,
                ]
            )
        )
        self.fields.append(
            PasswordField(
                field_name="password", 
                is_required=True, 
                validator_list=[
                    self.isFourCharsMin,
                ]
            )
        )
        self.fields.append(
            PasswordField(
                field_name="passwordconfirmation", 
                is_required=True, 
                validator_list=[
                    self.isMatchingPassword
                ]
            )
        )
        self.fields.append(
            RadioSelectField(
                field_name="requestedRole", 
                is_required=True,
                choices=[
                   ('Researcher', 'Researcher'),
                   ('PrincipalInvestigator', 'Principal Investigator'),
                ],
            ),
        )
        self.fields.append(
            SelectField(
                field_name="requestedGroup", 
                is_required=False,
                choices=self.listGroups(),
            ),
        )
        self.fields.append(
            FileUploadField(
                field_name="safetyTrainingCertificate", 
                is_required=False,
            )   
        )
        if self.dictionary['captcha.enable']:
            self.fields.append(
                TextField(
                    field_name="captcha", 
                    is_required=isCaptchaEnabled, 
                    validator_list=[
                        self.isCaptchaCorrect
                    ]
                ) 
            )
            self.fields.append(
                HiddenField(
                    field_name="captchahash", 
                    is_required=False,
                )   
            )

class PersonUpdateManipulator(PersonManipulator):

    def buildFields(self):
        self.fields.append(
            PasswordField(
                field_name="password", 
                is_required=False, 
                validator_list=[
                    self.isFourCharsMin,
                ]
            )
        )
        self.fields.append(
            PasswordField(
                field_name="passwordconfirmation", 
                is_required=False, 
                validator_list=[
                    self.isMatchingPassword
                ]
            )
        )
        self.fields.append(
            TextField(
                field_name="fullname", 
                is_required=True
            )
        )
        self.fields.append(
            EmailField(
                field_name="email", 
                is_required=False
            )
        )
        self.fields.append(
            FileUploadField(
                field_name="safetyTrainingCertificate", 
                is_required=False,
            )   
        )
    

class PersonApproveManipulator(PersonUpdateManipulator):

    def buildFields(self):
        PersonUpdateManipulator.buildFields(self)
        self.fields.append(
            SelectField(
                field_name="requestedRole",
                is_required=True,
                choices=self.listRoles(),
            ),
        )
        self.fields.append(
            SelectField(
                field_name="requestedGroup", 
                is_required=False,
                choices=self.listGroups(),
            ),
        )
        self.fields.append(
            SelectField(
                field_name="role",
                is_required=True,
                choices=self.listRoles(),
            ),
        )


class PersonUpdateManipulatorAdmin(PersonUpdateManipulator):

    def buildFields(self):
        PersonUpdateManipulator.buildFields(self)
        self.fields.append(
            SelectField(
                field_name="role",
                is_required=True,
                choices=self.listRoles(),
            ),
        )
        self.fields.append(
            SelectField(
                field_name="researcher",
                is_required=False,
                choices=self.listResearchers(),
            ),
        )

class AccountManipulator(DomainObjectManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'code': AccountCodeField(
                    manipulator=self,
                ),
                'comment': webkit.CharField(
                    required=False,
                ),
                #'projects': MultipleChoiceField(
                #    required=False,
                #    choices=self.listProjects(),
                #),
                'researchers': MultipleChoiceField(
                    required=False,
                    choices=self.listResearchers(),
                ),
                'organisations': MultipleChoiceField(
                    required=False,
                    choices=self.listOrganisations(),
                ),
                'notes': webkit.CharField(
                    required=False,
                    widget=webkit.widgets.Textarea()
                ),
            })
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = TextField(
                field_name="code", 
                is_required=True,
                validator_list=[
                    self.isAccountCodeUnique,
                ]
            )
            self.fields.append(field)
            
            field = TextField(
                field_name="comment",
                is_required=False,
            )
            field.field_title = 'comment'
            self.fields.append(field)

            # For Lucille.
            #field.field_title = 'QQR code'
            #self.fields.append(field)
            #
            #field = TextField(
            #    field_name="wbsCode", 
            #    is_required=False,
            #    validator_list=[
            #        #self.isAccountLongCodeUnique,
            #    ]
            #)
            #field.field_title = 'WBS code'
            #self.fields.append(field)
            #field = TextField(
            #    field_name="wbsCode", 
            #    is_required=False,
            #    validator_list=[
            #        #self.isAccountLongCodeUnique,
            #    ]
            #)
            #field.field_title = 'WBS code'
            #self.fields.append(field)
            
            field = SelectMultipleField(
                field_name="researchers",
                is_required=False,
                choices=self.listResearchers(),
                size=self.sizeSelectMultiple,
            )
            field.field_title = 'researchers'
            self.fields.append(field)

            field = SelectMultipleField(
                field_name="organisations",
                is_required=False,
                choices=self.listOrganisations(),
                size=self.sizeSelectMultiple,
            )
            field.field_title = 'organisations'
            self.fields.append(field)

            field = LargeTextField(
                field_name="notes",
                is_required=False,
            )
            field.field_title = 'notes'
            self.fields.append(field)

    def listProjects(self):
        return self.listSortedMultipleOptions(self.registry.projects)

    def listResearchers(self):
        return self.listSortedMultipleOptions(self.registry.researchers)

    def listOrganisations(self):
        return self.listSortedMultipleOptions(self.registry.organisations)

    def listSortedMultipleOptions(self, domainObjectRegister):
        sortedList = domainObjectRegister.getSortedList()
        return self.listSelectMultipleOptions(sortedList)

    def listSelectMultipleOptions(self, domainObjects):
        return [(
            i.getRegisterKeyValue(), i.getLabelValue()
        ) for i in domainObjects]

    def isAccountCodeUnique(self, field_data, all_data):
        new_code = field_data
        l = self.registry.accounts.findDomainObjects(code=new_code)
        # For Lucille.
        #l = self.registry.accounts.findDomainObjects(qqrCode=new_code)
        if self.domainObject != None:
            if self.domainObject in l:
                l.remove(self.domainObject)
        if len(l):
            message = "Account code '%s' is already in use." % new_code
            raise ValidationError(message)

    def isAccountLongCodeUnique(self, field_data, all_data):
        new_code = field_data
        l = self.registry.accounts.findDomainObjects(wbsCode=new_code)
        if self.domainObject != None:
            if self.domainObject in l:
                l.remove(self.domainObject)
        if len(l):
            message = "WBS code '%s' is already in use." % new_code
            raise ValidationError(message)


class ApprovalManipulator(DomainObjectManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'code': ApprovalCodeField(
                    manipulator=self,
                ),
                'description': webkit.CharField(
                    required=False,
                ),
                'principalInvestigators': webkit.MultipleChoiceField(
                    label='principal investigators',
                    required=False,
                    choices=self.listResearchers(),
                ),
                'additionalResearchers': webkit.MultipleChoiceField(
                    label='additional researchers',
                    required=False,
                    choices=self.listResearchers(),
                ),
                'numberAllocated': webkit.IntegerField(
                    label='number allocated',
                    required=False,
                ),
                'numberUsedAdjustment': webkit.IntegerField(
                    label='allocation excluded',
                    required=False,
                ),
                'expires': webkit.DateField(
                    required=False,
                ),
                'notes': webkit.CharField(
                    required=False,
                    widget=webkit.widgets.Textarea()
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = TextField(
                field_name="code", 
                is_required=True,
                validator_list=[
                    self.isApprovalCodeUnique,
                ]
            )
            field.field_title = 'code'
            self.fields.append(field)

            field = TextField(
                field_name="description", 
                is_required=False,
            )
            field.field_title = 'description'
            self.fields.append(field)

            field = SelectMultipleField(
                field_name="principalInvestigators",
                is_required=False,
                choices=self.listResearchers(),
                size=self.sizeSelectMultiple,
            )
            field.field_title = 'principal investigators'
            self.fields.append(field)

            field = SelectMultipleField(
                field_name="additionalResearchers",
                is_required=False,
                choices=self.listResearchers(),
                size=self.sizeSelectMultiple,
            )
            field.field_title = 'additional researchers'
            self.fields.append(field)

            field = IntegerField(
                field_name="numberAllocated",
                is_required=False,
            )
            field.field_title = 'number allocated'
            self.fields.append(field)

            field = IntegerField(
                field_name="numberUsedAdjustment",
                is_required=False,
            )
            field.field_title = 'number used adjustment'
            self.fields.append(field)

            field = RDateField(
                field_name="expires",
                is_required=False,
            )
            field.field_title = 'expires'
            self.fields.append(field)

            field = LargeTextField(
                field_name="notes",
                is_required=False,
            )
            field.field_title = 'notes'
            self.fields.append(field)

    def listResearchers(self):
        return self.listSortedMultipleOptions(self.registry.researchers)

    def listProjects(self):
        return self.listSortedMultipleOptions(self.registry.projects)

    def listSortedMultipleOptions(self, domainObjectRegister):
        sortedList = domainObjectRegister.getSortedList()
        return self.listSelectMultipleOptions(sortedList)

    def listSelectOptions(self, domainObjects):
        return [('', '-- select option --')] + [(i.getRegisterKeyValue(), i.getLabelValue()) for i in domainObjects]

    def listSelectMultipleOptions(self, domainObjects):
        return [(
            i.getRegisterKeyValue(), i.getLabelValue()
        ) for i in domainObjects]

    def isApprovalCodeUnique(self, field_data, all_data):
        new_code = field_data
        l = self.registry.approvals.findDomainObjects(code=new_code)
        if self.domainObject != None:
            if self.domainObject in l:
                l.remove(self.domainObject)
        if len(l):
            message = "Approval code '%s' is already in use." % new_code
            raise ValidationError(message)


class ProjectManipulator(DomainObjectManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'title': ProjectTitleField(
                    manipulator=self,
                ),
                'nickname': CharField(
                    required=False,
                ),
                'leader': ChoiceField(
                    required=False,
                    choices=self.listSortedOptions(self.registry.researchers),
                ),
                'account': ChoiceField(
                    required=False,
                    choices=self.listSortedOptions(self.registry.accounts),
                    label='cost account',
                ),
                'researchers': MultipleChoiceField(
                    required=False,
                    choices=self.listSortedOptions(self.registry.researchers),
                ),
                'approvals': MultipleChoiceField(
                    required=False,
                    choices=self.listSortedOptions(self.registry.approvals),
                ),
                'funding': ChoiceField(
                    required=False,
                    choices=self.listSortedOptions(self.registry.fundingStatuses),
                ),
                'status': ChoiceField(
                    required=False,
                    choices=self.listSortedOptions(self.registry.projectStatuses),
                ),
                'outcome': ChoiceField(
                    required=False,
                    choices=self.listSortedOptions(self.registry.projectOutcomes),
                ),
                'preparationMinutes': IntegerField(
                    required=False,
                    min_value=0,
                    label='preparation minutes',
                ),
                'volunteerBookingMethod': ChoiceField(
                    required=False,
                    choices=self.listSortedOptions(self.registry.volunteerBookingMethods),
                    label='volunteer booking method',
                ),
                'IIGPresentation': DateField(
                    required=False,
                    label='date of presentation',
                ),
                'IMCApproval': DateField(
                    required=False,
                    label='date of approval',
                ),
                'numberSubjects': IntegerField(
                    required=False,
                    label='number of subjects',
                ),
                'numberPilots': IntegerField(
                    required=False,
                    label='number of pilots',
                ),
                'slotMinutes': IntegerField(
                    required=False,
                    label='minutes per slot',
                ),
                'volunteerType': ChoiceField(
                    required=False,
                    choices=self.listSortedOptions(self.registry.volunteerTypes),
                    label='type of volunteer',
                ),
                'startDate': DateField(
                    required=False,
                    label='start date',
                ),
                'completionDate': DateField(
                    required=False,
                    label='completion date',
                ),
                'notes': CharField(
                    required=False,
                    widget=webkit.widgets.Textarea()
                ),
            })
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = TextField(
                field_name="title", 
                is_required=True,
                validator_list=[
                    self.isProjectTitleUnique,
                ]
            )
            field.field_title = 'project title'
            self.fields.append(field)

            field = TextField(
                field_name="nickname", 
                is_required=False,
            )
            field.field_title = 'nickname'
            self.fields.append(field)

            field = SelectField(
                field_name="leader",
                is_required=False,
                choices=self.listSortedOptions(self.registry.researchers),
            )
            field.field_title = 'leader'
            self.fields.append(field)

            field = SelectField(
                field_name="account",
                is_required=False,
                choices=self.listSortedOptions(self.registry.accounts),
            )
            field.field_title = 'cost account'
            self.fields.append(field)

            field = SelectMultipleField(
                field_name="researchers",
                is_required=False,
                choices=self.listSortedMultipleOptions(self.registry.researchers),
                size=self.sizeSelectMultiple,
            )
            field.field_title = 'researchers'
            self.fields.append(field)

            field = SelectMultipleField(
                field_name="approvals",
                is_required=False,
                choices=self.listSortedMultipleOptions(self.registry.approvals),
                size=self.sizeSelectMultiple,
            )
            field.field_title = 'approvals'
            self.fields.append(field)

            field = SelectField(
                field_name="funding",
                is_required=False,
                choices=self.listSortedOptions(self.registry.fundingStatuses),
            )
            field.field_title = 'funding'
            self.fields.append(field)

            field = SelectField(
                field_name="status",
                is_required=False,
                choices=self.listSortedOptions(self.registry.projectStatuses),
            )
            field.field_title = 'status'
            self.fields.append(field)

            field = SelectField(
                field_name="outcome",
                is_required=False,
                choices=self.listSortedOptions(self.registry.projectOutcomes),
            )
            field.field_title = 'outcome'
            self.fields.append(field)

            field = IntegerField(
                field_name="preparationMinutes",
                is_required=True,
            )
            field.field_title = 'preparation minutes'
            self.fields.append(field)

            field = SelectField(
                field_name="volunteerBookingMethod",
                is_required=False,
                choices=self.listSortedOptions(
                    self.registry.volunteerBookingMethods),
            )
            field.field_title = 'volunteer booking method'
            self.fields.append(field)

            field = RDateField(
                field_name="IIGPresentation", 
                is_required=False,
            )
            field.field_title = 'IIG presentation'
            self.fields.append(field)


            field = RDateField(
                field_name="IMCApproval", 
                is_required=False,
            )
            field.field_title = 'IMC approval'
            self.fields.append(field)

            field = IntegerField(
                field_name="numberSubjects",
                is_required=False,
            )
            field.field_title = 'number of subjects'
            self.fields.append(field)

            field = IntegerField(
                field_name="numberPilots",
                is_required=False,
            )
            field.field_title = 'number of pilots'
            self.fields.append(field)

            field = IntegerField(
                field_name="slotMinutes",
                is_required=True,
            )
            field.field_title = 'slot minutes'
            self.fields.append(field)

            field = SelectField(
                field_name="volunteerType",
                is_required=False,
                choices=self.listSortedOptions(
                    self.registry.volunteerTypes),
            )
            field.field_title = 'volunteer type'
            self.fields.append(field)

            field = RDateField(
                field_name="startDate",
                is_required=False,
            )
            field.field_title = 'start date'
            self.fields.append(field)

            field = RDateField(
                field_name="completionDate",
                is_required=False,
            )
            field.field_title = 'completion date'
            self.fields.append(field)

            field = LargeTextField(
                field_name="notes",
                is_required=False,
            )
            field.field_title = 'notes'
            self.fields.append(field)


    def listSortedOptions(self, domainObjectRegister):
        sortedList = domainObjectRegister.getSortedList()
        return self.listSelectOptions(sortedList)

    def listSortedMultipleOptions(self, domainObjectRegister):
        sortedList = domainObjectRegister.getSortedList()
        return self.listSelectMultipleOptions(sortedList)

    def listSelectOptions(self, domainObjects):
        return [('', '-- select option --')] + [(i.getRegisterKeyValue(), i.getLabelValue()) for i in domainObjects]

    def listSelectMultipleOptions(self, domainObjects):
        return [(
            i.getRegisterKeyValue(), i.getLabelValue()
        ) for i in domainObjects]

    def isProjectTitleUnique(self, field_data, all_data):
        new_title = field_data
        l = self.registry.projects.findDomainObjects(title=new_title)
        if self.domainObject != None:
            if self.domainObject in l:
                l.remove(self.domainObject)
        if len(l):
            message = "Project title '%s' is already in use." % new_title
            raise ValidationError(message)


class VolunteerManipulator(DomainObjectManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'realname': VolunteerRealnameField(
                    label='real name',
                    manipulator=self,
                ),
                'dateOfBirth': DateField(
                    required=False,
                ),
                'language': webkit.CharField(
                    required=False,
                ),
                'panelId': VolunteerPanelIdField(
                    required=False,
                    label='panel ID',
                    manipulator=self,
                ),
                'status': ChoiceField(
                    required=False,
                    label='panel ID',
                    choices=self.listStatusOptions(),
                ),
                'onHitList': webkit.BooleanField(
                    label='show on hitlist',
                    required=False,
                ),
                'handedness': ChoiceField(
                    required=False,
                    choices=self.listHandednessOptions(),
                ),
                'homeAddress': webkit.CharField(
                    label='home address',
                    required=False,
                    widget=webkit.widgets.Textarea()
                ),
                'recruitment': ChoiceField(
                    label='recruitment method',
                    required=False,
                    choices=self.listRecruitmentOptions(),
                ),
                'email': EmailField(
                    label='email address',
                    required=False,
                ),
                'workTelephone': CharField(
                    label='work telephone',
                    required=False,
                ),
                'mobileTelephone': CharField(
                    label='mobile telephone',
                    required=False,
                ),
                'doctorAddress': webkit.CharField(
                    label='doctor address',
                    required=False,
                    widget=webkit.widgets.Textarea()
                ),
                'doctorName': webkit.CharField(
                    label='doctor name',
                    required=False,
                    widget=webkit.widgets.Textarea()
                ),
                'doctorTelephone': CharField(
                    label='doctor telephone',
                    required=False,
                ),
                'notes': webkit.CharField(
                    required=False,
                    widget=webkit.widgets.Textarea()
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = TextField(
                field_name="realname", 
                is_required=True,
                validator_list=[
                    self.isVolunteerRealnameUnique,
                ]
            )
            field.field_title = 'real name'
            self.fields.append(field)

            field = RDateField(
                field_name='dateOfBirth',
                is_required=False,
            )
            field.field_title = 'date of birth'
            self.fields.append(field)

            field = TextField(
                field_name="language", 
                is_required=False,
            )
            field.field_title = 'language'
            self.fields.append(field)

            field = TextField(
                field_name="panelId", 
                is_required=True,
                validator_list=[
                    self.isVolunteerPanelIdUnique,
                ]
            )
            field.field_title = 'panel ID'
            self.fields.append(field)

            field = SelectField(
                field_name="status",
                is_required=False,
                choices=self.listStatusOptions()
            )
            field.field_title = 'status'
            self.fields.append(field)

            field = CheckboxField(
                field_name="onHitlist",
            )
            field.field_title = 'show on hitlist'
            self.fields.append(field)

            field = SelectField(
                field_name="handedness",
                is_required=False,
                choices=self.listHandednessOptions()
            )
            field.field_title = 'handedness'
            self.fields.append(field)

            field = LargeTextField(field_name="homeAddress", is_required=False)
            field.field_title = 'home address'
            self.fields.append(field)

            field = SelectField(
                field_name="recruitment",
                is_required=False,
                choices=self.listRecruitmentOptions()
            )
            field.field_title = 'recruitment method'
            self.fields.append(field)

            field = EmailField(field_name="email", is_required=False)
            field.field_title = 'email address'
            self.fields.append(field)

            field = TextField(field_name="workTelephone", is_required=False)
            field.field_title = 'work telephone'
            self.fields.append(field)

            field = TextField(field_name="workTelephone", is_required=False)
            field.field_title = 'home telephone'
            self.fields.append(field)

            field = TextField(field_name="mobileTelephone", is_required=False)
            field.field_title = 'mobile telephone'
            self.fields.append(field)

            field = LargeTextField(field_name="doctorAddress", is_required=False)
            field.field_title = 'doctor address'
            self.fields.append(field)

            field = LargeTextField(field_name="doctorName", is_required=False)
            field.field_title = 'doctor name'
            self.fields.append(field)

            field = TextField(field_name="doctorTelephone", is_required=False)
            field.field_title = 'doctor telephone'
            self.fields.append(field)

            field = LargeTextField(field_name="notes", is_required=False)
            field.field_title = 'notes'
            self.fields.append(field)

    def isVolunteerRealnameUnique(self, field_data, all_data):
        new_realname = field_data
        l = self.registry.volunteers.findDomainObjects(realname=new_realname)
        if self.domainObject != None:
            if self.domainObject in l:
                l.remove(self.domainObject)
        if len(l):
            message = "Volunteer '%s' is already registered." % new_realname
            raise ValidationError(message)

    def isVolunteerPanelIdUnique(self, field_data, all_data):
        panelId = field_data
        l = self.registry.volunteers.findDomainObjects(panelId=panelId)
        if self.domainObject != None:
            if self.domainObject in l:
                l.remove(self.domainObject)
        if len(l):
            message = "Panel ID '%s' is already in use." % panelId
            raise ValidationError(message)

    def listStatusOptions(self):
        return self.listSortedOptions(self.registry.volunteerStatuses)

    def listHandednessOptions(self):
        return self.listSortedOptions(self.registry.handednesses)

    def listRecruitmentOptions(self):
        return self.listSortedOptions(self.registry.volunteerRecruitmentMethods)

    def listSortedOptions(self, domainObjectRegister):
        sortedList = domainObjectRegister.getSortedList()
        return self.listSelectOptions(sortedList)

    def listSelectOptions(self, domainObjects):
        return [('', '-- select option --')] + \
        [(i.getRegisterKeyValue(), i.getLabelValue()) for i in domainObjects]


class ReportCreateManipulator(DomainObjectManipulator):
    
    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'title': webkit.CharField(
                    required=False,
                ),
                'against': ChoiceField(
                    required=False,
                    choices=self.getAgainstOptions(),
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = TextField(
                field_name='title', 
                is_required=False,
            )
            field.field_title = 'title'
            self.fields.append(field)

            field = SelectField(
                field_name="against",
                is_required=True,
                choices=self.getAgainstOptions(),
            )
            field.field_title = 'report against'
            self.fields.append(field)

    def getAgainstOptions(self):
        classNames = self.registry.getDomainClassRegister().keys()
        classNames.sort()
        return [('', '-- select option --')] + [(n, n) for n in classNames]


class ReportUpdateManipulator(DomainObjectManipulator):
    
    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields.update({
                'title': webkit.CharField(
                    required=False,
                ),
            }) 
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            field = TextField(
                field_name='title', 
                is_required=False,
            )
            field.field_title = 'title'
            self.fields.append(field)

    def getAgainstOptions(self):
        classNames = self.registry.getDomainClassRegister().keys()
        classNames.sort()
        return [('', '-- select option --')] + [(n, n) for n in classNames]


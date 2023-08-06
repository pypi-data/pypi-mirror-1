from dm.dom.stateful import *
from mx.DateTime import DateTimeDelta

class SessionType(StandardObject):

    isConstant = True
    color = String()


class ScanningSessionType(StandardObject):
 
    isConstant = True


class TrainingSessionType(StandardObject):
 
    isConstant = True


class VolunteerBookingMethod(StandardObject):
 
    isConstant = True


class ScanningSessionOutcome(StandardObject):
 
    isConstant = True


class EarmarkedTimeTemplateWeek(StandardObject):

    earmarkedTimeTemplates = AggregatesMany('EarmarkedTimeTemplate', 'id')


class EarmarkedTimeTemplate(StatefulObject):

    isUnique = False
    earmarkedTimeTemplateWeek = HasA('EarmarkedTimeTemplateWeek')
    sessionType = HasA('SessionType', isRequired=False, isSimpleOption=True)
    organisation = HasA('Organisation', isRequired=False)
    startsDay = Integer()
    startsHour = Integer()
    startsMinute = Integer()
    endsDay = Integer()
    endsHour = Integer()
    endsMinute = Integer()
    comment = String(default='', isRequired=False)


# Old earmark template class.
class WeekEarmarkTemplate(StandardObject):

    earmarkTemplates = AggregatesMany('EarmarkTemplate', 'id')


# Old earmark template class.
class EarmarkTemplate(StatefulObject):

    isUnique = False
    weekEarmarkTemplate = HasA('WeekEarmarkTemplate')
    sessionType = HasA('SessionType', isRequired=False, isSimpleOption=True)
    comment = String(default='', isRequired=False)
    day = Integer()
    hour = Integer()
    minute = Integer()


# todo: Rename to TimeSlot?
class AbstractSession(DatedStatefulObject):

    isUnique = False

    starts = RNSDateTime()
    ends = RNSDateTime()
    
    typeNick = 'abstract'

    sortOnName = 'starts'
    sortAscending = True

    def getDuplicateAttrNames(self):
        names = []
        names.append('starts')
        names.append('ends')
        return names

    def getGridCellLink(self, cell=None):
        url = '/%s/%s/' % (
            self.getRegistryAttrName(),
            self.getRegisterKeyValue()
        )
        return url

    def getGridCellLinkLabel(self):
        return ''

    def getCellContent(self):
        return self.typeNick

    def getGridStartCellContent(self):
        return self.getCellContent()

    def getGridMiddleCellContent(self):
        return self.getCellContent()

    def getGridEndCellContent(self):
        return self.getCellContent()

    def getGridCellClass(self):  # Used for CSS classes.
        return self.typeNick

    def getCalendarTypeName(self):
        return 'abstract'

    def getCalendarSummary(self):
        return u'<span class="sessiontimesummary">%s:%s - %s:%s</span>' % (
            str(self.starts.hour).zfill(2),
            str(self.starts.minute).zfill(2),
            str(self.ends.hour).zfill(2),
            str(self.ends.minute).zfill(2),
        )

    def getCalendarId(self):
        return "%s.%s" % (self.__class__.__name__, self.id)

    def getSlotTypeName(self):
        return 'abstract'

    def getTooltipContent(self):
        tooltipContent = """
        %s<br />
        Starts: %s<br />
        Ends: %s<br />
        """ % (
            self.typeNick.capitalize(),
            self.starts,
            self.ends
        )
        return tooltipContent

    def getStartsEndsContent(self):
        startsContent = str(self.starts.hour).zfill(2)
        startsContent += ':'
        startsContent += str(self.starts.minute).zfill(2)
        endsContent = str(self.ends.hour).zfill(2)
        endsContent += ':'
        endsContent += str(self.ends.minute).zfill(2)
        return startsContent + ' - ' + endsContent

    def getDuration(self):
        if self.ends and self.starts:
            return self.ends - self.starts
        else:
            return None

    def getMinutes(self):
        duration = self.getDuration()
        if duration != None:
            return int(duration.minutes)
        else:
            return 0


class AbstractScannerSession(AbstractSession):

    scanner = HasA('Scanner', isRequired=False)
    organisation = HasA('Organisation', isRequired=False)
    
    isEarmark = False
    isBooking = False

    def initialise(self, register=None):
        if self.organisation == None:
            if 'default' in self.registry.settings:
                settings = self.registry.settings['default']
                self.organisation = settings.defaultOrganisation
        if self.organisation != None:
            self.isChanged = True

    def duplicateAt(self, starts, register=None):
        register = register or self.__class__.createRegister()
        ends = starts + (self.ends - self.starts)
        kwds = {}
        for attrName in self.getDuplicateAttrNames():
            kwds[attrName] = getattr(self, attrName)
        kwds['starts'] = starts
        kwds['ends'] = ends
        return register.create(**kwds)
        
    def getDuplicateAttrNames(self):
        names = super(AbstractScannerSession, self).getDuplicateAttrNames()
        names.append('scanner')
        names.append('organisation')
        return names

    # old method
    def getDuplicateKwds(self):
        kwds = {}
        kwds['starts'] = self.ends
        kwds['ends'] = kwds['starts'] + (self.ends - self.starts)
        return kwds


class EarmarkedTime(AbstractScannerSession):

    typeNick = 'earmarked'
    sessionType = HasA('SessionType', isRequired=False, isSimpleOption=True)
    comment = String(default='', isRequired=False)
    isEarmark = True
    bookableSessionTypes = ['Scanning', 'Maintenance']

    def getDuplicateAttrNames(self):
        names = super(EarmarkedTime, self).getDuplicateAttrNames()
        names.append('sessionType')
        names.append('comment')
        return names

    def getGridCellLink(self, cell=None):
        if self.sessionType.name in self.bookableSessionTypes:
            sessionClassName = self.sessionType.name + "Session"
            sessionClass = self.registry.getDomainClass(sessionClassName)
            registryAttrName = sessionClass.getRegistryAttrName()
            actionName = "create"
            url = '/%s/%s/' % (
                registryAttrName,
                actionName,
            )
            url += "?starts=%s-%s-%s %s:%s:00" % (
                cell['year'],
                cell['month'],
                cell['day'],
                cell['hour'],
                cell['minute'],
            )
            hour = cell['hour']
            hour = int(hour)
            hour += 1
            hour = str(hour)
            if len(hour) == 1:
                hour = "0%s" % hour
            url += "&ends=%s-%s-%s %s:%s:00" % (
                cell['year'],
                cell['month'],
                cell['day'],
                hour,
                cell['minute'],
            )
            url += "&scanner=%s" % (
                cell['scanner'],
            )
            return url
        else:
            registryAttrName = self.getRegistryAttrName()
            registerKeyValue = self.getRegisterKeyValue()
            return '/%s/%s/' % (
                registryAttrName,
                registerKeyValue,
            )

    def getCalendarSummary(self):
        cellContent = u' '
        if self.comment:
            cellContent += u'%s' % self.comment
        return cellContent

    def getCellContent(self):
        return self.comment

    def getGridCellClass(self):  # Used for CSS classes.
        return self.sessionType.name.lower().replace(" ", "")

    def getGridCellLinkLabel(self):
        if self.sessionType.name in self.bookableSessionTypes:
            return 'Create %s session' % self.sessionType.name.lower()
        else:
            return 'Update %s time' % self.sessionType.name.lower()
        
    def getTooltipContent(self):
        tooltipContent = """
        %s<br />
        %s: %s<br />
        Comment: %s<br />
        """ % (
            self.getStartsEndsContent(),
            self.typeNick.capitalize(),
            self.sessionType.name,
            self.comment,
        )
        return tooltipContent

    def getCalendarTypeName(self):
        if self.sessionType:
            typeName = self.sessionType.name
            typeName = typeName.replace(" ", "")
            typeName = typeName[0].lower() + typeName[1:]
            return typeName
        return 'earmarked'

    def getSlotTypeName(self):
        return 'earmark'


class ScheduledScannerSession(AbstractScannerSession):

    isBooking = True
    createdBy = HasA('Person', isRequired=False)
    
    def getDuplicateAttrNames(self):
        names = super(ScheduledScannerSession, self).getDuplicateAttrNames()
        names.append('createdBy')
        return names

    def getDuplicateKwds(self):
        kwds = super(ScheduledScannerSession, self).getDuplicateKwds()
        kwds['scanner'] = self.scanner
        kwds['createdBy'] = self.createdBy
        return kwds

    def getLabelValue(self):
        labelValue = ""
        if self.starts:
            labelValue += self.starts.strftime("%H:%M")
        if self.ends:
            labelValue += self.ends.strftime(" - %H:%M, %a, %e %b %Y")
        return labelValue

    def isComplete(self):
        return False

    def getGridStartCellContent(self):
        return '%s'[0:11] % self.typeNick.upper()

    def getGridCellLinkLabel(self):
        return 'Update %s session' % self.typeNick

    def getGridCellClass(self):  # Used for CSS classes.
        return self.typeNick + "light"

    def getSlotTypeName(self):
        return 'session'


class MaintenanceSession(ScheduledScannerSession):

    typeNick = 'maintenance'
    comment = String(isRequired=False)

    def getDuplicateAttrNames(self):
        names = super(MaintenanceSession, self).getDuplicateAttrNames()
        names.append('comment')
        return names

    def getDuplicateKwds(self):
        kwds = super(MaintenanceSession, self).getDuplicateKwds()
        kwds['comment'] = self.comment
        return kwds

    def getCalendarSummary(self):
        cellContent = super(MaintenanceSession, self).getCalendarSummary()
        cellContent += u"<br/>Maintenance"
        if self.comment:
            cellContent += u"<br/>%s" % self.comment
        return cellContent

    def getCellContent(self):
        cellContent = ""
        if self.comment:
            cellContent = self.comment
        else:
            cellContent = "Maintenance"
        return "<br/>" + cellContent

    def getComment(self):
        if self.comment:
            return self.comment
        else:
            return "None"

    def isComplete(self):
        return bool(self.comment)

    def getTooltipContent(self):
        tooltipContent = """
        %s<br />
        Maintainer: %s<br />
        Created: %s<br />
        Modified: %s<br />
        """ % (
            self.getStartsEndsContent(),
            self.getComment(),
            self.dateCreatedLocal(),
            self.lastModifiedLocal(),
        )
        return tooltipContent

    def getCalendarTypeName(self):
        return 'maintenance'


class MethodsSession(ScheduledScannerSession):

    typeNick = 'methods'
    comment = String(isRequired=False)

    def getDuplicateAttrNames(self):
        names = super(MethodsSession, self).getDuplicateAttrNames()
        names.append('comment')
        return names

    def getDuplicateKwds(self):
        kwds = super(MethodsSession, self).getDuplicateKwds()
        kwds['comment'] = self.comment
        return kwds

    def getCalendarSummary(self):
        cellContent = super(MethodsSession, self).getCalendarSummary()
        cellContent += u"<br/>Methods"
        if self.comment:
            cellContent += u"<br/>%s" % self.comment
        return cellContent

    def getCellContent(self):
        cellContent = ""
        if self.comment:
            cellContent = self.comment
        else:
            cellContent = "Methods"
        return "<br/>" + cellContent

    def getComment(self):
        if self.comment:
            return self.comment
        else:
            return "None"

    def isComplete(self):
        return bool(self.comment)
    
    def getCalendarTypeName(self):
        return 'methods'


class DowntimeSession(ScheduledScannerSession):

    typeNick = 'downtime'
    reason = String(isRequired=False)

    def getDuplicateAttrNames(self):
        names = super(DowntimeSession, self).getDuplicateAttrNames()
        names.append('reason')
        return names

    def getDuplicateKwds(self):
        kwds = super(DowntimeSession, self).getDuplicateKwds()
        kwds['reason'] = self.reason
        return kwds
  
    def getCalendarSummary(self):
        cellContent = super(DowntimeSession, self).getCalendarSummary()
        cellContent += u"<br />Downtime"
        if self.reason:
            cellContent += u"<br />%s" % self.reason
        return cellContent

    def getCellContent(self):
        cellContent = ""
        if self.reason:
            cellContent = self.reason
        else:
            cellContent = "Downtime"
        return "<br/>" + cellContent

    def getReason(self):
        if self.reason:
            return self.reason
        else:
            return "None"

    def isComplete(self):
        return bool(self.reason)

    def getTooltipContent(self):
        tooltipContent = """
        %s<br />
        Reason: %s<br />
        Created: %s<br />
        Modified: %s<br />
        """ % (
            self.getStartsEndsContent(),
            self.getReason(),
            self.dateCreatedLocal(),
            self.lastModifiedLocal(),
        )
        return tooltipContent

    def getCalendarTypeName(self):
        return 'downtime'


class ScanningSession(ScheduledScannerSession):

    typeNick = 'scanning'
    
    # session booking stage
    project = HasA('Project', isRequired=False)
    leader = HasA('Researcher', isRequired=False)
    approval = HasA('Approval', isRequired=False)
    ethicsUsed = Boolean(default=True)
    scanningSessionType = HasA('ScanningSessionType', default='Standard',
        isRequired=False, isSimpleOption=True)
    volunteerBookingMethod = HasA('VolunteerBookingMethod', isRequired=False,
        isSimpleOption=True)
    replacement = Boolean(default=False)
    bookingOwnVolunteers = Boolean(default=False)
    buddy1 = HasA('Researcher', isRequired=False)
    buddy2 = HasA('Researcher', isRequired=False)
    notes = String(default='', isRequired=False)

    # volunteer booking stage
    volunteer = HasA('Volunteer', isRequired=False)
    backupVolunteer = HasA('Volunteer', isRequired=False)
    
    # session reporting stage
    scanId = String(default='', isRequired=False)
    outcome = HasA('ScanningSessionOutcome', isRequired=False, isSimpleOption=True)
    volunteerUsed = Boolean(default=False)
    usedMinutes = Integer(default=0, isRequired=False)

    def getDuplicateAttrNames(self):
        names = super(ScanningSession, self).getDuplicateAttrNames()
        names.append('project')
        names.append('approval')
        names.append('leader')
        names.append('ethicsUsed')
        names.append('scanningSessionType')
        names.append('volunteerBookingMethod')
        names.append('replacement')
        names.append('bookingOwnVolunteers')
        names.append('buddy1')
        names.append('buddy2')
        return names

    def getDuplicateKwds(self):
        kwds = super(ScanningSession, self).getDuplicateKwds()
        kwds['project'] = self.project
        kwds['approval'] = self.approval
        kwds['scanningSessionType'] = self.scanningSessionType
        kwds['replacement'] = self.replacement
        kwds['volunteerBookingMethod'] = self.volunteerBookingMethod
        kwds['bookingOwnVolunteers'] = self.bookingOwnVolunteers
        kwds['buddy1'] = self.buddy1
        kwds['buddy2'] = self.buddy2
        return kwds

    def getCalendarSummary(self):
        cellContent = super(ScanningSession, self).getCalendarSummary()
        cellContent += u"<br/>%s" % self.getContactName()
        if self.bookingOwnVolunteers:
            cellContent += u" <strong>&lowast;</strong>"
        if self.project and self.project.account:
            cellContent += u"<br/>C: %s" % self.project.account.getLabelValue()
        if self.approval:
            cellContent += u"<br/>E: %s" % self.approval.code
        return cellContent

    def getCellContent(self):
        cellContent = self.getIconDiv()
        cellContent += "<br />%s" % self.getContactName()
        if self.bookingOwnVolunteers:
            cellContent += " <strong>&lowast;</strong>"
        if self.volunteer:
            cellContent += " <strong>V</strong>"
        return cellContent

    def getIconDiv(self):
        return """
        <div id="session-icons" style="float:left; color:black; font-size:x-small">&nbsp;%s</div>
        """ % self.getIconString()

    def getIconString(self):
        icons = []
        if self.replacement:
            icons.append('R')
        if self.scanningSessionType.name == "Pilot":
            icons.append('P')
        return "&nbsp;".join(icons)
        
    def getArrivalTime(self):
        preparationMinutes = 0
        if self.project:
            preparationMinutes = self.project.preparationMinutes
        return self.starts - DateTimeDelta(0, 0, preparationMinutes)

    def isComplete(self):
        return self.project and self.volunteer

    def getContactName(self):
        sessionContact = self.getContact()
        if sessionContact:
            return sessionContact.realname
        else:
            return u"No contact"

    def getContact(self):
        if self.leader:
            return self.leader
        elif self.project and self.project.leader:
            return self.project.leader
        else:
            return None
    
    def getResearcherNames(self):
        if self.project and self.project.researchers:
            return [r.realname for r in self.project.researchers.keys()]
        else:
            if self.createdBy and (self.createdBy.role.name != 'Administrator'):
                return [self.createdBy.fullname]
            else:
                return ["No project"]
    
    def getProjectTitle(self):
        if self.project:
            return self.project.title
        else:
            return "None"
    
    def getVolunteerName(self):
        if self.volunteer:
            return self.volunteer.realname
        else:
            return "None"
    
    def getOutcomeName(self):
        if self.outcome:
            return self.outcome.name
        else:
            return "None"
    
    def getTooltipContent(self):
        tooltipContent = """
        %s<br />
        Leader: %s<br />
        Researchers: %s<br />
        Project: %s<br />
        Volunteer: %s<br />
        Outcome: %s<br />
        Created: %s<br />
        Modified: %s<br />
        """ % (
            self.getStartsEndsContent(),
            self.getContactName(),
            ", ".join(self.getResearcherNames()),
            self.getProjectTitle(),
            self.getVolunteerName(),
            self.getOutcomeName(),
            self.dateCreatedLocal(),
            self.lastModifiedLocal(),
        )
        return tooltipContent

    def getCalendarTypeName(self):
        return 'scanning'


class TrainingSession(AbstractSession):

    typeNick = 'training'
    
    type = HasA('TrainingSessionType', isRequired=False, isSimpleOption=True)
    capacity = Integer(default=10, isRequired=False)
    location = String(isRequired=False)
    presenter = String(isRequired=False)
    comment = String(isRequired=False)
    researchers = AggregatesMany('ResearcherTrainingAppointment', 'researcher')
    notes = Text(isRequired=False)

    def getLabelValue(self):
        labelValue = ""
        if self.starts:
            labelValue += self.starts.strftime("%H:%M")
        if self.ends:
            labelValue += self.ends.strftime(" - %H:%M")
            labelValue += self.ends.strftime(", %a, %e %b %Y")
        return labelValue

    def getCalendarTypeName(self):
        return 'training'

    def countAvailable(self):
        countResearchers = len(self.researchers)
        if countResearchers >= self.capacity:
            return 0
        else:
            return self.capacity - countResearchers


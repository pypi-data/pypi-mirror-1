from scanbooker.django.apps.sui.views.base import ScanBookerView
import scanbooker.command
import scanbooker.workingHours
import mx.DateTime
from dm.strategy import EpochFromDateTime
from scanbooker.dictionarywords import DOJO_PREFIX
from markdown import Markdown

class Day(object):
    
    def __init__(self, starts, number, name):
        self.starts = starts
        self.number = number
        self.name = name
    

class TimeBlock(object):

    def __init__(self, hour, minute):
        self.hour = int(hour)
        self.minute = int(minute)
        self.name = self.createBlockName()

    def createBlockName(self):
        hour = str(int(self.hour))
        minute = str(int(self.minute))
        if len(hour) == 1:
            hour = '0' + hour
        if len(hour) != 2:
            raise Exception, hour
        if len(minute) == 1:
            minute = '0' + minute 
        if len(minute) != 2:
            raise Exception, minute
        return hour + ":" + minute


class GridCell(object):

    top = None
    left = None
    width = None
    height = None
    cssClass = None
    htmlContent = None
    tooltipContent = None

    def __init__(self, item):
        self.item = item

    def setTopLeftWidthHeight(self, view):
        self.setStartsEnds()
        self.setTop(view)
        self.setLeft(view)
        self.setHeight(view)
        self.setWidth(view)

    def asHash(self):
        data = {}
        data['top'] = self.top
        data['left'] = self.left
        data['width'] = self.width
        data['height'] = self.height
        data['cssClass'] = self.cssClass
        data['htmlContent'] = self.htmlContent
        data['tooltipContent'] = self.tooltipContent
        data['background'] = ''
        return data
 

class DayGridCell(GridCell):

    def __init__(self, day):
        super(DayGridCell, self).__init__(item=day)
        self.cssClass = 'schedule-day'
        self.htmlContent = """%s
        """ % (
            self.item.name
        )
    
    def setStartsEnds(self):
        pass
    
    def setTop(self, view):
        self.top = 0
 
    def setLeft(self, view):
        self.left = self.item.number * view.pixelsPerDay + view.timeColWidth
        
    def setHeight(self, view):
        self.height = view.dayRowHeight
 
    def setWidth(self, view):
        self.width = view.pixelsPerDay
 

class TimeBlockGridCell(GridCell):

    def __init__(self, timeBlock):
        super(TimeBlockGridCell, self).__init__(item=timeBlock)
        self.cssClass = 'schedule-timeblock'
        if self.item.minute:
            self.cssClass += ' schedule-greyed'
        self.htmlContent = """%s
        """ % (
            self.item.name
        )
    
    def setStartsEnds(self):
        pass
    
    def setTop(self, view):
        cellStartMinuteOfDay = self.item.hour * 60 + self.item.minute
        cellStartMinuteOfGrid = cellStartMinuteOfDay - view.gridStartMinuteOfDay
        if cellStartMinuteOfGrid < 0:
            cellStartMinuteOfGrid = 0
        elif cellStartMinuteOfGrid > view.gridMinutesMax:
            cellStartMinuteOfGrid = view.gridMinutesMax
        cellStartPixelOfGrid = int(cellStartMinuteOfGrid * view.pixelsPerMinute)
        self.top = cellStartPixelOfGrid + view.dayRowHeight
 
    def setLeft(self, view):
        self.left = 0
        
    def setHeight(self, view):
        cellDurationMinutes = view.blockDuration.minutes
        cellDurationPixels = int(cellDurationMinutes * view.pixelsPerMinute)
        self.height = cellDurationPixels
 
    def setWidth(self, view):
        self.width = view.timeColWidth
 

class ScheduledTimeGridCell(GridCell):

    def __init__(self, session):
        super(ScheduledTimeGridCell, self).__init__(item=session)
        self.registryAttrName = self.item.getRegistryAttrName()
        self.registerKeyValue = self.item.getRegisterKeyValue()
        self.cssClass = 'schedule-%s' % self.item.typeNick
        if self.item.typeNick == 'earmarked':
            #self.htmlContent = ""
            self.htmlContent = self.createHtmlContent()
        else:
            self.htmlContent = self.createHtmlContent()
        self.tooltipContent = self.createTooltipContent()
            
    def createHtmlContent(self):
        return self.item.getCellContent()

    def createTooltipContent(self):
        return ""
        
    def asHash(self):
        data = super(ScheduledTimeGridCell, self).asHash()
        data['registryId'] = self.item.getRegistryId()
        return data
        
    def setStartsEnds(self):
        # Convert to mx.DateTime.DateTime.
        self.starts = mx.DateTime.DateTime(
            self.item.starts.year,
            self.item.starts.month,
            self.item.starts.day,
            self.item.starts.hour,
            self.item.starts.minute,
            self.item.starts.second,
        )
        self.ends = mx.DateTime.DateTime(
            self.item.ends.year,
            self.item.ends.month,
            self.item.ends.day,
            self.item.ends.hour,
            self.item.ends.minute,
            self.item.ends.second,
        )

    def setTop(self, view):
        cellStartMinuteOfDay = self.starts.hour * 60 + self.starts.minute
        cellStartMinuteOfGrid = cellStartMinuteOfDay - view.gridStartMinuteOfDay
        if cellStartMinuteOfGrid < 0:
            cellStartMinuteOfGrid = 0
        elif cellStartMinuteOfGrid > view.gridMinutesMax:
            cellStartMinuteOfGrid = view.gridMinutesMax
        cellStartPixelOfGrid = int(cellStartMinuteOfGrid * view.pixelsPerMinute)
        self.top = cellStartPixelOfGrid + view.dayRowHeight
 
    def setLeft(self, view):
        cellStartDuration = self.starts - view.weekStarts
        cellStartDayOfWeek = cellStartDuration.day
        cellStartPixelOfGrid = cellStartDayOfWeek * view.pixelsPerDay
        self.left = cellStartPixelOfGrid + view.timeColWidth
 
    def setHeight(self, view):
        cellDuration = self.ends - self.starts
        cellDurationMinutes = cellDuration.hour * 60 + cellDuration.minute
        cellDurationPixels = int(cellDurationMinutes * view.pixelsPerMinute)
        self.height = cellDurationPixels
 
    def setWidth(self, view):
        self.width = view.pixelsPerDay


class SessionGridCell(ScheduledTimeGridCell):
    pass 
    

class EarmarkedGridCell(ScheduledTimeGridCell):

    def asHash(self):
        data = super(EarmarkedGridCell, self).asHash()
        data['background'] = '#' + self.item.sessionType.color
        return data


class ScheduleView(ScanBookerView):

    blockDuration = mx.DateTime.oneMinute * 15

    def __init__(self, year=None, month=None, day=None, block=None, **kwds):
        super(ScheduleView, self).__init__(**kwds)
        self.year = year
        self.month = month
        self.day = day
        self.block = block

    def setMinorNavigationItems(self):
        self.minorNavigation = [
        ]
        self.minorNavigation.append(
            {'title': 'Week',       'url': '/schedule/week/'}
        )
        if self.canCreateScanningSession():
            self.minorNavigation.append(
                {'title': 'Quick entry', 'url': '/scanningSessions/create/'}
            )

    def canAccess(self):
        return self.canReadSystem()

    def takeAction(self):
        pass


# Simple view, to return the schedule view framework only.
class WeekScheduleView2(ScheduleView):

    templatePath = 'schedule2/week'
    majorNavigationItem = '/schedule/'
    minorNavigationItem = '/schedule/week/'
    
    def __init__(self, **kwds):
        super(WeekScheduleView2, self).__init__(**kwds)

    def takeAction(self):
        super(WeekScheduleView2, self).takeAction()
        self.setScheduleBookmark()

    def setScheduleBookmark(self):
        if self.year and self.month and self.day:
            timeInWeek = mx.DateTime.Date(
                int(self.year), int(self.month), int(self.day)
            )
            if self.session:
                if self.session.scheduleBookmark != timeInWeek:
                    self.session.scheduleBookmark = timeInWeek
                    self.session.save()


# Now used as the base class for the Widgets.
class WeekScheduleView(ScheduleView):

    templatePath = 'schedule/week'
    majorNavigationItem = '/schedule/'
    minorNavigationItem = '/schedule/week/'
    numberDays = 6
    timeInWeek = None
    weekStarts = None
    weekEnds   = None
    calendarYear  = None
    calendarMonth = None
    calendarDay   = None
    
    def __init__(self, **kwds):
        super(WeekScheduleView, self).__init__(**kwds)
        self.week = None

    def isWeekVisible(self):
        if self.isAfterFutureHorizon() or self.isBeforePastHorizon():
            return False
        else:
            return self.isWeekPublished()

    def isWeekPublished(self):
        week = self.findWeek()
        if week:
            return week.isPublished
        elif self.canUpdateSystem():
            self.publishWeek()
        else:
            return False

    def hideWeek(self):
        week = self.findWeek()
        if not week:
            week = self.createWeek()
        week.isPublished = False
        week.save()

    def publishWeek(self):
        week = self.findWeek()
        if not week:
            week = self.createWeek()
        if week.isPublished != True:
            week.isPublished = True
            week.save()

    def findWeek(self):
        if self.weekStarts == None:
            self.initialiseWeekTimes()
        register = self.registry.weeks
        return register.findSingleDomainObject(starts=self.weekStarts)

    def createWeek(self):
        if self.weekStarts == None:
            self.initialiseWeekTimes()
        register = self.registry.weeks
        return register.create(starts=self.weekStarts, isPublished=True)

    def getWeek(self):
        if self.weekStarts == None:
            self.initialiseWeekTimes()
        if not self.week:
            self.week = self.findWeek()
            if not self.week:
                self.week = self.createWeek()
        return self.week

    def getPastHorizon(self):
        numberWeeksPast = 4  # todo: create SystemConfig domain object
        pastHorizonDistance = mx.DateTime.oneWeek * numberWeeksPast
        return mx.DateTime.now() - pastHorizonDistance
    
    def getFutureHorizon(self):
        numberWeeksFuture = 12  # todo: create SystemConfig domain object
        futureHorizonDistance = mx.DateTime.oneWeek * numberWeeksFuture
        return mx.DateTime.now() + futureHorizonDistance

    def isAfterFutureHorizon(self):
        if self.weekStarts == None:
            self.initialiseWeekTimes()
        return self.getFutureHorizon() < self.weekStarts

    def isBeforePastHorizon(self):
        if self.weekStarts == None:
            self.initialiseWeekTimes()
        return self.getPastHorizon() > self.weekStarts

    def takeAction(self):
        self.initialiseWeekTimes()

    def setContext(self, **kwds):
        super(WeekScheduleView, self).setContext(**kwds)
        dojoPrefix = self.dictionary[DOJO_PREFIX]
        jsCanCreateEarmarkedTime = str(self.canCreateEarmarkedTime()).lower()
        jsCanUpdateEarmarkedTime = str(self.canUpdateEarmarkedTime()).lower()
        jsCanDeleteEarmarkedTime = str(self.canDeleteEarmarkedTime()).lower()
        jsCanCreateScanningSession = str(self.canCreateScanningSession()).lower()
        jsCanCreateMaintenanceSession = str(self.canCreateMaintenanceSession()).lower()
        jsCanCreateDowntimeSession = str(self.canCreateDowntimeSession()).lower()

        self.context.update({
            'dojoPrefix'    : dojoPrefix,
            'calendarDay'   : self.calendarDay,
            'calendarMonth' : self.calendarMonth,
            'calendarYear'  : self.calendarYear,
            'weekStarts'    : self.weekStarts,
            'previousStarts': self.weekStarts - mx.DateTime.oneWeek,
            'nextStarts'    : self.weekStarts + mx.DateTime.oneWeek,
            'jsCanCreateEarmarkedTime' : jsCanCreateEarmarkedTime,
            'jsCanUpdateEarmarkedTime' : jsCanUpdateEarmarkedTime,
            'jsCanDeleteEarmarkedTime' : jsCanDeleteEarmarkedTime,
            'jsCanCreateScanningSession' : jsCanCreateScanningSession,
            'jsCanCreateMaintenanceSession' : jsCanCreateMaintenanceSession,
            'jsCanCreateDowntimeSession' : jsCanCreateDowntimeSession,
        })

    def initialiseWeekTimes(self):
        if self.timeInWeek == None:
            if self.year and self.month and self.day:
                timeInWeek = mx.DateTime.Date(
                    int(self.year), int(self.month), int(self.day)
                )
                if self.session:
                    if self.session.scheduleBookmark != timeInWeek:
                        self.session.scheduleBookmark = timeInWeek
                        self.session.save()
            elif self.session and self.session.scheduleBookmark:
                timeInWeek = mx.DateTime.Date(
                    self.session.scheduleBookmark.year,
                    self.session.scheduleBookmark.month,
                    self.session.scheduleBookmark.day,
                )
            else:
                timeInWeek = mx.DateTime.now()
                if self.session:
                    self.session.scheduleBookmark = timeInWeek
                    self.session.save()
            self.setTimeInWeek(timeInWeek)
        if self.weekStarts == None:
            self.setTimesOfWeek()

    def setTimeInWeek(self, timeInWeek):
        self.timeInWeek = timeInWeek

    def setTimesOfWeek(self):
        self.weekStarts = self.calcWeekStarts(self.timeInWeek)
        self.weekEnds = self.weekStarts + mx.DateTime.oneDay * self.numberDays
        self.calendarYear = self.weekStarts.year
        self.calendarMonth = mx.DateTime.Month[self.weekStarts.month]
        self.calendarDay = self.weekStarts.day
        
    def calcWeekStarts(self, timeInWeek):
        if self.numberDays > 5:
            durationSinceMonday = timeInWeek.day_of_week * mx.DateTime.oneDay
            timeInMonday = timeInWeek - durationSinceMonday
            weekStartYear = timeInMonday.year
            weekStartMonth = timeInMonday.month
            weekStartDay = timeInMonday.day
        else:
            durationSinceMonday = timeInWeek.day_of_week * mx.DateTime.oneDay
            weekStartYear = timeInWeek.year
            weekStartMonth = timeInWeek.month
            weekStartDay = timeInWeek.day
        weekStarts = mx.DateTime.Date(
            weekStartYear,weekStartMonth,weekStartDay
        )
        return weekStarts
        

#class MonthScheduleView(WeekScheduleView):
#
#    templatePath = 'schedule/month'
#    majorNavigationItem = '/schedule/'
#    minorNavigationItem = '/schedule/month/'
#
#
#class YearScheduleView(WeekScheduleView):
#
#    templatePath = 'schedule/year'
#    majorNavigationItem = '/schedule/'
#    minorNavigationItem = '/schedule/year/'


class WeekScheduleWidget2(WeekScheduleView):

    templatePath = 'rpc2/blank'
    workingStartsHour = scanbooker.workingHours.start
    workingEndsHour   = scanbooker.workingHours.end

    def __init__(self, layerName=None, **kwds):
        super(WeekScheduleWidget2, self).__init__(**kwds)
        self.layerName = layerName
        self.earmarkedTimes = None
        self.scanningSessions = None
        self.scheduledSessions = None

    def setContext(self, **kwds):
        pass
        
    def canAccess(self):
        return True

    def markNavigation(self):
        pass

    def getJsonData(self):
        self.initialiseWeekTimes()
        self.jsonData = {}
        self.getScheduleConfigData()
        if self.getOnlyConfig():
            pass
        elif self.layerName == 'earmarks':
            self.getEarmarkData()
        elif self.layerName == 'sessions':
            self.getSessionData()
        else:
            self.getEarmarkData()
            self.getSessionData()
        self.fixupScheduleConfigData()
        return self.jsonData

    def getOnlyConfig(self):
        return not self.canUpdateSystem() and not self.isWeekPublished()

    def getScheduleConfigData(self):
        config = {}
        self.jsonData['config'] = config
        config['weekStarts'] = int(self.weekStarts)
        config['workingStartsHour'] = int(self.workingStartsHour)
        config['workingEndsHour'] = int(self.workingEndsHour)
        isWeekPublished = self.isWeekPublished()
        config['isWeekPublished'] = isWeekPublished
        week = self.findWeek()
        if self.canUpdateSystem():
            if week:
                text = ''
                config['weekNotesPrivate'] = week.notesPrivate
                config['weekNotesPublic'] = week.notesPublic
                if week.notesPublic:
                    text += '\n\nadmin notes\n\n'
                    text += week.notesPrivate
                if week.notesPublic.strip():
                    text += '\n\nunit notes\n\n'
                    text += week.notesPublic
                md = Markdown(safe_mode='escape')
                weekNotesRendered = md.convert(text)
                config['weekNotesRendered'] = weekNotesRendered
            else:
                config['weekNotesPrivate'] = ''
                config['weekNotesPublic'] = ''
                config['weekNotesRendered'] = ''
        elif isWeekPublished:
            if week:
                md = Markdown(safe_mode='escape')
                config['weekNotesRendered'] = md.convert(week.notesPublic)
            else:
                config['weekNotesRendered'] = ''
        else:
            notesPublic = 'This week is not yet published.'
            md = Markdown(safe_mode='escape')
            config['weekNotesRendered'] = md.convert(notesPublic)

    def fixupScheduleConfigData(self):
        config = self.jsonData['config']
        if not self.canUpdateSystem():
            if self.scanningSessions != None:
                count = len(self.scanningSessions)
                if count == 1:
                    notice = 'There is 1 scanning session.'
                else:
                    notice = 'There are %s scanning sessions.' % count
                md = Markdown(safe_mode='escape')
                config['weekNotesRendered'] += md.convert(notice)

    def getEarmarkData(self):
        self.jsonData['earmarks'] = {}
        self.initDayLists(self.jsonData['earmarks'])
        for earmarkedTime in self.getEarmarkedTimes():
            self.appendDayList(self.jsonData['earmarks'], earmarkedTime)

    def getSessionData(self):
        self.jsonData['sessions'] = {}
        self.initDayLists(self.jsonData['sessions'])
        for scheduledSession in self.getScheduledSessions():
            self.appendDayList(self.jsonData['sessions'], scheduledSession)

    def initDayLists(self, typeList):
        for dayName in self.findDayNames():
            typeList[dayName] = []
                
    def makeCalendarEvent(self, domainObject):
        startsEpochSecs = EpochFromDateTime(domainObject.starts).seconds()
        endsEpochSecs = EpochFromDateTime(domainObject.ends).seconds()
        calendarEvent = {
            'id': domainObject.getCalendarId(),
            'layer': domainObject.getSlotTypeName(),
            'sessionType': domainObject.getCalendarTypeName(),
            'summary': domainObject.getCalendarSummary().encode('utf-8'),
            'location': u'MRI'.encode('utf-8'),
            'dtstart': startsEpochSecs,
            'dtend': endsEpochSecs,
        }
        return calendarEvent

    def appendDayList(self, typeList, domainObject):
        dayName = self.findDayName(domainObject.starts)
        if not typeList.has_key(dayName):
            typeList[dayName] = []
        calendarEvent = self.makeCalendarEvent(domainObject)
        typeList[dayName].append(calendarEvent)
            
    def getEarmarkedTimes(self):
        if self.earmarkedTimes == None:
            self.findEarmarkedTimes()
            if len(self.earmarkedTimes) == 0:
                self.createEarmarkedTimes()
                self.findEarmarkedTimes()
        return self.earmarkedTimes
        
    def getScheduledSessions(self):
        if self.scheduledSessions == None:
            self.findScheduledSessions()
        return self.scheduledSessions
        
    def findEarmarkedTimes(self):
        earmarkedTimes = self.registry.earmarkedTimes.findDomainObjects(
            __startsBefore__    =   self.weekEnds,
            __endsAfter__       =   self.weekStarts
        )
        earmarkedTimes.sort(self.cmpStarts)
        self.earmarkedTimes = earmarkedTimes
        
    def findScheduledSessions(self):
        methodsRegister = self.registry.methodsSessions
        methodsSessions = methodsRegister.findDomainObjects(
            __startsBefore__    =   self.weekEnds,
            __endsAfter__       =   self.weekStarts
        )
        maintenanceRegister = self.registry.maintenanceSessions
        maintenanceSessions = maintenanceRegister.findDomainObjects(
            __startsBefore__    =   self.weekEnds,
            __endsAfter__       =   self.weekStarts
        )
        downtimeRegister = self.registry.downtimeSessions
        downtimeSessions = downtimeRegister.findDomainObjects(
            __startsBefore__    =   self.weekEnds,
            __endsAfter__       =   self.weekStarts
        )
        scanningRegister = self.registry.scanningSessions
        scanningSessions = scanningRegister.findDomainObjects(
            __startsBefore__    =   self.weekEnds,
            __endsAfter__       =   self.weekStarts
        )
        self.scheduledSessions = scanningSessions + methodsSessions + maintenanceSessions + downtimeSessions
        self.scheduledSessions.sort(self.cmpStarts)
        self.scanningSessions = scanningSessions

    def cmpStarts(self, x, y):
        xStarts = mx.DateTime.Date(
            x.starts.year,
            x.starts.month,
            x.starts.day,
            x.starts.hour,
            x.starts.minute,
        )
        yStarts = mx.DateTime.Date(
            y.starts.year,
            y.starts.month,
            y.starts.day,
            y.starts.hour,
            y.starts.minute,
        )
        if xStarts < yStarts:
            return -1
        elif xStarts > yStarts:
            return 1
        else:
            return 0

    def findDayName(self, dateTime):
        return mx.DateTime.Weekday[dateTime.day_of_week].lower()

    def findDayNames(self):
        return [mx.DateTime.Weekday[i].lower() for i in range(0,6)]

    def deleteEarmarkedTimes(self):
        if self.weekStarts == None:
            self.initialiseWeekTimes()
        self.findEarmarkedTimes()
        for earmarkedTime in self.earmarkedTimes:
            earmarkedTime.delete()
        self.earmarkedTimes = None

    def createEarmarkedTimes(self, templateName=None):
        if self.weekStarts == None:
            self.initialiseWeekTimes()
        weekTemplate = None
        if templateName != None:
            weekTemplate = self.registry.earmarkedTimeTemplateWeeks[templateName]
        else:
            settings = self.getDefaultSettings()
            weekTemplate = settings.earmarkTemplate
        if weekTemplate == None:
            return
        scanner = self.registry.scanners['MRI']
        oneDay = mx.DateTime.oneDay
        for earmarkedTimeTemplate in weekTemplate.earmarkedTimeTemplates:
            earmarkedTimeStarts = mx.DateTime.DateTime(
                self.weekStarts.year,
                self.weekStarts.month,
                self.weekStarts.day,
                earmarkedTimeTemplate.startsHour,
                earmarkedTimeTemplate.startsMinute
            )
            earmarkedTimeStarts += oneDay * earmarkedTimeTemplate.startsDay
            earmarkedTimeEnds = mx.DateTime.DateTime(
                self.weekStarts.year,
                self.weekStarts.month,
                self.weekStarts.day,
                earmarkedTimeTemplate.endsHour,
                earmarkedTimeTemplate.endsMinute
            )
            earmarkedTimeEnds += oneDay * earmarkedTimeTemplate.endsDay
            self.registry.earmarkedTimes.create(
                starts=earmarkedTimeStarts, ends=earmarkedTimeEnds,
                sessionType=earmarkedTimeTemplate.sessionType,
                comment=earmarkedTimeTemplate.comment,
                organisation=earmarkedTimeTemplate.organisation,
                scanner=scanner
            )


class WeekScheduleWidget(WeekScheduleView):

    templatePath = 'widgets/schedulegrid'
    workingStartsHour = scanbooker.workingHours.start
    workingEndsHour   = scanbooker.workingHours.end
    blockMinutes = [0, 15, 30, 45]
    pixelsPerMinute = 1
    pixelsPerDay = 100
    gridStartMinuteOfDay = workingStartsHour * 60
    gridEndMinuteOfDay = workingEndsHour * 60
    gridMinutesMax = gridEndMinuteOfDay - gridStartMinuteOfDay
    timeColWidth = 32
    dayRowHeight = 18
    
    def __init__(self, **kwds):
        super(WeekScheduleWidget, self).__init__(**kwds)

    def getJsonData(self):
        self.initialiseWeekTimes()
        self.createScheduleGrid()
        data = {}
        if not self.canUpdateSystem():
            if not self.isWeekVisible():
                data['notVisibleMessage'] = 'Sorry, this week is not available.'
            else:
                data['notVisibleMessage'] = ''
        data['gridWidth'] = self.gridWidth
        data['gridHeight'] = self.gridHeight
        data['calendarDay'] = self.calendarDay
        data['calendarMonth'] = self.calendarMonth
        data['calendarYear'] = self.calendarYear
        timeCells = []
        data['timeCells'] = timeCells
        for timeCell in self.gridTimeCells:
            timeCells.append(timeCell.asHash())
        dayCells = []
        data['dayCells'] = dayCells
        for dayCell in self.gridDayCells:
            dayCells.append(dayCell.asHash())
        earmarkCells = []
        data['earmarkCells'] = earmarkCells
        for earmarkCell in self.gridEarmarkedCells:
            earmarkCells.append(earmarkCell.asHash())
        sessionCells = []
        data['sessionCells'] = sessionCells
        for sessionCell in self.gridSessionCells:
            sessionCells.append(sessionCell.asHash())
        return data
        
    def takeAction(self):
        super(WeekScheduleWidget, self).takeAction()
        self.createScheduleGrid()

    def setContext(self, **kwds):
        super(WeekScheduleWidget, self).setContext(**kwds)
        self.context.update({
            'gridWidth'     : self.gridWidth,
            'gridHeight'    : self.gridHeight,
            'countPhrase'   : self.scheduleCountPhrase,
            'timeBlocks'        : self.timeBlocks,
            'days'              : self.days,
            'earmarkedTimes'    : self.earmarkedTimes,
            'scanningSessions'  : self.scanningSessions,
            'scheduledSessions' : self.scheduledSessions,
            'gridTimeCells'         : self.gridTimeCells,
            'gridDayCells'          : self.gridDayCells,
            'gridEarmarkedCells'    : self.gridEarmarkedCells,
            'gridSessionCells'      : self.gridSessionCells,
        })

    def createScheduleGrid(self):
        self.initialiseGrid()
        self.calcGridWidthHeight()
        self.createGridCells()
        self.positionGridCells()
        self.createScheduleCountPhrase()

    def initialiseGrid(self):
        self.timeBlocks         = None
        self.days               = None
        self.earmarkedTimes     = None
        self.scanningSessions   = None
        self.scheduledSessions  = None
        self.gridWidth          = None
        self.gridTimeCells      = None
        self.gridDayCells       = None
        self.gridEarmarkedCells = None
        self.gridSessionCells   = None
        
    def calcGridWidthHeight(self):
        gridWidth  = int(self.numberDays * self.pixelsPerDay)
        gridWidth  += self.timeColWidth
        self.gridWidth = gridWidth
        gridHeight = int(self.gridMinutesMax * self.pixelsPerMinute)
        gridHeight += self.dayRowHeight
        self.gridHeight = gridHeight

    def createGridCells(self):
        self.createTimeBlockCells()
        self.createDayCells()
        self.createEarmarkedCells()
        self.createSessionCells()
        
    def createTimeBlockCells(self):
        self.gridTimeCells = []
        for timeBlock in self.getTimeBlocks():
            newCell = TimeBlockGridCell(timeBlock)
            self.gridTimeCells.append(newCell)
    
    def createDayCells(self):
        self.gridDayCells = []
        for day in self.getDays():
            newCell = DayGridCell(day)
            self.gridDayCells.append(newCell)
    
    def createEarmarkedCells(self):
        self.gridEarmarkedCells = []
        for earmarkedTime in self.getEarmarkedTimes():
            newCell = EarmarkedGridCell(earmarkedTime)
            self.gridEarmarkedCells.append(newCell)

    def createSessionCells(self):
        self.gridSessionCells = []
        for session in self.getScheduledSessions():
            newCell = SessionGridCell(session)
            self.gridSessionCells.append(newCell)

    def getTimeBlocks(self):
        if self.timeBlocks == None:
            self.findTimeBlocks()
        return self.timeBlocks
        
    def getDays(self):
        if self.days == None:
            self.findDays()
        return self.days
        
    def getEarmarkedTimes(self):
        if self.earmarkedTimes == None:
            self.earmarkedTimes = self.findEarmarkedTimes()
            self.earmarkedTimes.sort(self.cmpStarts)
        return self.earmarkedTimes
        
    def getScheduledSessions(self):
        if self.scheduledSessions == None:
            self.findScheduledSessions()
        return self.scheduledSessions
        
    def findTimeBlocks(self):
        timeBlocks = []
        for hour in range(self.workingStartsHour, self.workingEndsHour):
            for minute in self.blockMinutes:
                timeBlock = TimeBlock(hour, minute)
                timeBlocks.append(timeBlock)
        self.timeBlocks = timeBlocks

    def findDays(self):
        if not self.weekStarts:
            raise Exception, "No weekStarts."
        self.days = []
        for i in range(self.numberDays):
            dayStarts = self.weekStarts + mx.DateTime.oneDay * i
            dayOfWeek = dayStarts.day_of_week
            dayHeading = mx.DateTime.Weekday[dayOfWeek][0:3] 
            dayHeading += '&nbsp;'+ str(dayStarts.day)
            day = Day(starts=dayStarts, number=dayOfWeek, name=dayHeading)
            self.days.append(day)

    def findEarmarkedTimes(self):
        return self.registry.earmarkedTimes.findDomainObjects(
            __startsBefore__    =   self.weekEnds,
            __endsAfter__       =   self.weekStarts
        )
        
    def findScheduledSessions(self):
        maintenanceRegister = self.registry.maintenanceSessions
        maintenanceSessions = maintenanceRegister.findDomainObjects(
            __startsBefore__    =   self.weekEnds,
            __endsAfter__       =   self.weekStarts
        )
        downtimeRegister = self.registry.downtimeSessions
        downtimeSessions = downtimeRegister.findDomainObjects(
            __startsBefore__    =   self.weekEnds,
            __endsAfter__       =   self.weekStarts
        )
        scanningRegister = self.registry.scanningSessions
        scanningSessions = scanningRegister.findDomainObjects(
            __startsBefore__    =   self.weekEnds,
            __endsAfter__       =   self.weekStarts
        )
        self.scheduledSessions = scanningSessions + maintenanceSessions + downtimeSessions
        self.scheduledSessions.sort(self.cmpStarts)
        self.scanningSessions = scanningSessions

    def cmpStarts(self, x, y):
        xStarts = mx.DateTime.Date(
            x.starts.year,
            x.starts.month,
            x.starts.day,
            x.starts.hour,
            x.starts.minute,
        )
        yStarts = mx.DateTime.Date(
            y.starts.year,
            y.starts.month,
            y.starts.day,
            y.starts.hour,
            y.starts.minute,
        )
        if xStarts < yStarts:
            return -1
        elif xStarts > yStarts:
            return 1
        else:
            return 0

    def positionGridCells(self):
        for cell in self.gridTimeCells:
           cell.setTopLeftWidthHeight(self)
        for cell in self.gridDayCells:
           cell.setTopLeftWidthHeight(self)
        for cell in self.gridEarmarkedCells:
           cell.setTopLeftWidthHeight(self)
        for cell in self.gridSessionCells:
           cell.setTopLeftWidthHeight(self)

    def createScheduleCountPhrase(self):
        scheduleCount = len(self.scanningSessions)
        if scheduleCount == 1:
            countStr = "is <b>one</b>"
            pluralStr = ""
        else:
            countStr = "are <b>" + str(scheduleCount) + "</b>"
            pluralStr = "s"
            
        phrase = "Week beginning <b>%s %s %s</b>." % (
            self.calendarDay, self.calendarMonth, self.calendarYear
        )
        
        #phrase += " There %s scheduled scanning session%s." % (
        #    countStr, pluralStr
        #)
        self.scheduleCountPhrase = phrase


class ClearWeekEarmarkedTimesWidget(WeekScheduleWidget):

    def createScheduleGrid(self):
        for earmarkedTime in self.findEarmarkedTimes():
            earmarkedTime.delete()
        super(ClearWeekEarmarkedTimesWidget, self).createScheduleGrid()  


class SessionScheduleWidget2(WeekScheduleWidget2):

    templatePath = 'rpc2/blank'

    def __init__(self, scheduledSession=None, **kwds):
        super(SessionScheduleWidget2, self).__init__(**kwds)
        self.scheduledSession = scheduledSession

    def canAccess(self):
        return True

    def markNavigation(self):
        pass

    def setContext(self, **kwds):
        pass

    def getJsonData(self):
        self.initialiseWeekTimes()
        domainObject = self.scheduledSession
        calendarEvent = self.makeCalendarEvent(domainObject)
        return calendarEvent 


class SessionScheduleWidget(WeekScheduleWidget):

    templatePath = 'widgets/scheduledsession'

    def __init__(self, scheduledSession=None, **kwds):
        super(SessionScheduleWidget, self).__init__(**kwds)
        self.scheduledSession = scheduledSession

    def getJsonData(self):
        self.initialiseWeekTimes()
        self.initialiseGrid()
        self.calcGridWidthHeight()
        self.cell = SessionGridCell(self.scheduledSession)
        self.cell.setTopLeftWidthHeight(self)
        data = {
            'top': self.cell.top,
            'left': self.cell.left,
            'width': self.cell.width,
            'height': self.cell.height,
            'cssClass': self.cell.cssClass,
            'registryId': self.cell.item.getRegistryId(),
            'htmlContent': self.cell.htmlContent,
            'tooltipContent': self.cell.tooltipContent,
        }
        return data

    def setContext(self, **kwds):
        self.cell = SessionGridCell(self.scheduledSession)
        self.cell.setTopLeftWidthHeight(self)
        self.context.update({
            'cell': self.cell,
        })

    def createScheduleGrid(self):
        self.initialiseGrid()
        self.calcGridWidthHeight()


class CreateScheduleView(ScheduleView):

    templatePath = 'schedule/create'
    majorNavigationItem = '/schedule/'
    minorNavigationItem = '/schedule/create/'

    def takeAction(self):
        if self.request.POST:
            sessionTypeName = self.request.POST['sessionType']
            starts = self.request.POST['starts']
            ends = self.request.POST['ends']
            redirectPath = '/%s/create/' % sessionTypeName
            redirectPath += '?starts=%s' % starts
            redirectPath += '&ends=%s' % ends
            redirectPath += '&initialise=true'
            self.setRedirect(redirectPath) 

    def setContext(self, **kwds):
        super(CreateScheduleView, self).setContext(**kwds)
        if self.year:
            year = int(self.year)
            month = int(self.month)
            day = int(self.day)
            block = str(self.block)
            if len(block) == 3:
                block = '0' + block
            hour = int(block[0] + block[1])
            minute = int(block[2] + block[3])
            second = 0 
            starts = mx.DateTime.Date(year,month,day,hour,minute,second)
            ends = starts + self.blockDuration * 6
            self.context.update({
                'starts': self.createTimeString(starts),
                'ends': self.createTimeString(ends),
            })

    def createTimeString(self, time):
        timeString = "%s-%s-%s %s:%s:%s" % (
            str(time.year),
            self.zeroPadString(time.month),
            self.zeroPadString(time.day),
            self.zeroPadString(time.hour),
            self.zeroPadString(time.minute),
            self.zeroPadString(0),
        )
        return timeString

    def zeroPadString(self, value):
        value = str(value)
        if len(value) == 1:
            return '0' + value
        elif len(value) == 2:
            return value
        raise Exception, "Value has unsupported length for conversion."

def view2(request, year=None, month=None, day=None):
    view = WeekScheduleView2(
        request=request, year=year, month=month, day=day
    )
    return view.getResponse()

def create(request, year=None, month=None, day=None, block=None):
    view = CreateScheduleView(
        request=request, year=year, month=month, day=day, block=block
    )
    return view.getResponse()


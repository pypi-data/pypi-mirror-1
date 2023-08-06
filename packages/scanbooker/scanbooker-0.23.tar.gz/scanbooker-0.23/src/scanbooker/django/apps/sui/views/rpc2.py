from scanbooker.django.apps.sui.views.base import ScanBookerView
from scanbooker.django.apps.sui.views.schedule import ClearWeekEarmarkedTimesWidget
from scanbooker.django.apps.sui.views.schedule import WeekScheduleWidget2 as WeekScheduleWidget
from scanbooker.django.apps.sui.views.schedule import SessionScheduleWidget2 as SessionScheduleWidget
from scanbooker.django.apps.sui.views.registryExtn import DuplicateWidget
from scanbooker.django.apps.sui.views.registryExtn import UpdateFormWidget2 as UpdateFormWidget
from scanbooker.django.apps.sui.views.registryExtn import UpdatePostWidget2 as UpdatePostWidget
from dm.datetimeconvertor import RNSDateTimeConvertor
import simplejson
import mx.DateTime
import datetime
from markdown import Markdown
from dm.dom.meta import HasA

# todo: Supress construction of navigation items (with all their access control calls) on widgets.
# todo: Implement do_initialiseView() RPC method.
# todo: Refused template loading/rendering bequest, not just setContext: pass with rpc2/blank
# Todo: Fix 'Access Denied' return status codes (shouldn't be 500).

moddebug = False

views = {}

class RpcView(ScanBookerView):

    def __init__(self, *args, **kwds):
        super(RpcView, self).__init__(*args, **kwds)
    
    def canAccess(self):
        return self.canReadSystem()

    def markNavigation(self):
        pass


class ScheduleSmd(RpcView):

    templatePath = 'rpc2/schedulesmd'


class JsonView(RpcView):

    def __init__(self, *args, **kwds):
        super(JsonView, self).__init__(*args, **kwds)
        self.jsonString = ''
        self.jsonHash = {'method': 'default'}
        self.jsonParams = ['']
        self.message = ''

    def createContent(self):
        try:
            self.runProcedure()
            self.dumpMessageAsJsonContent()
        except Exception, inst:
            message = "AJAX View Error: %s" % str(inst)
            self.logger.warning(message)
            raise

    def jsonStringToData(self, string):
        try:
            return simplejson.loads(string)
        except Exception, inst:
            msg = "Can't convert JSON string to data structure: %s" % string
            self.logger.error(msg)
            raise Exception(msg)

    def jsonDataToString(self, string):
        try:
            return simplejson.dumps(string)
        except Exception, inst:
            msg = "Can't convert data structure to JSON string: %s" % string
            self.logger.error(msg)
            raise Exception(msg)

    def runProcedure(self, procedureName='default'):
        self.jsonHash = {}
        if self.request.POST:
            try:
                self.jsonString = self.request.POST.keys()[0]
                #Todo? self.jsonString = self.jsonString.decode('utf-8', 'ignore')
                if moddebug and self.isDebug:
                    msg = "AJAX JSON raw string: %s" % self.jsonString
                    self.logger.debug(msg)
                self.jsonHash = self.jsonStringToData(self.jsonString)
                if moddebug and self.isDebug:
                    self.logger.debug("AJAX Request: %s" % self.jsonHash)
                procedureName = self.jsonHash['method']
                if self.isDebug:
                    self.logger.debug("AJAX Procedure: %s" % procedureName)
                self.jsonParams = self.jsonHash['params']
                if self.isDebug:
                    self.logger.debug("AJAX Params: %s" % self.jsonParams)
            except Exception, inst:
                raise Exception, "AJAX JSON Error: %s" % str(inst)
            procedureMethod = getattr(self, 'do_'+procedureName)
            procedureMethod()
        elif self.isDebug:
            self.logger.debug("AJAX Error: No POST params in HTTP request.")
            
    def dumpMessageAsJsonContent(self):
        if self.isDebug:
            self.logger.debug("AJAX Response: %s" % self.message)
        try:
            self.content = self.jsonDataToString(self.message)
        except Exception, inst:
            raise Exception, "JSON Dump Error: %s" % str(inst)
        if moddebug and self.isDebug:
            self.logger.debug("AJAX JSON: %s" % self.content)

    def do_default(self):
        self.message = 'default message'


class ScheduleService(JsonView):

    templatePath = 'rpc2/blank'

    def __init__(self, *args, **kwds):
        super(ScheduleService, self).__init__(*args, **kwds)

    def setContext(self, **kwds):
        pass

    def canAccess(self):
        return True     #  NB: Make sure access is controlled within methods.
        
    def getBookmarkTime(self):
        bookmark = self.session.scheduleBookmark
        return mx.DateTime.DateTime(
            bookmark.year,
            bookmark.month,
            bookmark.day,
            bookmark.hour,
            bookmark.minute,
            bookmark.second
        )

    def createWeekScheduleWidget(self, layerName=''):
        return WeekScheduleWidget(
            request=self.request,
            layerName=layerName,
            masterView=self,
        )

    def do_viewWeek(self):
        weekName = str(self.jsonParams[0])
        layerName = str(self.jsonParams[1])
        self.canReadSystem()
        view = self.createWeekScheduleWidget(layerName=layerName)
        if (weekName == '') or (weekName == 'current'):
            pass
        elif weekName == '':
            pass
        elif weekName.lower() == 'previous':
            bookmarkTime = self.getBookmarkTime()
            bookmarkTime -= mx.DateTime.oneWeek
            self.session.scheduleBookmark = bookmarkTime
            self.session.save()
        elif weekName.lower() == 'next':
            bookmarkTime = self.getBookmarkTime()
            bookmarkTime += mx.DateTime.oneWeek
            self.session.scheduleBookmark = bookmarkTime
            self.session.save()
        else:
            bookmarkEpochSecs = int(weekName)
            bookmarkDt = datetime.datetime.fromtimestamp(bookmarkEpochSecs)
            bookmarkTime = mx.DateTime.DateTime(
                bookmarkDt.year, bookmarkDt.month, bookmarkDt.day,
                bookmarkDt.hour, bookmarkDt.minute, bookmarkDt.second
            )
            self.session.scheduleBookmark = bookmarkTime
            self.session.save()

        self.message = view.getJsonData()

    def makeEarmarkSessionTypeName(self, timeSlotSessionTypeName):
        sessionTypes = {
            'cleaning': 'Cleaning',
            'closed':   'Closed',
            'otherUse': 'Other Use',
            'reserved': 'Reserved',
            'scanning': 'Scanning',
        }
        if timeSlotSessionTypeName in sessionTypes:
            return sessionTypes[timeSlotSessionTypeName]
        else:
            return sessionTypes['scanning']

    def makeSessionClassName(self, timeSlotSessionTypeName):
        sessionClasses = {
            'maintenance': 'MaintenanceSession',
            'methods': 'MethodsSession',
            'scanning': 'ScanningSession',
            'downtime': 'DowntimeSession',
        }
        if timeSlotSessionTypeName in sessionClasses:
            return sessionClasses[timeSlotSessionTypeName]
        else:
            return sessionClasses['scanning']

    def do_createTimeSlot(self):
        timeSlotData = self.jsonParams[0]
        startsEpochSecs = int(timeSlotData['dtstart'])
        startsDt = datetime.datetime.fromtimestamp(startsEpochSecs)
        timeSlotStarts = mx.DateTime.DateTime(
            startsDt.year, startsDt.month, startsDt.day,
            startsDt.hour, startsDt.minute, startsDt.second
        )
        endsEpochSecs = int(timeSlotData['dtend'])
        endsDt = datetime.datetime.fromtimestamp(endsEpochSecs)
        timeSlotEnds = mx.DateTime.DateTime(
            endsDt.year, endsDt.month, endsDt.day,
            endsDt.hour, endsDt.minute, endsDt.second
        )
        timeSlotLayerName = timeSlotData['layer']
        timeSlotSessionTypeName = timeSlotData['sessionType']
        if timeSlotLayerName == 'earmark':
            sessionTypeName = self.makeEarmarkSessionTypeName(timeSlotSessionTypeName)
            sessionType = self.registry.sessionTypes[sessionTypeName]
            timeSlotClass = self.registry.getDomainClass('EarmarkedTime')
            if not self.canCreate(timeSlotClass):
                raise Exception("Access Denied")
            timeSlotRegister = timeSlotClass.createRegister()
            timeSlot = timeSlotRegister.create(
                starts=timeSlotStarts,
                ends=timeSlotEnds,
                sessionType=sessionType,
            )
        elif timeSlotLayerName == 'session':
            sessionClassName = self.makeSessionClassName(timeSlotSessionTypeName)
            timeSlotClass = self.registry.getDomainClass(sessionClassName)
            if not self.canCreate(timeSlotClass):
                raise Exception("Access Denied")
            timeSlotRegister = timeSlotClass.createRegister()
            timeSlot = timeSlotRegister.create(
                starts=timeSlotStarts,
                ends=timeSlotEnds,
                createdBy=self.session.person,
            )
        view = SessionScheduleWidget(
            request=self.request,
            masterView=self,
            scheduledSession=timeSlot,
        )
        self.message = view.getJsonData()

    def do_updateTimeSlot(self):
        """Consumes dict with keys ('id', 'dtstart', 'dtend')."""
        isChanged = False
        timeSlotData = self.jsonParams[0]
        timeSlotId = timeSlotData['id']
        domainClassName, domainObjectId = timeSlotId.split('.')
        domainObjectId = int(domainObjectId)
        timeSlotClass = self.registry.getDomainClass(domainClassName)
        timeSlotRegister = timeSlotClass.createRegister()
        timeSlot = timeSlotRegister[domainObjectId]
        if 'dtstart' in timeSlotData and 'dtend' in timeSlotData:
            if not self.canUpdate(timeSlot):
                raise Exception("Access Denied")
            timeSlotStartsEpochSecs = int(timeSlotData['dtstart'])
            starts = datetime.datetime.fromtimestamp(timeSlotStartsEpochSecs)
            timeSlotStarts = mx.DateTime.DateTime(
                starts.year, starts.month, starts.day,
                starts.hour, starts.minute, starts.second
            )
            if timeSlot.starts != timeSlotStarts:
                timeSlot.starts = timeSlotStarts
                isChanged = True
            timeSlotEndsEpochSecs = int(timeSlotData['dtend'])
            ends = datetime.datetime.fromtimestamp(timeSlotEndsEpochSecs)
            timeSlotEnds = mx.DateTime.DateTime(
                ends.year, ends.month, ends.day,
                ends.hour, ends.minute, ends.second
            )
            if timeSlot.ends != timeSlotEnds:
                timeSlot.ends = timeSlotEnds
                isChanged = True
            if isChanged:
                timeSlot.save()
        else:  # Just checking for new data.
            if not self.canRead(timeSlot):
                raise Exception("Access Denied")
        view = SessionScheduleWidget(
            request=self.request,
            masterView=self,
            scheduledSession=timeSlot,
        )
        self.message = view.getJsonData()

    def do_deleteTimeSlot(self):
        timeSlotData = self.jsonParams[0]
        timeSlotId = timeSlotData['id']
        domainClassName, domainObjectId = timeSlotId.split('.')
        domainObjectId = int(domainObjectId)
        timeSlotClass = self.registry.getDomainClass(domainClassName)
        timeSlotRegister = timeSlotClass.createRegister()
        timeSlot = timeSlotRegister[domainObjectId]
        if not self.canDelete(timeSlot):
            raise Exception("Access Denied")
        timeSlot.delete()
        self.message = timeSlotData

    def do_duplicateTimeSlot(self):
        # Pull data from JSON params. 
        timeSlotData = self.jsonParams[0]
        # Get object to be duplicated.
        timeSlotId = timeSlotData['id']
        domainClassName, domainObjectId = timeSlotId.split('.')
        timeSlotClass = self.registry.getDomainClass(domainClassName)
        timeSlotRegister = timeSlotClass.createRegister()
        domainObjectId = int(domainObjectId)
        timeSlot = timeSlotRegister[domainObjectId]
        # Get start time of new object.
        startsEpochSecs = int(timeSlotData['dtstart'])
        startsDt = datetime.datetime.fromtimestamp(startsEpochSecs)
        timeSlotStarts = mx.DateTime.DateTime(
            startsDt.year, startsDt.month, startsDt.day,
            startsDt.hour, startsDt.minute, startsDt.second
        )
        # Control access.
        if not self.canRead(timeSlot) or not self.canCreate(timeSlotClass):
            raise Exception("Access Denied")
        # Duplicate at new start time.
        if self.isDebug:
            msg = "Duplicating timeSlot %s at time %s." % (
                timeSlot, timeSlotStarts
            )
            self.logger.debug(msg)
        try:
            newTimeSlot = timeSlot.duplicateAt(timeSlotStarts, timeSlotRegister)
        except Exception, inst:
            self.message = {
                'error': "Couldn't duplicate time slot (%s): %s" % (timeSlotData, inst) 
            } 
        # Prepare RPC response message.
        view = SessionScheduleWidget(
            request=self.request,
            masterView=self,
            scheduledSession=newTimeSlot,
        )
        self.message = view.getJsonData()

    def do_getEarmarkTemplateNames(self):
        if not self.canCreateEarmarkedTime():
            self.message = []
        else:
            self.message = self.registry.earmarkedTimeTemplateWeeks.keys()

    def do_earmarkCurrentWeek(self):
        if not self.canCreateEarmarkedTime():
            return
        templateName = str(self.jsonParams[0])
        view = self.createWeekScheduleWidget()
        view.initialiseWeekTimes()
        view.deleteEarmarkedTimes()
        view.createEarmarkedTimes(templateName)
        self.message = view.getJsonData()

    def do_createEarmarkTemplate(self):
        if not self.canCreateEarmarkedTime():
            return
        templateName = str(self.jsonParams[0])
        view = self.createWeekScheduleWidget()
        view.initialiseWeekTimes()
        templateRegister = self.registry.earmarkedTimeTemplateWeeks
        if templateName in templateRegister:
            weekTemplate = templateRegister[templateName]
            for e in weekTemplate.earmarkedTimeTemplates:
                e.delete()
        else:
            weekTemplate = templateRegister.create(templateName)
        earmarkedTimes = view.getEarmarkedTimes()
        for earmarkedTime in earmarkedTimes:
            weekTemplate.earmarkedTimeTemplates.create(
                sessionType=earmarkedTime.sessionType,
                comment=earmarkedTime.comment,
                organisation=earmarkedTime.organisation,
                startsDay=(earmarkedTime.starts - view.weekStarts).day,
                startsHour=earmarkedTime.starts.hour,
                startsMinute=earmarkedTime.starts.minute,
                endsDay=(earmarkedTime.ends - view.weekStarts).day,
                endsHour=earmarkedTime.ends.hour,
                endsMinute=earmarkedTime.ends.minute,
            )

    def do_deleteEarmarkTemplate(self):
        if not self.canDeleteEarmarkedTime():
            return
        templateName = str(self.jsonParams[0])
        templateRegister = self.registry.earmarkedTimeTemplateWeeks
        if templateName in templateRegister:
            del(templateRegister[templateName])
        self.message = True

    def do_getTimeSlotUpdateForm(self):
        timeSlotData = self.jsonParams[0]
        timeSlotId = timeSlotData['id']
        domainClassName, domainObjectId = timeSlotId.split('.')
        domainObjectId = int(domainObjectId)
        timeSlotClass = self.registry.getDomainClass(domainClassName)
        timeSlotRegister = timeSlotClass.createRegister()
        timeSlot = timeSlotRegister[domainObjectId]
        if not self.canUpdate(timeSlot):
            raise Exception("Access Denied")
        view = UpdateFormWidget(
            request=self.request,
            masterView=self,
            domainObject=timeSlot,
        )
        self.message = view.getJsonData()

    def do_getWeekIsPublished(self):
        view = self.createWeekScheduleWidget()
        self.message = view.isWeekPublished()

    def do_setWeekIsPublished(self):
        if not self.canUpdateSystem():
            return
        messageData = self.jsonParams[0]
        isPublished = messageData['isPublished']
        view = self.createWeekScheduleWidget()
        if isPublished:
            view.publishWeek()
        else:
            view.hideWeek()
        week = view.findWeek()
        self.message = view.isWeekPublished()

    def do_setWeekNotes(self):
        if not self.canUpdateSystem():
            return
        messageData = self.jsonParams[0]
        notesPublic = messageData['notesPublic']
        notesPrivate = messageData['notesPrivate']
        view = self.createWeekScheduleWidget()
        week = view.getWeek()
        week.notesPublic = notesPublic
        week.notesPrivate = notesPrivate
        week.save()
        md = Markdown(safe_mode='escape')
        text = ''
        if notesPrivate.strip():
            text += '\n\nadmin notes\n\n'
            text += notesPrivate
        if notesPublic.strip():
            text += '\n\nunit notes\n\n'
            text += notesPublic
        weekNotesRendered = md.convert(text)
        self.message = {'weekNotesRendered': weekNotesRendered}


class ReportSmd(RpcView):

    templatePath = 'rpc2/reportsmd'


class ReportService(JsonView):

    templatePath = 'rpc2/blank'

    def __init__(self, *args, **kwds):
        super(ReportService, self).__init__(*args, **kwds)

    def setContext(self, **kwds):
        pass

    def canAccess(self):
        return True     #  NB: Make sure access is controlled within methods.
        
    def do_getReportFilters(self):
        if not self.canUpdateSystem():
            self.message = {
                'filters': []
            }
            return
        reportId = int(self.jsonParams[0])
        report = self.registry.reports[reportId]
        filters = report.listFilters()
        self.message = {
            'filters': [self.createFilterMessage(c) for c in filters]
        }

    def do_getReportColumns(self):
        if not self.canUpdateSystem():
            self.message = {
                'columns': []
            }
            return
        reportId = int(self.jsonParams[0])
        report = self.registry.reports[reportId]
        columns = report.listColumns()
        self.message = {
            'columns': [self.createColumnMessage(c) for c in columns]
        }

    def do_insertFilter(self):
        if not self.canUpdateSystem():
            return
        reportId = int(self.jsonParams[0])
        try:
            filterId = int(self.jsonParams[1])
        except:
            filterId = 0
        report = self.registry.reports[reportId]
        if filterId:
            refFilter = self.registry.reportFilters[filterId]
            newFilter = report.filters.create(
                next=refFilter, previous=refFilter.previous
            )
            if refFilter.previous:
                refFilter.previous.next = newFilter
                refFilter.previous.save()
            refFilter.previous = newFilter
            refFilter.save()
        else:
            lastFilter = None
            filters = report.listFilters()
            lastFilter = None
            if len(filters):
                lastFilter = filters[-1]
            newFilter = report.filters.create(
                next=None, previous=lastFilter
            )
            if lastFilter:
                lastFilter.next = newFilter
                lastFilter.save()
        self.message = self.createFilterMessage(newFilter)

    def do_insertColumn(self):
        if not self.canUpdateSystem():
            return
        reportId = int(self.jsonParams[0])
        try:
            columnId = int(self.jsonParams[1])
        except:
            columnId = 0
        report = self.registry.reports[reportId]
        if columnId:
            refColumn = self.registry.reportColumns[columnId]
            newColumn = report.columns.create(
                next=refColumn, previous=refColumn.previous
            )
            if refColumn.previous:
                refColumn.previous.next = newColumn
                refColumn.previous.save()
            refColumn.previous = newColumn
            refColumn.save()
        else:
            lastColumn = None
            columns = report.listColumns()
            lastColumn = None
            if len(columns):
                lastColumn = columns[-1]
            newColumn = report.columns.create(
                next=None, previous=lastColumn
            )
            if lastColumn:
                lastColumn.next = newColumn
                lastColumn.save()
        self.message = self.createColumnMessage(newColumn)

    def do_updateReportTitle(self):
        if not self.canUpdateSystem():
            return
        reportId = int(self.jsonParams[0])
        reportTitle = self.jsonParams[1]
        report = self.registry.reports[reportId]
        report.title = reportTitle
        report.save()
        self.message = True

    def do_updateFilterName(self):
        if not self.canUpdateSystem():
            return
        filterId = int(self.jsonParams[0])
        filterName = self.jsonParams[1]
        filter = self.registry.reportFilters[filterId]
        filter.setName(filterName)
        self.message = self.createFilterMessage(filter)

    def do_updateFilterMode(self):
        if not self.canUpdateSystem():
            return
        filterId = int(self.jsonParams[0])
        filterMode = self.jsonParams[1]
        filter = self.registry.reportFilters[filterId]
        filter.mode = filterMode
        filter.save()
        self.message = self.createFilterMessage(filter)

    def do_updateFilterValue(self):
        if not self.canUpdateSystem():
            return
        filterId = int(self.jsonParams[0])
        filterValue = self.jsonParams[1]
        filter = self.registry.reportFilters[filterId]
        filter.value = filterValue
        filter.save()
        self.message = self.createFilterMessage(filter)

    def do_updateColumnName(self):
        if not self.canUpdateSystem():
            return
        columnId = int(self.jsonParams[0])
        columnName = self.jsonParams[1]
        column = self.registry.reportColumns[columnId]
        column.name = columnName
        column.qual = ''
        column.save()
        self.message = self.createColumnMessage(column)

    def do_updateColumnQual(self):
        if not self.canUpdateSystem():
            return
        columnId = int(self.jsonParams[0])
        columnQual = self.jsonParams[1]
        column = self.registry.reportColumns[columnId]
        column.qual = columnQual
        column.save()
        self.message = self.createColumnMessage(column)

    def do_deleteFilter(self):
        if not self.canUpdateSystem():
            return
        filterId = int(self.jsonParams[0])
        filter = self.registry.reportFilters[filterId]
        filter.delete()
        self.message = self.createFilterMessage(filter)

    def do_deleteColumn(self):
        if not self.canUpdateSystem():
            return
        columnId = int(self.jsonParams[0])
        column = self.registry.reportColumns[columnId]
        column.delete()
        self.message = self.createColumnMessage(column)

    def createFilterMessage(self, filter):
        return {
            'filter': filter.asDictValues(),
            'filterId': filter.id,
            'filterType': filter.decideType(),
            'nameOptions': self.getFilterNameOptions(filter),
            'modeOptions': self.getFilterModeOptions(filter),
            'selectionOptions': self.getFilterSelectionOptions(filter),
        }

    def createColumnMessage(self, column):
        msg = {
            'column': column.asDictValues(),
            'nameOptions': self.getColumnNameOptions(column),
            'qualOptions': self.getColumnQualOptions(column),
        }
        msg['column']['id'] = column.id
        return msg

    def getFilterModeOptions(self, filter):
        return [(o, o) for o in filter.getModeOptions()]

    def getFilterNameOptions(self, filter):
        keys = filter.getNameOptions()
        return [
            ('', ' -- select option -- '),
            ('id', 'id'),
        ] + [(o,o) for o in keys]

    def getFilterSelectionOptions(self, filter):
        filterType = filter.decideType()
        options = []
        if filterType == 'Selection':
            if filter.name == 'id':
                 metaAttr = HasA(filter.report.against)
                 options = [('', 'None')]
                 options += metaAttr.getAllChoices(None)
            else:
                meta = filter.report.getAgainstClass().meta
                if filter.name in meta.attributeNames:
                    metaAttr = meta.attributeNames[filter.name]
                    options = [('', 'None')]
                    options += metaAttr.getAllChoices(None)
        return options

    def getColumnNameOptions(self, column):
        keys = column.getNameOptions()
        return [
            ('', ' -- select option -- '),
            ('id', 'id'),
        ] + [(o,o) for o in keys]

    def getColumnQualOptions(self, column):
        keys = column.getQualOptions()
        return keys


class RpcUpdatePostView(JsonView):

    templatePath = 'rpc2/blank'

    def __init__(self, registryPath, *args, **kwds):
        super(RpcUpdatePostView, self).__init__(*args, **kwds)
        self.registryPath = registryPath
    
    def setContext(self, **kwds):
        pass

    def runProcedure(self):
        view = UpdatePostWidget(
            request=self.request,
            masterView=self,
            registryPath=self.registryPath,
            actionName='update',
        )
        self.message = view.getJsonData()


views['schedulesmd']    = ScheduleSmd
views['schedule']       = ScheduleService
views['reportsmd']    = ReportSmd
views['report']       = ReportService


def view(request, viewName=None):
    viewClass = views[viewName]
    view = viewClass(request=request)
    return view.getResponse()

def updatepost(request, registryPath):
    view = RpcUpdatePostView(
        request=request,
        registryPath=registryPath
    )
    return view.getResponse()


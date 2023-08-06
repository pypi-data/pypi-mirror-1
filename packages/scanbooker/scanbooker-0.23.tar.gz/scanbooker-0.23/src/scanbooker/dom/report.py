from dm.dom.stateful import *
import mx.DateTime

# Todo: Reintroduce associating researchers with reports, so they can see them?

class Report(DatedStatefulObject):

    isUnique = False
    title = String()
    against = String(default='ScanningSession')
    filters = AggregatesMany('ReportFilter', 'id')
    columns = AggregatesMany('ReportColumn', 'id')

    searchAttributeNames = ['title']
    startsWithAttributeName = 'title'

    def getLabelValue(self):
        return self.title

    def getAgainstClass(self):
        return self.registry.getDomainClass(self.against)

    def listColumns(self):
        columns = []
        column = self.columns.findSingleDomainObject(previous=None)
        while column:
            columns.append(column)
            column = column.next
        return columns
    
    def listFilters(self):
        filters = []
        filter = self.filters.findSingleDomainObject(previous=None)
        while filter:
            filters.append(filter)
            filter = filter.next
        return filters
    
    def listHeadings(self):
        headings = []
        for column in self.listColumns():
            heading = column.name
            if column.qual not in ['label', 'value']:
                heading += ' %s' % column.qual
            headings.append(heading)
        return headings

    def listColumnNames(self):
        names = []
        for column in self.listColumns():
            if column.name:
                names.append(column.name)
        return names

    def createAgainstRegister(self):
        return self.registry.getDomainClass(self.against).createRegister()

    def generateData(self):
        self.labelRows = []
        try:
            register = self.createAgainstRegister()
            if not self.listColumnNames():
                return [['Please add some column names.']]
            valueRows = []
            domainFilter = self.createDomainFilter()
            metaAttrs = self.getMetaAttrs()
            columns = self.listColumns()
            try:
                filteredDomainObjects = register.findDomainObjects(**domainFilter)
            except Exception, inst:
                # Todo: Log this error.
                return [['error: %s' % repr(inst)]]
            if not filteredDomainObjects:
                return [['The filter isn\'t matching anything.']]
            for domainObject in filteredDomainObjects:
                #raise Exception, repr(domainObject)
                row = []
                valueRows.append(row)
                values = domainObject.asSortableValues()
                for column in columns:
                    if column.name == '':
                        continue
                    elif column.name == 'id':
                        value = domainObject.id
                    elif column.name == 'duration' and 'starts' in metaAttrs \
                    and 'ends' in metaAttrs and 'duration' not in metaAttrs:
                        starts = domainObject.starts
                        ends = domainObject.ends
                        duration = ends - starts
                        value = duration
                    elif column.name == 'start' and 'starts' in metaAttrs \
                    and 'ends' in metaAttrs and 'start' not in metaAttrs \
                    and 'end' not in metaAttrs and 'date' not in metaAttrs:
                        start = domainObject.starts.strftime("%H:%M")
                        value = start
                    elif column.name == 'end' and 'starts' in metaAttrs \
                    and 'ends' in metaAttrs and 'start' not in metaAttrs \
                    and 'end' not in metaAttrs and 'date' not in metaAttrs:
                        end = domainObject.ends.strftime("%H:%M")
                        value = end
                    elif column.name == 'date' and 'starts' in metaAttrs \
                    and 'ends' in metaAttrs and 'start' not in metaAttrs \
                    and 'end' not in metaAttrs and 'date' not in metaAttrs:
                        date = mx.DateTime.Date(
                            domainObject.starts.year,
                            domainObject.starts.month,
                            domainObject.starts.day,
                        )
                        value = date
                    else:
                        value = values[column.name]
                    row.append(value)
                row.append(domainObject)
            valueRows.sort()
            for domainObject in [row[-1] for row in valueRows]:
                row = []
                self.labelRows.append(row)
                labels = domainObject.asDictLabels()
                values = domainObject.asDictValues()
                for column in columns:
                    item = ''
                    metaAttr = self.getMetaAttr(column.name)
                    if metaAttr:
                        if metaAttr.isDomainObjectRef:
                            refObject = getattr(domainObject, column.name)
                            if refObject:
                                if column.qual in refObject.meta.attributeNames:
                                    refLabels = refObject.asDictLabels()
                                    item = refLabels[column.qual]
                                elif column.qual == 'label':
                                    item = refObject.getLabelValue()
                                elif column.qual == 'id':
                                    item = "#%s" % refObject.id
                                else:
                                    item = refObject.getLabelValue()
                        else:
                            if column.qual == 'value':
                                item = values[column.name]
                            elif column.qual == 'label':
                                item = labels[column.name]
                            else:
                                item = labels[column.name]
                    elif column.name == 'id':
                        item = '#%d' % domainObject.id
                    elif column.name == 'duration' and 'starts' in metaAttrs \
                    and 'ends' in metaAttrs and 'duration' not in metaAttrs:
                        starts = domainObject.starts
                        ends = domainObject.ends
                        duration = ends - starts
                        value = duration
                        item = int(value.minutes)
                    elif column.name == 'start' and 'starts' in metaAttrs \
                    and 'ends' in metaAttrs and 'start' not in metaAttrs \
                    and 'end' not in metaAttrs and 'date' not in metaAttrs:
                        start = domainObject.starts.strftime("%H:%M")
                        value = start
                        item = value
                    elif column.name == 'end' and 'starts' in metaAttrs \
                    and 'ends' in metaAttrs and 'start' not in metaAttrs \
                    and 'end' not in metaAttrs and 'date' not in metaAttrs:
                        end = domainObject.ends.strftime("%H:%M")
                        value = end
                        item = value
                    elif column.name == 'date' and 'starts' in metaAttrs \
                    and 'ends' in metaAttrs and 'start' not in metaAttrs \
                    and 'end' not in metaAttrs and 'date' not in metaAttrs:
                        date = mx.DateTime.Date(
                            domainObject.starts.year,
                            domainObject.starts.month,
                            domainObject.starts.day,
                        )
                        # Todo: Convert with the model date attribute?
                        value = date.strftime("%d-%m-%Y")
                        item = value
                    row.append(item)
            return self.labelRows
        except Exception, inst:
            msg = "Couldn't generate data: %s" % inst
            raise 

    def generateSummary(self):
        try:
            summaries = []
            if not self.labelRows:
                return [''] * len(self.listColumns())
            types = []
            for item in self.labelRows[0]:
                if type(item) == type(1):
                    types.append(int)
                    summaries.append(0)
                else:
                    types.append(int)
                    summaries.append('')
            for row in self.labelRows:
                for (i, item) in enumerate(row):
                    if types[i] == int and type(item) == type(1):
                        summaries[i] += item
            return summaries
        except Exception, inst:
            msg = "Couldn't generate summary: %s" % inst
            raise Exception, msg

    def createDomainFilter(self):
        domainFilter = {}
        for filter in self.filters:
            filterName = filter.name
            filterName = str(filterName) # Python keywords must be strings.
            if filter.name == '':
                continue
            if filter.name == 'id' and filter.value == '':
                continue
            if filter.mode == 'less than':
                filterName = '__%sBefore__' % filterName
            elif filter.mode == 'greater than':
                filterName = '__%sAfter__' % filterName
            domainValue = filter.getDomainValue()
            domainFilter[filterName] = domainValue
        return domainFilter

    def getDomainValue(self, filter):
        if filter.name == 'id':
            return filter.value
        metaAttr = self.getMetaAttr(filter.name)
        if metaAttr:
            return metaAttr.makeValueFromMultiValueDict({
                filter.name: filter.value
            })
        return filter.value

    def getValueLabel(self, filter):
        if filter.name == 'id':
            return filter.value
        metaAttr = self.getMetaAttr(filter.name)
        if metaAttr:
            domainValue = metaAttr.makeValueFromMultiValueDict({
                filter.name: filter.value
            })
            class A(object): pass
            a = A()
            setattr(a, filter.name, domainValue)
            return metaAttr.createLabelRepr(a)
        return filter.value

    def getMetaAttr(self, attrName):
        attributes = self.getMetaAttrs()
        if attrName in attributes:
            return attributes[attrName]
        return None

    def getMetaAttrs(self):
        return self.getAgainstClass().meta.attributeNames


class ReportDefinition(DatedStatefulObject):

    previous = None
    next = None

    def getNameOptions(self):
        metaAttrs = self.report.getMetaAttrs()
        options = []
        for metaAttr in metaAttrs.values():
            if self.excludeAttr(metaAttr):
                continue
            else:
                options.append(metaAttr.name)
        options.sort()
        return options

    def excludeAttr(self, metaAttr):
        return False

    def delete(self):
        self.removeFromLinkedList()
        super(ReportDefinition, self).delete()

    def removeFromLinkedList(self):
        # Extract from list.
        if self.next and self.previous:  # Middle of list.
            self.previous.next = self.next
            self.previous.save()
            self.next.previous = self.previous
            self.next.save()
            self.next = None
            self.previous = None
            self.save()
        elif self.next:  # First in list.
            self.next.previous = None
            self.next.save()
            self.next = None
            self.save()
        elif self.previous:  # Last in list.
            self.previous.next = None
            self.previous.save()
            self.previous = None
            self.save()
        else:  # Alone in list.
            pass


class ReportFilter(ReportDefinition):

    isUnique = False
    name = String()
    mode = String()
    value = String()
    report = HasA('Report')
    previous = HasA('ReportFilter', isRequired=False)
    next = HasA('ReportFilter', isRequired=False)

    def excludeAttr(self, metaAttr):
        return metaAttr.isAssociateList

    def initialise(self, register=None):
        self.resetModeAndValue()

    def setName(self, name):
        self.name = name
        self.resetModeAndValue()

    def resetModeAndValue(self):
        modeOptions = self.getModeOptions()
        if modeOptions:
            self.mode = modeOptions[0]
        else:
            self.mode = ''
        self.value = ''
        self.save()

    def getModeOptions(self):
        filterType = self.decideType()
        if filterType == 'Date':
            options = [
                'equal to',
                'greater than',
                'less than',
            ]
        else:
            options = [
                'equal to',
            ]
        return options

    def getDomainValue(self):
        return self.report.getDomainValue(self)

    def getValueLabel(self):
        return self.report.getValueLabel(self)

    def decideType(self):
        filterType = 'Unsupported'
        metaAttr = self.report.getMetaAttr(self.name)
        if metaAttr:
            if metaAttr.isValueRef:
                if metaAttr.isDateTime:
                    filterType = 'Date'
                elif metaAttr.isBoolean:
                    filterType = 'Check'
                else:
                    filterType = 'Text'
            elif metaAttr.isDomainObjectRef:
                filterType = 'Selection'
        elif self.name == 'id':
            filterType = 'Selection'
        return filterType


class ReportColumn(ReportDefinition):

    isUnique = False
    name = String(default='')
    qual = String(default='label')
    report = HasA('Report')
    previous = HasA('ReportColumn', isRequired=False)
    next = HasA('ReportColumn', isRequired=False)

    def getNameOptions(self):
        options = super(ReportColumn, self).getNameOptions()
        if 'starts' in options:
            if 'ends' in options:
                if 'duration' not in options:
                    options += ['duration']
                    options.sort()
                if 'start' not in options and 'end' not in options \
                and 'date' not in options:
                    options += ['start']
                    options += ['end']
                    options += ['date']
                    options.sort()
        return options

    def getQualOptions(self):
        metaAttr = self.report.getMetaAttr(self.name)
        if not metaAttr:
            options = ['label']
        elif metaAttr.isValueRef:
            options = [
                'label',
                'value',
            ]
        elif metaAttr.isDomainObjectRef:
            domainClass = metaAttr.getDomainClass()
            options = ['label', 'id']
            attrNames = domainClass.meta.attributeNames.keys()
            attrNames.sort()
            options += attrNames
        else:
            options = ['label']
        return options


#class Report(StatefulObject):
#
#    isUnique = False
#
#    reportedClassName = String(default='ScanningSession')
#    breakdownAttributeName = String(default='')
#    starts = RDate()
#    ends = RDate()
#    periodTypeName = String(default='Monthly')
#    periodAttributeName = String(default='starts')
#    runRecordCount = Boolean(default=True)
#    runStartsEndsDuration = Boolean(default=True)
#    reportsTo = AggregatesMany('ReportResearcher', 'researcher')
#
#    def getLabelValue(self):
#        return "%s %s by %s" % (
#            self.periodTypeName,
#            self.reportedClassName,
#            self.breakdownAttributeName
#        )
#        
#    def isPeriodTypeNameSupported(self):
#        return self.periodTypeName in ['Monthly', 'Yearly' 'Annual']
#        
#    def generate(self):
#        domainClass = self.registry.getDomainClass(self.reportedClassName)
#        register = domainClass.createRegister()
#        self.intervals = []
#        if self.isPeriodTypeNameSupported():
#            self.intervals = []
#            ends = self.starts
#            while(ends < self.ends):
#                starts = ends
#                ends = self.calcIntervalEnds(starts)
#                interval = {}
#                interval['starts'] = starts
#                interval['ends'] = ends
#                interval['objectList'] = None
#                interval['recordCount'] = None
#                interval['recordStartsEndsDuration'] = None
#                self.intervals.append(interval)
#        else:
#            msg = "Period type name not supported: '%s'" % self.periodTypeName
#            raise Exception(msg)
#            
#        for interval in self.intervals:
#            kwds = {}
#            perAttrName = self.periodAttributeName
#            if not perAttrName:
#                continue
#            afterKwdsName = '__%sAfter__' % perAttrName
#            beforeKwdsName = '__%sBefore__' % perAttrName
#            kwds[afterKwdsName] = interval['starts']
#            kwds[beforeKwdsName] = interval['ends']
#            objectList = register.findDomainObjects(**kwds)
#            interval['objectList'] = objectList
#            if self.runRecordCount:
#                interval['recordCount'] = len(objectList)
#            if self.runStartsEndsDuration:
#                duration = mx.DateTime.DateTimeDelta(0)
#                for domainObject in objectList:
#                    duration += domainObject.ends - domainObject.starts
#                interval['recordStartsEndsDuration'] = duration
#
#        for interval in self.intervals:
#            breakdowns = {}
#            for object in interval['objectList']:
#                if not self.breakdownAttributeName:
#                    continue
#                value = getattr(object, self.breakdownAttributeName)
#                if not value in breakdowns:
#                    breakdowns[value] = {}
#                    breakdowns[value]['objectList'] = []
#                    breakdowns[value]['value'] = value
#                breakdowns[value]['objectList'].append(object)
#            for value in breakdowns:
#                breakdown = breakdowns[value]
#                self.runMethods(breakdown)
#            interval['breakdowns'] = breakdowns
#
#        recordCount = 0
#        recordDuration = mx.DateTime.DateTimeDelta(0)
#        for interval in self.intervals:
#            if self.runRecordCount:
#                recordCount += interval['recordCount']
#            if self.runStartsEndsDuration:
#                recordDuration += interval['recordStartsEndsDuration']
#        if self.runRecordCount:
#            self.recordCount = recordCount
#        if self.runStartsEndsDuration:
#            self.recordStartsEndsDuration = recordDuration
#        report = {}
#        report['intervals'] = self.intervals
#        if self.runRecordCount:
#            report['recordCount'] = self.recordCount
#        if self.runStartsEndsDuration:
#            report['recordStartsEndsDuration'] = self.recordStartsEndsDuration
#        self.report = report
#        return ''
#        
#    def runMethods(self, report):
#        if self.runStartsEndsDuration:
#            recordCount = 0
#            duration = mx.DateTime.DateTimeDelta(0)
#            for domainObject in report['objectList']:
#                duration += domainObject.ends - domainObject.starts
#                recordCount += 1
#            report['recordStartsEndsDuration'] = duration
#        elif self.runRecordCount:
#            recordCount = len(report['objectList'])
#        if self.runRecordCount:
#            report['recordCount'] = recordCount
#        
#    def calcIntervalEnds(self, starts):
#        if self.periodTypeName == 'Monthly':
#            ends = mx.DateTime.DateTime(
#                starts.year, starts.month, starts.day, 0,0,0)
#            while(ends.day == 1):
#                ends = ends + mx.DateTime.oneDay
#            while(ends.day != 1):
#                ends = ends + mx.DateTime.oneDay
#        elif self.periodTypeName == 'Quarterly':
#            ends = mx.DateTime.DateTime(
#                starts.year, starts.month, starts.day, 0,0,0)
#            while(ends.month in [1,4,7,10]):
#                ends = ends + mx.DateTime.oneDay
#            while(ends.month not in [1,4,7,10]):
#                ends = ends + mx.DateTime.oneDay
#        elif self.periodTypeName == 'Annual':
#            ends = mx.DateTime.DateTime(
#                starts.year, starts.month, starts.day, 0,0,0)
#            while(ends.month == 1):
#                ends = ends + mx.DateTime.oneDay
#            while(ends.month != 1):
#                ends = ends + mx.DateTime.oneDay
#        else:
#            msg = "Period type name not supported: '%s'" % self.periodTypeName
#            raise Exception(msg)
#        return ends
#
#
#class ReportResearcher(DatedStatefulObject):
#    
#    report = HasA('Report')
#    researcher = HasA('Researcher')
#            
##    def getLabelValue(self):
##        return "%s-%s" % (
##            self.report.getLabelValue(),
##            self.researcher.realname
##        )
#
#
#

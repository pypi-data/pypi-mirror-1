from dm.view.registry import RegistryUpdateView
from scanbooker.django.apps.sui.views.registry import ScanBookerRegistryCreateView
from scanbooker.django.apps.sui.views.registry import ScanBookerRegistryUpdateView
from scanbooker.django.apps.sui.views.registry import ScanBookerRegistryView
from scanbooker.django.apps.sui.views.schedule import SessionScheduleWidget
from scanbooker.django.apps.sui.views.manipulator import SessionTimeManipulator
from scanbooker.django.apps.sui.views.manipulator import ScanningSessionUpdateManipulator
from django.utils.datastructures import MultiValueDict
from dm.datetimeconvertor import DateTimeConvertor
from scanbooker.dictionarywords import URI_PREFIX
import mx.DateTime

class DuplicateWidget(ScanBookerRegistryCreateView):

    templatePath = 'rpc2/blank'

    def __init__(self, requestParams, **kwds):
        super(DuplicateWidget, self).__init__(actionName='create', **kwds)
        self.requestParams = requestParams

    def markNavigation(self):
        pass

    def setContext(self, **kwds):
        pass

    def canAccess(self):
        return True


class UpdateFormWidget2(ScanBookerRegistryUpdateView):

    templatePath = 'widgets2/updateForm'

    def __init__(self, domainObject, **kwds):
        registryPath = "%s/%s" % (
            domainObject.getRegistryAttrName(),
            domainObject.getRegisterKeyValue(),
        )
        super(UpdateFormWidget2, self).__init__(
            registryPath=registryPath, actionName='update', **kwds
        )

    def setMajorNavigationItems(self):
        self.majorNavigation = []

#    def canAccess(self):
#        return True

#    def markNavigation(self):
#        pass

    def setContext(self, **kwds):
        self.context.update({
            'uriPrefix': self.dictionary[URI_PREFIX],
            'registryPath': self.registryPath,
            'form': self.getForm(),
        })

    def getJsonData(self):
        self.getResponse()
        data = {}
        data['form'] = self.content
        data['id'] = self.domainObject.getCalendarId()
        return data

    def takeAction(self):
        self.requestParams = self.getZeroRequestParams()
        super(UpdateFormWidget2, self).takeAction()


class UpdateFormWidget(ScanBookerRegistryUpdateView):

    templatePath = 'widgets/updateForm'

    def __init__(self, layerName=None, **kwds):
        super(UpdateFormWidget, self).__init__(**kwds)
        self.layerName = layerName
    
    def getJsonData(self):
        data = {}
        self.getResponse()
        self.logger.debug("Update Form Widget: %s" % self.form)
        data['form'] = self.content
        return data

    def takeAction(self):
        self.requestParams = self.getZeroRequestParams()
        super(UpdateFormWidget, self).takeAction()

    def setContext(self):
        super(UpdateFormWidget, self).setContext()
        self.context.update({
            'typeNick': self.getManipulatedDomainObject().typeNick,
            'layerName': self.layerName or '',
        })
 

class UpdatePostWidget2(ScanBookerRegistryUpdateView):

    templatePath = 'rpc2/blank'

    def markNavigation(self):
        pass

    def setContext(self, **kwds):
        pass

    def getJsonData(self):
        self.getResponse()
        self.logger.debug("Update Post Widget...")
        validationErrors = self.getValidationErrors()
        data = {}
        if validationErrors:
            #errors = []
            #data['errors'] = errors
            #for attrName in validationErrors:
            #    snagList = validationErrors[attrName]
            #    snags = ", ".join(snagList)
            #    errors.append('%s: %s' % (attrName, snags))
            #    #errors.append(attrName)
            errors = validationErrors.items()[0][1]
            data['errors'] = errors
        return data


class UpdatePostWidget(ScanBookerRegistryUpdateView):

    def getJsonData(self):
        self.getResponse()
        self.logger.debug("Update Post Widget...")
        validationErrors = self.getValidationErrors()
        if validationErrors:
            data = validationErrors.items()[0][1]
        else:
            data = ''
        return data
        

class SessionBudgeWidget(SessionScheduleWidget, RegistryUpdateView):

    oneBlock = 15 * mx.DateTime.oneMinute
    dateTimeConvertor = DateTimeConvertor()
    
    def __init__(self, **kwds):
        super(SessionBudgeWidget, self).__init__(actionName='Update', **kwds)

    def getManipulatorClass(self):
        return SessionTimeManipulator

    def getJsonData(self):
        validationErrors = self.getValidationErrors()
        if not validationErrors:
            self.manipulateDomainObject()
        self.scheduledSession = self.getManipulatedDomainObject()
        data = super(SessionBudgeWidget, self).getJsonData()
        if validationErrors:
            data['validationErrors'] = validationErrors.items()[0][1]
        else:
            data['validationErrors'] = ''
        return data
        
    def manipulateDomainObject(self):
        manipulator = self.getManipulator()
        requestParams = self.getRequestParams()
        manipulator.update(data=requestParams)

    def getRequestParams(self):
        if self.requestParams == None:
            self.requestParams = self.getInitialParams()
            self.budgeRequestParams()
            self.logger.debug("Budged params: %s" % self.requestParams)
        return self.requestParams

    def budgeRequestParams(self):
        pass

    def getStarts(self):
        startsHTML = self.requestParams['starts']
        startsDateTime = self.dateTimeConvertor.fromHTML(startsHTML)
        return startsDateTime

    def setStarts(self, startsDateTime):
        startsHTML = self.dateTimeConvertor.toHTML(startsDateTime)
        self.requestParams['starts'] = startsHTML

    def getEnds(self):
        endsHTML = self.requestParams['ends']
        endsDateTime = self.dateTimeConvertor.fromHTML(endsHTML)
        return endsDateTime

    def setEnds(self, endsDateTime):
        endsHTML = self.dateTimeConvertor.toHTML(endsDateTime)
        self.requestParams['ends'] = endsHTML


class SessionEarlierView(SessionBudgeWidget):

    def budgeRequestParams(self):
        starts = self.getStarts()
        starts -= self.oneBlock
        self.setStarts(starts)
        ends = self.getEnds()
        ends -= self.oneBlock
        self.setEnds(ends)


class SessionLaterView(SessionBudgeWidget):

    def budgeRequestParams(self):
        starts = self.getStarts()
        starts += self.oneBlock
        self.setStarts(starts)
        ends = self.getEnds()
        ends += self.oneBlock
        self.setEnds(ends)


class SessionBudgeStartsWidget(SessionBudgeWidget):

    def getManipulatedFieldNames(self):
        return ['starts', 'ends']


class SessionEarlierWidget(SessionBudgeStartsWidget):
        
    def budgeRequestParams(self):
        starts = self.getStarts()
        starts -= self.oneBlock
        self.setStarts(starts)
        ends = self.getEnds()
        ends -= self.oneBlock
        self.setEnds(ends)


class SessionLaterWidget(SessionBudgeStartsWidget):

    def budgeRequestParams(self):
        starts = self.getStarts()
        starts += self.oneBlock
        self.setStarts(starts)
        ends = self.getEnds()
        ends += self.oneBlock
        self.setEnds(ends)


class SessionBudgeEndsWidget(SessionBudgeWidget):

    def getManipulatedFieldNames(self):
        return ['ends']


class SessionShortenWidget(SessionBudgeEndsWidget):
        
    def budgeRequestParams(self):
        ends = self.getEnds()
        ends -= self.oneBlock
        self.setEnds(ends)


class SessionLengthenWidget(SessionBudgeEndsWidget):

    def budgeRequestParams(self):
        ends = self.getEnds()
        ends += self.oneBlock
        self.setEnds(ends)


class SessionToEarmarkWidget(SessionBudgeStartsWidget):
        
    def __init__(self, earmarkId=None, **kwds):
        super(SessionToEarmarkWidget, self).__init__(**kwds)
        self.logger.debug(
            "SessionToEarmarkWidget: Earmark id: %s (%s)" % (
                earmarkId, earmarkId.__class__.__name__
            )
        )
        self.earmark = self.registry.earmarkedTimes[earmarkId]
        self.logger.debug(
            "SessionToEarmarkWidget: Earmark: %s" % self.earmark
        )

    def budgeRequestParams(self):
        oldEnds = self.getEnds()
        self.logger.debug('Moved from ends %s' % oldEnds)
        oldStarts = self.getStarts()
        self.logger.debug('Moved from starts %s' % oldStarts)
        duration = oldEnds - oldStarts 
        self.logger.debug('Moved session duration %s' % duration)
        newStarts = self.earmark.starts
        self.logger.debug('Moved to starts %s' % newStarts)
        newEnds = newStarts + duration
        self.logger.debug('Moved to ends %s' % newEnds)
        self.setStarts(newStarts)
        self.setEnds(newEnds)


class SessionTruncateView(SessionBudgeWidget):

    def __init__(self, timeBlockName=None, **kwds):
        super(SessionTruncateView, self).__init__(**kwds)
        self.timeBlockName = timeBlockName
        if len(self.timeBlockName) != 4:
            raise Exception, "Time block name looks wrong: '%s'" % (
                self.timeBlockName
            )

    def budgeRequestParams(self):
        ends = self.getEnds()
        newHour = int(self.timeBlockName[0:2])
        newMinute = int(self.timeBlockName[2:4])
        ends = mx.DateTime.DateTime(
            ends.year, ends.month, ends.day,
            newHour, newMinute, 0
        )
        self.setEnds(ends)

    def setContext(self):
        self.context


def earlier(request, registryPath):
    view = SessionEarlierView(
        request=request,
        registryPath=registryPath,
    )
    return view.getResponse()

def later(request, registryPath):
    view = SessionLaterView(
        request=request,
        registryPath=registryPath,
    )
    return view.getResponse()

def shorten(request, registryPath):
    view = SessionShortenView(
        request=request,
        registryPath=registryPath,
    )
    return view.getResponse()

def lengthen(request, registryPath):
    view = SessionLengthenView(
        request=request,
        registryPath=registryPath,
    )
    return view.getResponse()

def ends(request, registryPath, timeBlockName):
    view = SessionTruncateView(
        request=request,
        registryPath=registryPath,
        timeBlockName=timeBlockName
    )
    return view.getResponse()


from scanbooker.django.apps.sui.views.registry import ScanBookerRegistryListallView
from scanbooker.django.apps.sui.views.registry import ScanBookerRegistryView
import dm.times

class VolunteerBookingSelectVolunteer(ScanBookerRegistryListallView):

    viewPosition = 'volunteers/booking'
    templatePath = 'volunteers/booking/select_volunteer'

    def __init__(self, **kwds):
        super(VolunteerBookingSelectVolunteer, self).__init__(
            registryPath='volunteers', **kwds)
        self.filtered = None

    def getManipulatedObjectRegister(self):
        if self.filtered == None:
            r = super(VolunteerBookingSelectVolunteer, self
                ).getManipulatedObjectRegister()
            self.filtered = r.clone()
            self.filtered.filter = {
                'status': self.registry.volunteerStatuses['Active']
            }
        return self.filtered

    def setContext(self, **kwds):
        super(VolunteerBookingSelectVolunteer, self).setContext()
        self.context.update({
            'upcomingSessionCount': self.countUpcomingSessions(),
            'showRegisterIndex': False,
        })

    def countUpcomingSessions(self):
        filtered = self.registry.scanningSessions.clone()
        filtered.filter = {
            'volunteer': None,
            'bookingOwnVolunteers': False,
            '__startsAfter__': dm.times.getLocalNow(),
        }
        return len(filtered)


class VolunteerCancellationSelectVolunteer(VolunteerBookingSelectVolunteer):
    
    viewPosition = 'volunteers/cancellation'
    templatePath = 'volunteers/cancellation/select_volunteer'


class VolunteerHitlistView(VolunteerBookingSelectVolunteer):
   
    viewPosition = 'volunteers/hitlist'
    templatePath = 'volunteers/hitlist/listall'

    def getManipulatedObjectRegister(self):
        if self.filtered == None:
            r = super(VolunteerBookingSelectVolunteer, self
                ).getManipulatedObjectRegister()
            self.filtered = r.clone()
            self.filtered.filter = {
                'status': self.registry.volunteerStatuses['Active'],
                'onHitlist': True,
            }
        return self.filtered


class VolunteerBookingSelectSession(ScanBookerRegistryListallView):

    viewPosition = 'volunteers/booking'
    templatePath = 'volunteers/booking/select_session'

    def __init__(self, volunteerId, **kwds):
        super(VolunteerBookingSelectSession, self).__init__(
            registryPath='scanningSessions', **kwds)
        self.selectedVolunteer = self.registry.volunteers[volunteerId]
        self.filtered = None

    def getManipulatedObjectRegister(self):
        if self.filtered == None:
            r = super(VolunteerBookingSelectSession, self
                ).getManipulatedObjectRegister()
            self.filtered = r.clone()
            self.filtered.filter = {
                'volunteer': self.filterByVolunteer(),
                'bookingOwnVolunteers': False,
                '__startsAfter__': dm.times.getLocalNow(),
            }
        return self.filtered

    def filterByVolunteer(self):
        return None

    def setContext(self, **kwds):
        super(VolunteerBookingSelectSession, self).setContext()
        self.context.update({
            'selectedVolunteer': self.selectedVolunteer,
            'showRegisterIndex': False,
        })


class VolunteerCancellationSelectSession(VolunteerBookingSelectSession):

    viewPosition = 'volunteers/cancellation'
    templatePath = 'volunteers/cancellation/select_session'

    def filterByVolunteer(self):
        return self.selectedVolunteer


class VolunteerCancellation(ScanBookerRegistryListallView):

    viewPosition = 'volunteers/cancellation'
    templatePath = 'volunteers/cancellation/select_session'

    def __init__(self, **kwds):
        super(VolunteerCancellation, self).__init__(
            registryPath='scanningSessions', **kwds)
        self.selectedVolunteer = self.registry.volunteers[1]  # Todo: This.
        self.filtered = None

    def getManipulatedObjectRegister(self):
        if self.filtered == None:
            r = super(VolunteerCancellation, self
                ).getManipulatedObjectRegister()
            self.filtered = r.clone()
            self.filtered.filter = {
                'volunteer': self.selectedVolunteer,
                'bookingOwnVolunteers': False,
                '__startsAfter__': dm.times.getLocalNow(),
            }
        return self.filtered

    def setContext(self, **kwds):
        super(VolunteerCancellation, self).setContext()
        self.context.update({
            'selectedVolunteer': self.selectedVolunteer,
            'showRegisterIndex': False,
        })


class VolunteerBookingConfirmSelection(ScanBookerRegistryView):

    viewPosition = 'volunteers/booking'
    templatePath = 'volunteers/booking/confirm_selection'

    def __init__(self, volunteerId, sessionId, isConfirmed, **kwds):
        super(VolunteerBookingConfirmSelection, self).__init__(
            registryPath='scanningSessions', **kwds)
        self.selectedVolunteer = self.registry.volunteers[volunteerId]
        self.selectedSession = self.registry.scanningSessions[sessionId]
        self.isConfirmed = isConfirmed
        self.filtered = None
        self.isAlreadyBooked = False
        if self.selectedSession.volunteer:
            self.isAlreadyBooked = True
            if self.isConfirmed == 'cancel':
                self.cancelVolunteerScanningAppointment()
        elif self.isConfirmed == 'confirm':
            self.createVolunteerScanningAppointment()

    def canAccess(self):
        return self.canCreateVolunteerScanningAppointment()

    def createVolunteerScanningAppointment(self):
        if self.canAccess():
            self.selectedSession.volunteer = self.selectedVolunteer
            self.selectedSession.save()

    def cancelVolunteerScanningAppointment(self):
        if self.canAccess():
            self.selectedSession.volunteer = None
            self.selectedSession.save()

    def setContext(self, **kwds):
        super(VolunteerBookingConfirmSelection, self).setContext()
        self.context.update({
            'selectedVolunteer': self.selectedVolunteer,
            'selectedSession': self.selectedSession,
            'isConfirmed': self.isConfirmed,
            'isAlreadyBooked': self.isAlreadyBooked,
        })


class VolunteerCancellationConfirmSelection(VolunteerBookingConfirmSelection):

    viewPosition = 'volunteers/cancellation'
    templatePath = 'volunteers/cancellation/confirm_selection'


class VolunteerHitActionView(VolunteerHitlistView):
   
    viewPosition = 'volunteers/hitlist'
    templatePath = 'volunteers/hitlist/action'

    def __init__(self, volunteerId, actionName, **kwds):
        super(VolunteerHitActionView, self).__init__(**kwds)
        self.selectedVolunteer = self.registry.volunteers[volunteerId]
        self.hitlistActionName = actionName
        self.hitlistActionSuccess = False
        if self.hitlistActionName == 'add':
            if self.selectedVolunteer.onHitlist == False:
                self.selectedVolunteer.onHitlist = True
                self.selectedVolunteer.save()
                self.hitlistActionSuccess = True
        elif self.hitlistActionName == 'remove':
            if self.selectedVolunteer.onHitlist == True:
                self.selectedVolunteer.onHitlist = False
                self.selectedVolunteer.save()
                self.hitlistActionSuccess = True

    # Todo: Error handling.
    def setContext(self, **kwds):
        super(VolunteerHitActionView, self).setContext()
        self.context.update({
            'selectedVolunteer': self.selectedVolunteer,
            'hitlistActionName': self.hitlistActionName,
            'hitlistActionSuccess': self.hitlistActionSuccess,
        })


def booking(request, volunteerId=None, sessionId=None, isConfirmed=''):
    if volunteerId == None:
        view = VolunteerBookingSelectVolunteer(request=request)
    elif sessionId == None:
        view = VolunteerBookingSelectSession(
           request=request,
           volunteerId=volunteerId
        )
    else:
        view = VolunteerBookingConfirmSelection(
           request=request,
           volunteerId=volunteerId,
           sessionId=sessionId,
           isConfirmed=isConfirmed,
        )
    return view.getResponse()

def cancellation(request, volunteerId=None, sessionId=None, isConfirmed=''):
    if volunteerId == None:
        view = VolunteerCancellationSelectVolunteer(request=request)
    elif sessionId == None:
        view = VolunteerCancellationSelectSession(
           request=request,
           volunteerId=volunteerId
        )
    else:
        view = VolunteerCancellationConfirmSelection(
           request=request,
           volunteerId=volunteerId,
           sessionId=sessionId,
           isConfirmed=isConfirmed,
        )
    return view.getResponse()

def hitlist(request, volunteerId=None, actionName=None):
    if not volunteerId:
        view = VolunteerHitlistView(request=request)
    else:
        view = VolunteerHitActionView(request=request,
        volunteerId=volunteerId, actionName=actionName)
    return view.getResponse()



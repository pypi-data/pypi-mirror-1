from dm.dom.stateful import *
from scanbooker.dom.base import PersonExtn
import mx.DateTime
import dm.times

class Volunteer(PersonExtn):

    homeAddress = Text(isRequired=False)
    homeTelephone = String(isRequired=False)
    workTelephone = String(isRequired=False)
    mobileTelephone = String(isRequired=False)
    email = String(isRequired=False)
    dateOfBirth = DateOfBirth(isRequired=False)
    panelId = String(isRequired=False)  # CBSU specific attribute
    notes = Text(isRequired=False)
    status = HasA('VolunteerStatus', isSimpleOption=True, isRequired=False, default='Active')
    handedness = HasA('Handedness', isSimpleOption=True, isRequired=False)
    recruitment = HasA('VolunteerRecruitmentMethod', isSimpleOption=True,
        isRequired=False)
    doctorName = String(isRequired=False)
    doctorAddress = Text(isRequired=False)
    doctorTelephone = String(isRequired=False)
    screenings = AggregatesMany('VolunteerScreening', 'scanningSession',
        isRequired=False)
    structuralScans = AggregatesMany('StructuralScan', 'id', isRequired=False)
    functionalScans = AggregatesMany('FunctionalScan', 'id', isRequired=False)
    scanningSessions = AggregatesMany('ScanningSession', 'id', isRequired=False)
    language = String(isRequired=False, default='English')
    onHitlist = Boolean(default=False)

    searchAttributeNames = ['realname', 'panelId', 'notes']

    def lastScan(self):
        return self.scanningSessions.findLastDomainObject(
            __startsBefore__=dm.times.getLocalNow()
        )

    def age(self):
        now = mx.DateTime.now()
        dob = self.dateOfBirth
        age = now.year - dob.year
        if (now.month < dob.month):
            age -= 1
        elif (now.month == dob.month) and (now.day < dob.day):
            age -= 1
        return age

    def hand(self):
        if self.handedness:
            return self.handedness.name[0].upper()
        else:
            return ''

    def isInactive(self):
        return not self.status or self.status.name != 'Active'


class VolunteerStatus(StandardObject):
    
    isContant = True


class VolunteerType(StandardObject):
    
    isContant = True


class VolunteerScanningAppointment(StatefulObject):

    volunteer       = HasA('Volunteer')
    scanningSession = HasA('ScanningSession')


class VolunteerScreening(StatefulObject):

    results         = String(isRequired=False)
    volunteer       = HasA('Volunteer')
    scanningSession = HasA('ScanningSession')


class StructuralScan(StatefulObject):

    volunteer = HasA('Volunteer')


class FunctionalScan(StatefulObject):

    volunteer = HasA('Volunteer')


class VolunteerRecruitmentMethod(StandardObject):
 
    isContant = True


class Handedness(StandardObject):

    isContant = True


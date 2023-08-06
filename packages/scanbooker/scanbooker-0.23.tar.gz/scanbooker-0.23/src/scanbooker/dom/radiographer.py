from dm.dom.stateful import *
from scanbooker.dom.base import PersonExtn

class Radiographer(PersonExtn):

    pass


class RadiographerTheoryAppointment(StatefulObject):

    radiographer  = HasA('Radiographer')
    theorySession = HasA('TheorySession')


class RadiographerPracticalAppointment(StatefulObject):

    radiographer     = HasA('Radiographer')
    practicalSession = HasA('PracticalSession')


class RadiographerScanningAppointment(StatefulObject):

    radiographer    = HasA('Radiographer')
    scanningSession = HasA('ScanningSession')




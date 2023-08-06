from dm.dom.stateful import *

class FundingStatus(DatedStatefulObject):

    isConstant = True
    
    title = String()
    
    def getLabelValue(self):
        return self.title


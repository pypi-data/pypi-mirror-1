from dm.dom.stateful import *

class Setting(StandardObject):

    earmarkTemplate = HasA('EarmarkedTimeTemplateWeek', isRequired=False)
    showInlineHelp = Boolean(default=True)
    defaultOrganisation = HasA('Organisation', isRequired=False)
    requireTrainedProjectLeader = Boolean(default=True)
    requireApprovedProjectLeader = Boolean(default=True)
    requireEthicsApprovalInDate = Boolean(default=True)
    requireEthicsApprovalBalance = Boolean(default=True)
    

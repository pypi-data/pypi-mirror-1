"""
AccessControl plugin, listens to domain model events and adjusts access.

"""

import dm.plugin.base
import os
from dm.strategy import FindInstanceProtectionObject
from dm.strategy import CreateProtectionObject

class Plugin(dm.plugin.base.PluginBase):
    "AccessControl plugin."

    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        name = 'accesscontrol'

    def onScanningSessionCreate(self, scanningSession):
        createObject = CreateProtectionObject(scanningSession)
        protectionObject = createObject.create()
        if scanningSession.createdBy == None:
            return
        # todo: do this with inferred roles instead
        else:
            grants = scanningSession.createdBy.grants
        grantedActionNames = ['Update', 'Delete']
        for actionName in grantedActionNames:
            action = self.registry.actions[actionName]
            permission = protectionObject.permissions[action]
            if not permission in grants:
                grants.create(permission)

    def onScanningSessionPurge(self, scanningSession):
        self.deleteProtectionObject(scanningSession)

    def deleteProtectionObject(self, domainObject):
        findObject = FindInstanceProtectionObject(domainObject)
        protectionObject = findObject.find()
        if protectionObject:
            protectionObject.delete()


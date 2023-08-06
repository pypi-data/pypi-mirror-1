import dm.plugin.base
import os

class Plugin(dm.plugin.base.PluginBase):

    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        name = 'metamodel'



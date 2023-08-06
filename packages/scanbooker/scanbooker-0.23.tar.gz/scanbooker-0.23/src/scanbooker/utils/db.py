import os
import commands

import dm.util.db
import scanbooker.ioc

class Database(dm.util.db.Database):

    features = scanbooker.ioc.features
        
    def _getSystemDictionary(self):
        import scanbooker.dictionary 
        systemDictionary = scanbooker.dictionary.SystemDictionary()
        return systemDictionary
            
    def init(self):
        """
        Initialise service database by creating initial domain object records.
        """
        import scanbooker.soleInstance
        commandSet = scanbooker.soleInstance.application.commands
        commandClass = commandSet['InitialiseDomainModel']
        initDomainModel = commandClass()
        initDomainModel.execute()


import os
import commands

import dm.util.db
import dm.ioc

class Database(dm.util.db.Database):

    features = dm.ioc.features
        
    def _getSystemDictionary(self):
        import desire.dictionary 
        systemDictionary = desire.dictionary.SystemDictionary()
        return systemDictionary
            
    def init(self):
        """
        Initialise service database by creating initial domain object records.
        """
        import desire.soleInstance
        commandSet = desire.soleInstance.application.commands
        commandClass = commandSet['InitialiseDomainModel']
        initDomainModel = commandClass()
        initDomainModel.execute()


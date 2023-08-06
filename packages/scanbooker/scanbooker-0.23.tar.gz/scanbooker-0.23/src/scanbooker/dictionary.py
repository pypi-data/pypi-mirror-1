"""
Configurable dictionary of attributes of the system.

"""

import os
import sys
import dm.dictionary
from scanbooker.dictionarywords import *
import scanbooker

class SystemDictionary(dm.dictionary.SystemDictionary):
    
    def getSystemName(self):
        return 'scanbooker'

    def getSystemVersion(self):
        return scanbooker.__version__

    def setDefaultWords(self):
        super(SystemDictionary, self).setDefaultWords()
        self[PLUGIN_PACKAGE_NAME] = 'scanbooker.plugin'
        self[INIT_STOP_VISITOR_REGISTRATION] = ''
        self[AC_SKIP_ROLE_INFERENCE] = ''
        self[INITIAL_PERSON_ROLE] = 'Staff'
        self[DOJO_PATH] = ''
        self[DOJO_PREFIX] = '/dojo'


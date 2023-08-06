"""
Configurable dictionary of attributes of the system.

"""

import os
import sys
import dm.dictionary
from desire.dictionarywords import *
import desire

class SystemDictionary(dm.dictionary.SystemDictionary):
    
    def getSystemName(self):
        return 'desire'

    def getSystemVersion(self):
        return desire.__version__

    def setDefaultWords(self):
        super(SystemDictionary, self).setDefaultWords()
        self[PLUGIN_PACKAGE_NAME] = 'desire.plugin'
        self[INIT_STOP_VISITOR_REGISTRATION] = ''
        self[AC_SKIP_ROLE_INFERENCE] = ''
        self[INITIAL_PERSON_ROLE] = 'Developer'
        self[PROVISIONS_DIR_PATH] = '/tmp/%s-provisions' % self[SYSTEM_NAME]
        self[TRAC_PATH] = '/usr/share/trac'
        self[DOJO_PATH] = '/usr/share/dojo'
        self[DOJO_PREFIX] = '/dojo'
        self[DISTINGUISH_MODE] = 'auto'


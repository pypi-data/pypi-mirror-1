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


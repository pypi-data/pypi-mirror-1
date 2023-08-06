from desire.plugin.base import PluginBase

class Plugin(PluginBase):

    def __init__(self, *args, **kwds):
        super(Plugin, self).__init__(*args, **kwds)
        self.resetCounts()

    def checkPluginDependencies(self):
        try:
            import sqlite
        except:
            msg = "Python package 'sqlite' can't be imported."
            raise Exception, msg

    def resetCounts(self):
        self.counts = {}

    def getCount(self, countName):
        if not countName in self.counts:
            return 0
        else:
            return self.counts[countName]

    def incCount(self, countName):
        if not countName in self.counts:
            self.counts[countName] = 1
        else:
            self.counts[countName] += 1

    def createProcess(self, process):
        self.incCount('onProcessCreate')
        return True

    def createApplication(self):
        return True


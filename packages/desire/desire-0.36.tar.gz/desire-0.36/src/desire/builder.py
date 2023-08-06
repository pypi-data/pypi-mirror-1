import dm.builder
from dm.ioc import *

class ApplicationBuilder(dm.builder.ApplicationBuilder):
    """
    Extends core builder by adding new application features, and by overriding
    core features with replacements for, or extensions of, core features.
    """

    #
    # Add features.
    
    def construct(self):
        super(ApplicationBuilder, self).construct()

    def findSystemDictionary(self):
        import desire.dictionary
        return desire.dictionary.SystemDictionary()

    def findModelBuilder(self):
        import desire.dom.builder
        return desire.dom.builder.ModelBuilder()

    def findCommandSet(self):
        import desire.command
        return desire.command.__dict__

    def findFileSystem(self):
        import desire.filesystem
        return desire.filesystem.FileSystemPathBuilder()

    def findAccessController(self):
        import desire.accesscontrol
        return desire.accesscontrol.AccessController()


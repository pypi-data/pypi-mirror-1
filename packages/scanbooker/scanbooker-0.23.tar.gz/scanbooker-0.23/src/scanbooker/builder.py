import dm.builder
from scanbooker.ioc import *

class ApplicationBuilder(dm.builder.ApplicationBuilder):
    """
    Extends core builder by adding new application features, and by overriding
    core features with replacements for, or extensions of, core features.
    """

    #
    # Add features.
    
    def construct(self):
        super(ApplicationBuilder, self).construct()
        features.register('UrlBuilderProject', self.findUrlBuilderProject())

    def findUrlBuilderProject(self):
        import scanbooker.url
        return scanbooker.url.UrlBuilderProject()
 
    #
    # Replace features.

    def findSystemDictionary(self):
        import scanbooker.dictionary
        return scanbooker.dictionary.SystemDictionary()

    def findModelBuilder(self):
        import scanbooker.dom.builder
        return scanbooker.dom.builder.ModelBuilder()

    def findCommandSet(self):
        import scanbooker.command
        return scanbooker.command.__dict__

    def findFileSystem(self):
        import scanbooker.filesystem
        return scanbooker.filesystem.FileSystemPathBuilder()

    def findAccessController(self):
        import scanbooker.accesscontrol
        return scanbooker.accesscontrol.AccessController()


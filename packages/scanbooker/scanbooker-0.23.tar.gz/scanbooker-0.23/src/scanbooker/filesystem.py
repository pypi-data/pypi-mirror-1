import os.path
import dm.filesystem

class FileSystemPathBuilder(dm.filesystem.FileSystemPathBuilder):

    def __init__(self):
        super(FileSystemPathBuilder, self).__init__()
    
    def getProjectPath(self, project):
        """
        Get base directory path for a project
        """
        return os.path.join(
            self.dictionary['project_data_dir'],
            project.name
        )
    
    def getProjectPluginPath(self, project, plugin):
        """
        Return path beneath project path for given plugin
        """
        if not project:
            raise Exception, "No project passed."
        if not plugin:
            raise Exception, "No plugin passed."
        return os.path.join(
            self.getProjectPath(project),
            plugin.name
        )
    
    def getServicePath(self, service): 
        """
        Map a service (project, plugin, name, id) tuple to a disk path.
        """
        basePath = self.getProjectPluginPath(service.project, service.plugin)
        result = os.path.join(
            basePath, 
            str(service.id)
        )
        return os.path.normpath(result)


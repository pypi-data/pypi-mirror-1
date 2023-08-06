import os
import dm.cli.admin
from scanbooker.dictionarywords import *

class AdministrationUtility(dm.cli.admin.AdministrationUtility):

    servicePathEnvironVariableName = 'SCANBOOKERHOME'

    def buildApplication(self):
        import scanbooker.soleInstance
        self.appInstance = scanbooker.soleInstance.application
        self.registry = self.appInstance.registry

    def backupSystemService(self):
        import scanbooker.soleInstance
        commandSet = scanbooker.soleInstance.application.commands
        backupCommandName = 'Backup'
        backupCommand = commandSet[backupCommandName](self.args[0])
        backupCommand.execute()

    def getDatabaseUtilityClass(self):
        from scanbooker.utils.db import Database
        return Database

    def upgradeSystemServiceDatabase(self):
        import scanbooker.utils.upgrade
        dbCommand = scanbooker.utils.upgrade.UpgradeDbTo0Point11()
        dbCommand.execute()

    def upgradeSystemServiceFilesystem(self):
        import scanbooker.utils.upgrade
        filesystemCommand = scanbooker.utils.upgrade.UpgradeDataTo0Point11(
            self.servicePath, self.systemPath
        )
        filesystemCommand.execute()

    def noSlash(self, path):
        if path and path[-1] == '/':
            path.pop()
        return path

    def buildApacheConfig(self):
        import scanbooker.soleInstance
        dictionary = scanbooker.soleInstance.application.dictionary
        configPath = dictionary[APACHE_CONFIG_PATH]
        configVars = {}
        configVars['SYSTEM_CONFIG_PATH'] = dictionary[SYSTEM_CONFIG_PATH]
        configVars['PYTHON_PATH'] = self.noSlash(dictionary[PYTHONPATH])
        if scanbooker.soleInstance.application.debug:
            configVars['PYTHON_DEBUG'] = 'On'
        else:
            configVars['PYTHON_DEBUG'] = 'Off'
        configVars['DOJO_PREFIX'] = self.noSlash(dictionary[DOJO_PREFIX])
        configVars['DOJO_PATH'] = self.noSlash(dictionary[DOJO_PATH])
        configVars['URI_PREFIX'] = self.noSlash(dictionary[URI_PREFIX])
        configVars['MEDIA_PREFIX'] = self.noSlash(dictionary[MEDIA_PREFIX])
        configVars['MEDIA_PATH'] = self.noSlash(dictionary[MEDIA_PATH])
        if dictionary[dictionary.words.VIRTUALENVBIN_PATH]:
            configVars['HANDLER_PATH'] = 'scanbookervirtualenvhandlers::djangohandler'
        else:
            configVars['HANDLER_PATH'] = 'scanbooker.handlers.modpython'
        configContent = """# ScanBooker auto-generated configuration.
        """
        configContent += """
# Application location.
<Location "%(URI_PREFIX)s/">
  SetEnv SCANBOOKER_SETTINGS %(SYSTEM_CONFIG_PATH)s
  SetEnv PYTHONPATH %(PYTHON_PATH)s
  SetEnv DJANGO_SETTINGS_MODULE scanbooker.django.settings.main
  SetHandler python-program
  PythonPath "'%(PYTHON_PATH)s'.split(':') + sys.path"
  PythonHandler %(HANDLER_PATH)s
  PythonDebug %(PYTHON_DEBUG)s
</Location>
        """ % configVars
        
        if configVars['MEDIA_PREFIX']:
            configContent += """            
# Media location.
Alias %(MEDIA_PREFIX)s/ %(MEDIA_PATH)s/
<Location "%(MEDIA_PREFIX)s/">
  SetHandler None
  Order Deny,Allow
  Allow from all
</Location>
            """ % configVars

#        configContent += """
# Dojo location.
#Alias %(DOJO_PREFIX)s/ %(DOJO_PATH)s/
#<Location "%(DOJO_PREFIX)s/">
#  SetHandler None
#</Location>
#        """ % configVars

        configFile = open(configPath, 'w')
        configFile.write(configContent)
        configFile.close()

    def reloadApacheConfig(self):
        import scanbooker.soleInstance

    def getSystemName(self):
        return "ScanBooker"
        
    def getSystemVersion(self):
        import scanbooker
        return scanbooker.__version__

    def touchMigratedDomainModel(self, line=None):
        # Update system version.
        system = self.registry.systems[1]
        system.version = self.appInstance.dictionary[SYSTEM_VERSION]
        system.save()
        
    def createAboutMessage(self):
        systemName = self.getSystemName()
        systemVersion = self.getSystemVersion()
        aboutMessage = \
'''This is %s version %s.

Copyright the Appropriate Software Foundation. ScanBooker is open-source
software licensed under the GPL v2.0. See COPYING for details.
''' % (systemName, systemVersion)
        return aboutMessage

    def constructSystemDictionary(self):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'scanbooker.django.settings.main'
        from scanbooker.dictionary import SystemDictionary
        return SystemDictionary()


class UtilityRunner(dm.cli.admin.UtilityRunner):

    systemName = 'scanbooker'
    servicePathEnvironVariableName = 'SCANBOOKERHOME'
    utilityClass = AdministrationUtility
    usage  = """Usage: %prog [options] [command]

Administer a ScanBooker service, including its domain objects. 

Can be run in two modes:
   1. single command: run the command provided and exit (Default)
   2. interactive (use the "--interactive" option)

To obtain information about the commands available run the "help" command.

Domain objects (e.g. persons, projects, etc) are administered by starting
a python shell from within interactive mode. Run "help shell" for more details.

"""


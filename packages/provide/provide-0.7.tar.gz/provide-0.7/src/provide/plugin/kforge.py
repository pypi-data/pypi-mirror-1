from provide.plugin.base import DomainModelApplicationPlugin
import os
from provide.dictionarywords import TRAC_PATH

# todo: parameterise the trac location in KForge, configure from linked trac

class Plugin(DomainModelApplicationPlugin):

    def generateNewConfigFile(self, service):
        configPath = self.makeConfigPath(service)
        configDir = os.path.dirname(configPath)
        os.makedirs(configDir)
        scriptPath = self.makeScriptRunnerPath(service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.chdir(scriptDirPath)
        commandString = self.getMakeConfigScriptCmdLine(service, configPath)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise "Couldn't run command through runner script: %s" % commandString

    def getMakeConfigScriptCmdLine(self, service, configPath):
        cmd = os.path.join(
            self.makeBinPath(service),
            'kforge-makeconfig'
        )
        return "%s %s" % (cmd, configPath)

    def getUpdateLinesDefault(self, service):
        lines = super(Plugin, self).getUpdateLinesDefault(service)
        lines.append('project_data_dir = ' + self.makeProjectDataPath(service))
        return lines

    def makeProjectDataPath(self, service):
        installPath = self.makeInstallPath(service)
        return os.path.join(installPath, 'var', 'project_data')

    def generateFilesystemData(self, service):
        scriptPath = self.makeScriptRunnerPath(service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.chdir(scriptDirPath)
        commandString = self.getFilesystemCreateCmdLine(service)
        self.runScriptRunnerScript(scriptPath, commandString)

    def getFilesystemCreateCmdLine(self, service):
        return "%s data create" % self.makeAdminScriptPath(service)

    def substituteConfigPaths(self, service):
        super(Plugin, self).substituteConfigPaths(service)
        self.substituteTemplateDir(service)
        self.substituteDocumentRoot(service)
        self.substituteMediaRoot(service)
        self.substituteApacheConfigFile(service)
        if self.dictionary[TRAC_PATH]:
            self.substituteTracTemplatesPath(service)
            self.substituteTracHtdocsPath(service)
            self.substituteTracAdminScript(service)

    def substituteTemplateDir(self, service):
        placeHolder = self.makePlaceHolderTemplateDir(service)
        realValue = self.makeRealValueTemplateDir(service)
        self.substituteConfig(service, placeHolder, realValue)

    def makePlaceHolderTemplateDir(self, service):
        return 'templates_dir\s+\=\s+\S+'

    def makeRealValueTemplateDir(self, service):
        return 'templates_dir = %s' % (
            os.path.join(
                self.makeInstallPath(service),
                'templates/kui'
            )
        )

    def substituteDocumentRoot(self, service):
        placeHolder = self.makePlaceHolderDocumentRoot(service)
        realValue = self.makeRealValueDocumentRoot(service)
        self.substituteConfig(service, placeHolder, realValue)

    def makePlaceHolderDocumentRoot(self, service):
        return 'document_root\s+\=\s+\S+'
    
    def makeRealValueDocumentRoot(self, service):
        return 'document_root = %s' % (
            os.path.join(
                self.makeInstallPath(service),
                'www'
            )
        )
        
    def substituteMediaRoot(self, service):
        placeHolder = self.makePlaceHolderMediaRoot(service)
        realValue = self.makeRealValueMediaRoot(service)
        self.substituteConfig(service, placeHolder, realValue)

    def makePlaceHolderMediaRoot(self, service):
        return 'media_root\s+\=\s+\S+'
    
    def makeRealValueMediaRoot(self, service):
        return 'media_root = %s' % (
            os.path.join(
                self.makeInstallPath(service),
                'media'
            )
        )
        
    def substituteApacheConfigFile(self, service):
        placeHolder = self.makePlaceHolderApacheConfigFile(service)
        realValue = self.makeRealValueApacheConfigFile(service)
        self.substituteConfig(service, placeHolder, realValue)

    def makePlaceHolderApacheConfigFile(self, service):
        return 'apache_config_file\s+=\s+\S+'
    
    def makeRealValueApacheConfigFile(self, service):
        return 'apache_config_file = %s' % (
            os.path.join(
                self.makeInstallPath(service),
                self.relApacheConfigPath()
            )
        )
        
    def relApacheConfigPath(self):
        return os.path.join('etc', 'httpd.conf')

    def substituteTracTemplatesPath(self, service):
        placeHolder = self.makePlaceHolderTracTemplatesPath(service)
        realValue = self.makeRealValueTracTemplatesPath(service)
        self.substituteConfig(service, placeHolder, realValue)

    def makePlaceHolderTracTemplatesPath(self, service):
        return 'templates_path\s+=\s+\/usr\/share\/trac\/templates'
    
    def makeRealValueTracTemplatesPath(self, service):
        tracTemplatesPath = self.getTracTemplatesPath(service)
        return 'templates_path = %s' % tracTemplatesPath

    def getTracTemplatesPath(self, service):
        relPath = os.path.join('share', 'trac', 'templates')
        basePath = self.makeTracServiceInstallPath(service)
        return os.path.join(basePath, relPath)

    def substituteTracAdminScript(self, service):
        placeHolder = self.makePlaceHolderTracAdminScript(service)
        realValue = self.makeRealValueTracAdminScript(service)
        self.substituteConfig(service, placeHolder, realValue)

    def makePlaceHolderTracAdminScript(self, service):
        return '^admin_script\s+=\s+trac-admin'
    
    def makeRealValueTracAdminScript(self, service):
        tracAdminScript = self.getTracAdminScript(service)
        return 'admin_script = %s' % tracAdminScript

    def getTracAdminScript(self, service):
        relPath = os.path.join('bin', 'trac-admin')
        basePath = self.makeTracServiceInstallPath(service)
        return os.path.join(basePath, relPath)

    def makeTracServiceInstallPath(self, service):
        tracService = self.getTracService(service)
        if tracService:
            basePath = self.makeInstallPath(tracService)
        else:
            basePath = self.dictionary[TRAC_PATH]
        return basePath

    def getTracService(self, service):
        return self.getLinkedService(service, 'trac')

    def getLinkedService(self, service, provisionName):
        if not provisionName in self.registry.provisions:
            return None
        provision = self.registry.provisions[provisionName]
        for link in service.application.links:
            if link.service.application.provision == provision:
                return link.service
        return None

    def substituteTracHtdocsPath(self, service):
        placeHolder = self.makePlaceHolderTracHtdocsPath(service)
        realValue = self.makeRealValueTracHtdocsPath(service)
        self.substituteConfig(service, placeHolder, realValue)

    def makePlaceHolderTracHtdocsPath(self, service):
        return 'htdocs_path\s+=\s+\/usr\/share\/trac\/htdocs'
    
    def makeRealValueTracHtdocsPath(self, service):
        tracHtdocsPath = self.getTracHtdocsPath(service)
        return 'htdocs_path = %s' % tracHtdocsPath
        
    def getTracHtdocsPath(self, service):
        relPath = os.path.join('share', 'trac', 'htdocs')
        basePath = self.makeTracServiceInstallPath(service)
        return os.path.join(basePath, relPath)

    def createPythonPackageLinks(self, service):
        tracService = self.getTracService(service)
        if tracService:
            tracPackageLink = os.path.join(
                self.makeLibPythonPath(service), 'trac'
            )
            if os.path.exists(tracPackageLink):
                msg = "Link file already exists: %s" % tracPackageLink
                raise Exception(msg)
            tracPackagePath = os.path.join(
                self.makeLibPythonPath(tracService), 'trac'
            )
            cmd = 'ln -s %s %s' % (tracPackagePath, tracPackageLink)
            print cmd
            if os.system(cmd):
                msg = "Couldn't create symbolic link to trac package."
                raise Exception(msg)
 
    def getUnitTestCmdLine(self, service):
        cmd = super(Plugin, self).getUnitTestCmdLine(service)
        cmd += " kforge.test.core"
        return cmd

    def createServiceDirs(self, service):
        super(Plugin, self).createServiceDirs(service)
        # todo: This only if supporting apache running as another user.
        installPath = self.makeInstallPath(service)
        cmd = "chmod -R g+rX %s" % installPath
        print cmd
        if os.system(cmd):
            msg = "Couldn't chmod to support group: %s" % installPath
            raise Exception(msg)


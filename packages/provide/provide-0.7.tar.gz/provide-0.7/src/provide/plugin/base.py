from dm.exceptions import DataMigrationError
from dm.ioc import RequiredFeature
from dm.plugin.base import PluginBase
from provide.dom.builder import Provision
from provide.dictionarywords import DOMAIN_NAME, SYSTEM_NAME
from provide.dictionarywords import DB_NAME, DB_USER, DB_PASS
from provide.dictionarywords import PROVISIONS_DIR_PATH
from dm.migrate import DomainModelMigrator
import os
from time import sleep
import simplejson
import re
import commands
import random
import string

# todo: Automatically distinguish purpose locations either with domain name, uri prefix, or both.
# todo: Know whether we are running in dual-mode or not, so we need to chmod for group, or not.
# todo: Use commands.getstatusoutput() instead of os.system(), a la:
#    status, output = commands.getstatusoutput(cmd)
#    if status:
#        msg = 'Creation of trac project environment failed'
#        msg += '(cmd was: %s) (output was: %s)' % (cmd, output)

from provide.configwriter import ConfigWriter

class PluginBase(PluginBase):

    # Todo: Plumb this in to -v argument.
    isVerbose = True

    # Todo: Move this method into the model's service object.
    def getServicePurpose(self, service):
        purposeRegister = service.application.provision.purposes
        if not purposeRegister:
            msg = "Purpose register is completely empty! Service: %s, Application: %s, Provision: %s, Register: %s" % (
                service, service.application, service.application.provision, purposeRegister
            )
            raise Exception(msg)
        serviceName = service.name
        if serviceName in purposeRegister:
            purpose = purposeRegister[serviceName]
        else:
            purpose = None
        return purpose

    # Todo: Move this method into the model's service object.
    def getLinkedService(self, service, provisionName):
        if not provisionName in self.registry.provisions:
            return None
        provision = self.registry.provisions[provisionName]
        for link in service.application.links:
            if link.service.application.provision == provision:
                return link.service
        return None

    # Todo: Extract method as class. This code is repeated in several places.
    def system(self, cmd, msg='run given command'):
        msg = "Unable to %s" % msg
        if self.isVerbose:
            print cmd
            if os.system(cmd):
                self.exit(msg + ".")
        else:
            (s, o) = commands.getstatusoutput(cmd)
            if s:
                if o:
                    msg = "%s: %s" % (msg, o)
                else:
                    msg = "%s." % (msg)
                self.exit(msg)

    def exit(self, msg, code=3):
        raise Exception, '\nError: %s' % msg

    def chdir(self, dirPath):
        try:
            os.chdir(dirPath)
        except OSError, inst:
            raise Exception("Couln't change directory to: %s" % inst)

    def chdirProvisions(self):
        dirPath = self.dictionary[PROVISIONS_DIR_PATH]
        self.chdir(dirPath)

    def fetchFileToDir(self, sourcePath, destPath, altBasename="download.tar.gz"):
        print "Fetching file to dir: %s %s" % (sourcePath, destPath)
        self.sourcePath = sourcePath
        self.destDirPath = destPath
        self.destFilePath = os.path.join(
            destPath, os.path.basename(self.sourcePath) or altBasename
        )
        self.fetch()

    def fetchFileToFile(self, sourcePath, destPath):
        self.sourcePath = sourcePath
        self.destDirPath = os.path.dirname(destPath)
        self.destFilePath = destPath
        self.fetch()

    def fetch(self):
        self.validateSourcePath()
        self.validateDestDirPath()
        # todo: self.validateDestFilePath() ?
        if os.path.exists(self.sourcePath):
            cmd = "cp %s %s" % (
                self.sourcePath, self.destFilePath
            )
        else:
            cmd = "wget %s --tries=45 --output-document=%s %s" % (
                not self.isVerbose and "--quiet" or "",
                self.destFilePath, self.sourcePath
            )
        msg = "download source from: %s" % self.sourcePath
        self.system(cmd, msg)

    def validateSourcePath(self):
        if not self.sourcePath:
            raise Exception("No source path provided.")
        
    def validateDestDirPath(self):
        if not os.path.exists(self.destDirPath):
            raise Exception("Desintation dir not found: %s" % self.destDirPath)
        if not os.path.isdir(self.destDirPath):
            raise Exception("Desintation dir not a dir: %s" % self.destDirPath)

    ## Methods to map provision domain model onto filesystem (smells).

    def makeProvisionsPath(self):
        return self.dictionary[PROVISIONS_DIR_PATH]

    def makeProvisionPath(self, provision):
        provisionsPath = self.makeProvisionsPath()
        if not provision.name:
            raise Exception("Provision has no name: %s" % provision)
        return os.path.join(provisionsPath, provision.name)

    def makeMigrationPlanPath(self, migrationPlan):
        provisionPath = self.makeProvisionPath(migrationPlan.provision)
        return os.path.join(provisionPath, 'migrationPlans', migrationPlan.name)

    def makePurposePath(self, purpose):
        provisionPath = self.makeProvisionPath(purpose.provision)
        return os.path.join(provisionPath, 'purposes', purpose.name)

    def makeApplicationPath(self, application):
        provisionPath = self.makeProvisionPath(application.provision)
        return os.path.join(provisionPath, 'applications', application.name)

    def makeApplicationTarballPath(self, application):
        "Filesystem path to downloaded tarball."
        basePath = self.makeApplicationPath(application)
        fileName = self.makeApplicationTarballName(application)
        return os.path.join(basePath, fileName)

    def makeApplicationTarballName(self, application):
        if application.location:
            return os.path.basename(application.location)
        else:
            return self.makeTarballName(
                self.tarballBaseName or application.provision.name, application.name
            )

    def makeTarballName(self, name, version):
        return "%s-%s.tar.gz" % (name, version)

    def makeDependenciesPath(self, dependency):
        applicationPath = self.makeApplicationPath(dependency.application)
        return os.path.join(applicationPath, 'dependencies')

    def makeDependencyPath(self, dependency):
        dependenciesPath = self.makeDependenciesPath(dependency)
        fileName = os.path.basename(dependency.location) or "%s.tar.gz" % dependency.name 
        return os.path.join(dependenciesPath, fileName)

    def makeServicePath(self, service):
        applicationPath = self.makeApplicationPath(service.application)
        return os.path.join(applicationPath, 'services', service.name)

    def makeDataDumpsPath(self, service):
        servicePath = self.makeServicePath(service)
        return os.path.join(servicePath, 'dataDumps')

    def makeDataDumpPath(self, dataDump):
        dumpsPath = self.makeDataDumpsPath(dataDump.service)
        return os.path.join(dumpsPath, dataDump.name)

    def makeDomainModelDumpPath(self, dataDump):
        dumpPath = self.makeDataDumpPath(dataDump)
        return os.path.join(dumpPath, 'domainModelDump')

    def makeFilesDumpDirPath(self, dataDump):
        dumpPath = self.makeDataDumpPath(dataDump)
        return os.path.join(dumpPath, 'filesDump')

    def makeInstallPath(self, service):
        servicePath = self.makeServicePath(service)
        return os.path.join(servicePath, 'live')

    def makeLogFilePath(self, service):
        installPath = self.makeInstallPath(service)
        systemName = self.dictionary[SYSTEM_NAME]
        return os.path.join(installPath, 'var', 'log', '%s.log' % systemName)

    def makeBinPath(self, service):
        installPath = self.makeInstallPath(service)
        return os.path.join(installPath, 'bin')

    def makeAdminScriptPath(self, service):
        binPath = self.makeBinPath(service)
        fileName = '%s-admin' % self.domainObject.name
        return os.path.join(binPath, fileName)

    def makeTestScriptPath(self, service):
        binPath = self.makeBinPath(service)
        fileName = '%s-test' % self.domainObject.name
        return os.path.join(binPath, fileName)

    def makeLibPythonPath(self, service):
        installPath = self.makeInstallPath(service)
        return os.path.join(installPath, 'lib', 'python')

    def makeScriptRunnerPath(self, service):
        installPath = self.makeInstallPath(service)
        return os.path.join(installPath, 'scriptrunner')

    def makeConfigPath(self, service):
        installPath = self.makeInstallPath(service)
        return os.path.join(installPath, self.relConfigPath())

    def relConfigPath(self):
        raise Exception("Method not implemented on %s" % self.__class__)

    def provisionDirExists(self, provision):
        provisionPath = self.makeProvisionPath(provision)
        return os.path.exists(provisionPath)

    def hasProvision(self, provision):
        if not self.isNativeProvision(provision):
            return False
        if not self.provisionDirExists(provision):
            return False
        return True

    def purposeDirExists(self, purpose):
        purposePath = self.makePurposePath(purpose)
        return os.path.exists(purposePath)
        
    def applicationDirExists(self, application):
        applicationPath = self.makeApplicationPath(application)
        return os.path.exists(applicationPath)
        
    def hasApplication(self, application):
        if not self.isNativeProvision(application.provision):
            return False
        if not self.applicationDirExists(application):
            return False
        return True

    def serviceDirExists(self, service):
        servicePath = self.makeServicePath(service)
        return os.path.exists(servicePath)

    def hasService(self, service):
        if not self.isNativeProvision(service.application.provision):
            return False
        if not self.serviceDirExists(service):
            return False
        return True

    def isNativeProvision(self, provision):
        if not issubclass(provision.__class__, Provision):
            raise Exception("Not a Provision object: %s" % provision)
        return provision.name == self.domainObject.name
    
    ## Methods to install from tarball.

    def runInstaller(self, tarballPath, installPath):
        self.runPythonInstaller(tarballPath, installPath)

    def runPythonInstaller(self, tarballPath, installPath):
        if not os.path.exists(tarballPath):
            raise Exception("Tarball path doesn't exist: %s" % tarballPath)
        if not os.path.exists(installPath):
            raise Exception("Install path doesn't exist: %s" % installPath)

        # change to dir containing source archive
        sourceDirPath = os.path.dirname(tarballPath)
        if not os.path.exists(sourceDirPath):
            raise Exception("Source path has no dir: %s" % tarballPath)
        print "Changing dir to: %s" % sourceDirPath
        self.chdir(sourceDirPath)
        # extract archive
        cmd = 'tar zxvf %s' % tarballPath
        msg = "extract archive: %s" % tarballPath
        self.system(cmd, msg)
        # change to unpacked archive root
        unpackedDirPath = os.path.join(
            sourceDirPath,
            os.path.basename(tarballPath)[:-7]
        )
        self.chdir(unpackedDirPath)
        # run installer
        cmd = self.getPythonInstallCmdLine(installPath=installPath)
        self.system(cmd, "run installer: %s" % cmd)
        self.chdir(sourceDirPath)
        # remove extracted archive
        cmd = 'rm -rf %s' % unpackedDirPath
        msg = "remove unpacked source archive: %s" % unpackedDirPath
        self.system(cmd, msg)

    def getPythonInstallCmdLine(self, installPath=''):
        cmd = self.getPythonInstallCmdLineBase()
        if installPath:
            cmd += " --home=%s" % installPath
        return cmd
        
    def getPythonInstallCmdLineBase(self):
        return "python %s install" % self.getPythonSetupFilename()

    def getPythonSetupFilename(self):
        return "setup.py"

    ## Method to run the application's script runner program.

    def runScriptRunnerScript(self, scriptPath, commandString, stdoutPath="",
            stdinPath=""):
        cmd = '%s "%s"' % (scriptPath, commandString)
        if stdinPath:
            cmd += ' < %s' % stdinPath
        if stdoutPath:
            cmd += ' > %s' % stdoutPath
        print cmd
        return os.system(cmd)
        if self.isVerbose:
            return os.system(cmd)
        else:
            return commands.getstatus(cmd)


    ## Methods to manipulate config files.

    def rewriteConfigFile(self, service, updateLines):
        configPath = self.makeConfigPath(service)
        configWriter = ConfigWriter()
        print "Updating config file %s with:" % configPath
        print "\n".join(updateLines)
        configWriter.updateFile(configPath, updateLines)

    def writeNewConfigFile(self, service, configContent):
        configPath = self.makeConfigPath(service)
        configFile = open(configPath, 'w')
        configFile.write(configContent)
        configFile.close()

    def checkConfigFileExists(self, service):
        configPath = self.makeConfigPath(service)
        if not os.path.exists(configPath):
            msg = "Config file not found on: %s" % configPath
            raise Exception(msg)
    
    def substituteConfig(self, service, placeHolder, realValue):
        print "Substituting '%s' for '%s'." % (realValue, placeHolder)
        configPath = self.makeConfigPath(service)
        configFile = open(configPath, 'r')
        configContentIn = configFile.readlines()
        configFile.close()
        configContentOut = []
        # todo: Check that one and only one change is made.
        for inLine in configContentIn:
            outLine = re.sub(placeHolder, realValue, inLine)
            configContentOut.append(outLine)
        configFile = open(configPath, 'w')
        configFile.writelines(configContentOut)
        configFile.close()
        

class ProvisionPlugin(PluginBase):

    purposeLocator = RequiredFeature('PurposeLocator')
    tarballBaseName = ''

    def onProvisionCreate(self, provision):
        if self.isNativeProvision(provision):
            self.checkPluginDependencies()
            self.createProvision(provision)

    def checkPluginDependencies(self):
        pass 

    def createProvision(self, provision):
        if not self.provisionDirExists(provision):
            self.createProvisionDirs(provision)

    def createProvisionDirs(self, provision):
        provisionPath = self.makeProvisionPath(provision)
        os.makedirs(provisionPath)
        os.makedirs(os.path.join(provisionPath, 'applications'))
        os.makedirs(os.path.join(provisionPath, 'purposes'))
        os.makedirs(os.path.join(provisionPath, 'migrationPlans'))

    def onProvisionDelete(self, provision):
        if self.isNativeProvision(provision):
            self.deleteProvision(provision)

    def deleteProvision(self, provision):
        if self.provisionDirExists(provision):
            self.deleteProvisionDirs(provision)

    def deleteProvisionDirs(self, provision):
        self.chdirProvisions()
        provisionPath = self.makeProvisionPath(provision)
        cmd ='rm -rf %s' % provisionPath
        self.system(cmd, "remove provision folders")

    def onApplicationCreate(self, application):
        if self.isNativeProvision(application.provision):
            self.createApplication(application)

    def createApplication(self, application):
        if not self.applicationDirExists(application):
            self.createApplicationDirs(application)
        sourcePath = self.makeApplicationDownloadPath(application)
        destPath = self.makeApplicationPath(application)
        try:
            self.fetchFileToDir(sourcePath, destPath)
        except:
            application.delete()
            raise

    def createApplicationDirs(self, application):
        applicationPath = self.makeApplicationPath(application)
        os.makedirs(applicationPath)
        os.makedirs(os.path.join(applicationPath, 'services'))
        os.makedirs(os.path.join(applicationPath, 'dependencies'))

    def makeApplicationDownloadPath(self, application):
        "URL for downloading application tarball."
        if application.location:
            return application.location
        elif application.provision.location:
            baseLocation = application.provision.location
            if baseLocation[-1] != '/':
                baseLocation += '/'
            fileName = self.makeTarballName(
                self.tarballBaseName or application.provision.name, application.name
            )
            return "%s%s" % (baseLocation, fileName)
        else:
            msg = "Neither application nor provision has a location."
            raise Exception(msg)

    def onApplicationDelete(self, application):
        if self.isNativeProvision(application.provision):
            self.deleteApplication(application)

    def deleteApplication(self, application):
        if self.applicationDirExists(application):
            self.deleteApplicationDirs(application)

    def deleteApplicationDirs(self, application):
        self.chdirProvisions()
        applicationPath = self.makeApplicationPath(application)
        cmd = 'rm -rf %s' % applicationPath
        msg = "remove application folder"
        self.system(cmd, msg)

    def onDependencyCreate(self, dependency):
        if self.isNativeProvision(dependency.application.provision):
            self.createDependency(dependency)

    def createDependency(self, dependency):
        destPath = self.makeDependenciesPath(dependency)
        sourcePath = dependency.location
        try:
            self.fetchFileToDir(sourcePath, destPath, "%s.tar.gz" % dependency.name)
        except:
            dependency.delete()
            raise

    def onServiceCreate(self, service):
        if self.isNativeProvision(service.application.provision):
            self.assertServicePurpose(service)
            self.createService(service)

    def assertServicePurpose(self, service):
        if not self.getServicePurpose(service):
            msg = "Can't find service name '%s' in provisions purposes: %s" % (
                service.name,
                 ', '.join(service.application.provision.purposes.keys())
            )
            raise Exception(msg)

    def createService(self, service):
        if not self.serviceDirExists(service):
            self.createServiceDirs(service)

    def createServiceDirs(self, service):
        servicePath = self.makeServicePath(service)
        installPath = self.makeInstallPath(service)
        dataDumpsPath = self.makeDataDumpsPath(service)
        libPythonPath = self.makeLibPythonPath(service)
        os.makedirs(servicePath)
        os.makedirs(installPath)
        os.makedirs(dataDumpsPath)
        os.makedirs(libPythonPath)
        service.isFsCreated = True
        service.save()
        tarballPath = self.makeApplicationTarballPath(service.application)
        self.runInstaller(tarballPath, installPath)

    def onServiceDelete(self, service):
        if self.isNativeProvision(service.application.provision):
            self.deleteService(service)

    def deleteService(self, service):
        if service.isDbCreated:
            self.deleteServiceDatabase(service)
            service.isDbCreated = False
            service.save()
        if service.isFsCreated:
            self.deleteServiceDirs(service)
            service.isFsCreated = False
            service.save()

    def deleteServiceDirs(self, service):
        self.chdirProvisions()
        servicePath = self.makeServicePath(service)
        cmd = 'rm -rf %s' % servicePath
        self.system(cmd, "remove service folder")
        
    def deleteServiceDatabase(self, service):
        self.runServiceDbDelete(service)
        
    def runServiceDbDelete(self, service):
        scriptPath = self.makeScriptRunnerPath(service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.chdir(scriptDirPath)
        commandString = self.getDbDeleteCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to delete the database.")

    def getDbDeleteCmdLine(self, service):
        return "%s db delete" % self.makeAdminScriptPath(service)

        
class DomainModelApplicationPlugin(ProvisionPlugin):
    "Supports provision of domainmodel applications."

    def onMigrationPlanCreate(self, migrationPlan):
        if self.isNativeProvision(migrationPlan.provision):
            self.createMigrationPlan(migrationPlan)

    def createMigrationPlan(self, migrationPlan):
        sourcePath = migrationPlan.location
        destPath = self.makeMigrationPlanPath(migrationPlan)
        try:
            self.fetchFileToFile(sourcePath, destPath)
        except:
            migrationPlan.delete()
            raise

    def onPurposeCreate(self, purpose):
        if self.isNativeProvision(purpose.provision):
            self.createPurpose(purpose)

    def createPurpose(self, purpose):
        if not self.purposeDirExists(purpose):
            self.createPurposeDirs(purpose)

    def createPurposeDirs(self, purpose):
        purposePath = self.makePurposePath(purpose)
        os.makedirs(purposePath)
        os.makedirs(os.path.join(purposePath, 'etc'))

    def onPurposeUpdate(self, purpose):
        if self.isNativeProvision(purpose.provision):
            self.updatePurpose(purpose)

    def updatePurpose(self, purpose):
        if not purpose.service:
            return
        purposePath = self.makePurposePath(purpose)
        apacheConfigPath = os.path.join(purposePath, 'etc', 'httpd.conf')
        print "Writing '%s' purpose Apache config for %s %s: %s" % (
            purpose.name,
            purpose.service.application.name,
            purpose.service.name,
            apacheConfigPath
        )
        apacheConfigContent = self.makePurposeApacheConfig(purpose)
        # todo: Write purpose attributes into service config copy.
        apacheConfigFile = open(apacheConfigPath, 'w')
        apacheConfigFile.write(apacheConfigContent)
        apacheConfigFile.close()

    def makePurposeApacheConfig(self, purpose):
        nameValues = {}
        nameValues['SERVICE_WEB_CONFIG'] = os.path.join(
            self.makeInstallPath(purpose.service),
            'etc', 'httpd.conf'
        )
        if self.purposeLocator.distinguishesDomains():
            nameValues['DOMAIN_NAME'] = self.purposeLocator.getFQDN(purpose) 
            configFragment = """NameVirtualHost *
<VirtualHost *>
    ServerName %(DOMAIN_NAME)s
    Include %(SERVICE_WEB_CONFIG)s
    # Favicon location.
    <Location "/favicon.ico">
      SetHandler None
    </Location>
</VirtualHost>
""" % nameValues
        else:
            configFragment = """Include %(SERVICE_WEB_CONFIG)s
""" % nameValues
        return configFragment

    def onServiceEditConfig(self, service):
        if self.isNativeProvision(service.application.provision):
            self.editServiceConfig(service)

    def editServiceConfig(self, service):
        self.presentConfigFileForEditing(service)

    def presentConfigFileForEditing(self, service):
        editorName = 'editor'
        configPath = self.makeConfigPath(service)
        cmd = '%s %s' % (editorName, configPath)
        self.system(cmd, "present file for manual editing")

    def onServiceUnitTest(self, service):
        if self.isNativeProvision(service.application.provision):
            self.unitTestService(service)

    def unitTestService(self, service):
        self.runServiceTests(service)
        self.buildApacheConfig(service)

    def runServiceTests(self, service):
        self.setConfigFileForTest(service)
        self.runDbInitScript(service)
        self.runTestScript(service)

    def setConfigFileForTest(self, service):
        self.rewriteConfigFile(service, [
            '[DEFAULT]',
            'system_mode = development'
        ])

    def runDbInitScript(self, service):
        scriptPath = self.makeScriptRunnerPath(service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.chdir(scriptDirPath)
        commandString = self.getDbCreateCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to create the database.")
        service.isDbCreated = True
        service.save()
        commandString = self.getDbInitCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to initialise the database.")

    def getDbCreateCmdLine(self, service):
        return "%s db create" % self.makeAdminScriptPath(service)
        
    def getDbInitCmdLine(self, service):
        return "%s db init" % self.makeAdminScriptPath(service)

    def runTestScript(self, service):
        scriptPath = self.makeScriptRunnerPath(service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.chdir(scriptDirPath)
        commandString = self.getUnitTestCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("There were some failing tests.")

    def getUnitTestCmdLine(self, service):
        raise Exception("Method not implemented on %s" % self.__class__)

    def buildApacheConfig(self, service):
        print "Building Apache server config...."
        scriptPath = self.makeScriptRunnerPath(service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.chdir(scriptDirPath)
        commandString = self.getBuildApacheConfigCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to build Apache server configuration.")

    def onServiceCommission(self, service):
        if self.isNativeProvision(service.application.provision):
            self.commissionService(service)

    def commissionService(self, service):
        self.runServiceDbInit(service)
        self.buildApacheConfig(service)

    def runServiceDbInit(self, service):
        print "Building application service database tables...."
        scriptPath = self.makeScriptRunnerPath(service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.chdir(scriptDirPath)
        commandString = self.getDbCreateCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to create the database.")
        else:
            service.isDbCreated = True
            service.save()
        print "Importing application service domain objects...."
        commandString = self.getDbInitCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to initialise the database.")

    def onDataDumpCreate(self, dataDump):
        if self.isNativeProvision(dataDump.service.application.provision):
            self.createDataDumpDirs(dataDump)
            if dataDump.sourceDump:
                self.runDataMigration(dataDump)
            elif dataDump.location:
                self.loadDataDumpSource(dataDump)
            else:
                self.runDataDump(dataDump)

    def createDataDumpDirs(self, dataDump):
        dataDumpPath = self.makeDataDumpPath(dataDump)
        filesDumpDirPath = self.makeFilesDumpDirPath(dataDump)
        os.makedirs(dataDumpPath)
        os.makedirs(filesDumpDirPath)

    def runDataMigration(self, dataDump):
        scriptPath = self.makeScriptRunnerPath(dataDump.service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.chdir(scriptDirPath)
        sourceDumpPath = self.makeDomainModelDumpPath(dataDump.sourceDump)
        sourceDumpFile = open(sourceDumpPath, 'r')
        sourceDumpContent = sourceDumpFile.read()
        dumpedData = simplejson.loads(sourceDumpContent)
        planSteps = self.getMigrationPlanSteps(dataDump)
        # Todo: Push this down to application.
        strategy = DomainModelMigrator(dumpedData, planSteps)
        strategy.migrate()
        destDumpContent = simplejson.dumps(dumpedData)
        destDumpPath = self.makeDomainModelDumpPath(dataDump)
        destDumpFile = open(destDumpPath, 'w')
        destDumpFile.write(destDumpContent)

    def getMigrationPlanSteps(self, dataDump):
        planPath = self.makeMigrationPlanPath(dataDump.migrationPlan)
        planFile = open(planPath, 'r')
        planSteps = []
        for line in planFile.readlines():
            strippedLine = line.strip()
            if strippedLine:
                planSteps.append(strippedLine)
        return planSteps

    def loadDataDumpSource(self, dataDump):
        destPath = self.makeDomainModelDumpPath(dataDump)
        sourcePath = dataDump.location
        try:
            self.fetchFileToFile(sourcePath, destPath)
        except:
            dataDump.delete()
            raise

    def runDataDump(self, dataDump):
        self.runDomainModelDump(dataDump)
        self.runFilesDump(dataDump)

    def runDomainModelDump(self, dataDump):
        scriptPath = self.makeScriptRunnerPath(dataDump.service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.chdir(scriptDirPath)
        dumpFilePath = self.makeDomainModelDumpPath(dataDump)
        commandString = self.getMigrateDataDumpCmdLine(
            dataDump.service, dumpFilePath
        )
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to dump the domain model.")

    def getMigrateDataDumpCmdLine(self, service, dumpFilePath):
        adminScriptPath = self.makeAdminScriptPath(service)
        return "%s migratedump %s" % (adminScriptPath, dumpFilePath)

    def runFilesDump(self, dataDump):
        scriptPath = self.makeScriptRunnerPath(dataDump.service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.chdir(scriptDirPath)
        dumpDirPath = self.makeFilesDumpDirPath(dataDump)
        commandString = self.getMigrateFilesDumpCmdLine(
            dataDump.service, dumpDirPath
        )
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to dump filesystem files.")

    def onDataDumpDelete(self, dataDump):
        if self.isNativeProvision(dataDump.service.application.provision):
            self.deleteDataDumpDirs(dataDump)

    def deleteDataDumpDirs(self, dataDump):
        dataDumpPath = self.makeDataDumpPath(dataDump)
        cmd = 'rm -rf %s' % dataDumpPath
        self.system(cmd, "remove dump folder")

    def onDataDumpCommissionService(self, dataDump):
        if self.isNativeProvision(dataDump.service.application.provision):
            self.commissionServiceFromDataDump(dataDump)

    def commissionServiceFromDataDump(self, dataDump):
        self.runDataInit(dataDump)
        self.buildApacheConfig(dataDump.service)

    def runDataInit(self, dataDump):
        scriptPath = self.makeScriptRunnerPath(dataDump.service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.chdir(scriptDirPath)
        commandString = self.getDbCreateCmdLine(dataDump.service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to create service database.")
        else:
            dataDump.service.isDbCreated = True
            dataDump.service.save()
        dumpFilePath = self.makeDomainModelDumpPath(dataDump)
        commandString = self.getMigrateDataLoadCmdLine(
            dataDump.service, dumpFilePath
        )
        if self.runScriptRunnerScript(scriptPath, commandString):
            msg = "Wasn't able to initialise database from migration data."
            raise Exception(msg)

    def getMigrateDataLoadCmdLine(self, service, dumpFilePath):
        adminScriptPath = self.makeAdminScriptPath(service)
        return "%s migrateload %s" % (adminScriptPath, dumpFilePath)

    def createServiceDirs(self, service):
        # Replaces superclass behaviour.
        servicePath = self.makeServicePath(service)
        installPath = self.makeInstallPath(service)
        dataDumpsPath = self.makeDataDumpsPath(service)
        libPythonPath = self.makeLibPythonPath(service)
        # satisfy setuptools
        self.replacePythonPath(libPythonPath)
        #self.addPathToPythonPath(libPythonPath)
        # build filesystem
        os.makedirs(servicePath)
        os.makedirs(installPath)
        os.makedirs(dataDumpsPath)
        os.makedirs(libPythonPath)
        service.isFsCreated = True
        service.save()
        # install dependencies (first)
        for dependency in service.application.dependencies:
            dependencyPath = self.makeDependencyPath(dependency)
            if dependencyPath[-7:] == '.tar.gz':
                self.runPythonInstaller(dependencyPath, installPath)
            elif dependencyPath[-4:] == '.egg':
                self.copyInstallEgg(dependencyPath, libPythonPath)
            else:
                raise Exception, "Dependency's downloaded file neither .tar.gz nor .egg: %s" % dependencyPath
        # install application
        applicationPath = self.makeApplicationPath(service.application)
        tarballPath = self.makeApplicationTarballPath(service.application)
        self.runPythonInstaller(tarballPath, installPath)
        self.fixupPythonEggsForModPython(service)
        self.createPythonPackageLinks(service)
        self.writeScriptRunnerScript(service)
        #self.setExecutables(service)
        self.setTemplates(service)
        self.setConfigFile(service)
        self.generateFilesystemData(service)

    def replacePythonPath(self, newPath):
        os.environ['PYTHONPATH'] = newPath
        print "PYTHONPATH=%s" % os.environ['PYTHONPATH']

    def addPathToPythonPath(self, newPath):
        pythonPath = os.environ['PYTHONPATH']
        pythonPath = "%s:%s" % (pythonPath, newPath)
        os.environ['PYTHONPATH'] = pythonPath
        print "PYTHONPATH=%s" % os.environ['PYTHONPATH']

    def copyInstallEgg(self, tarballPath, libPythonPath):
        if not os.path.exists(tarballPath):
            raise Exception("Tarball path doesn't exist: %s" % tarballPath)
        if not os.path.exists(libPythonPath):
            raise Exception("Path to python library doesn't exist: %s" % libPythonPath)
        cmd = 'cp %s %s' % (tarballPath, libPythonPath)
        msg = "copy downloaded egg to Python library: %s" % tarballPath 
        self.system(cmd, msg)

    def fixupPythonEggsForModPython(self, service):
        # Apache mod_python imports with the imp module.
        print "Hatching setuptools' Python eggs for mod_python...."
        eggCount = 0
        libPythonPath = self.makeLibPythonPath(service)
        self.chdir(libPythonPath)
        for i in os.listdir(libPythonPath):
            if i[-4:] == '.egg':
                eggPath = os.path.join(libPythonPath, i)
                if os.path.isfile(eggPath):
                    print "Hatching zip-shaped Python egg: %s" % i
                    cmd = 'unzip %s' % eggPath
                    msg = "Unable to unzip egg file: %s" % eggPath
                    self.system(cmd, msg)
                    cmd = 'rm -rf %s' % (
                        os.path.join(libPythonPath, 'EGG-INFO')
                    )
                    self.system(cmd, "remove EGG-INFO folder")
                    eggCount += 1
                elif os.path.isdir(eggPath):
                    print "Hatching folder-shaped Python egg: %s" % i
                    for j in os.listdir(eggPath):
                        if j == 'EGG-INFO':
                            continue
                        packagePath = os.path.join(eggPath, j)
                        #cmd = 'ln -s %s %s' % (
                        #    packagePath, libPythonPath
                        #)
                        #msg = "Unable to symlink egg dir: %s" % packagePath
                        #self.system(cmd, msg)
                        
                        targetPath = os.path.join(libPythonPath, j)
                        if not os.path.exists(targetPath):
                            cmd = 'mkdir %s' % targetPath
                            msg = "Unable to make egg dir: %s" % packagePath
                            self.system(cmd, msg)
                        for nodeName in os.listdir(packagePath):
                            if not os.path.exists(os.path.join(targetPath, nodeName)):
                                cmd = 'ln -s %s %s' % (os.path.join(packagePath, nodeName), targetPath)
                                msg = "Unable to link egg stuff: %s %s %s" % (nodeName, packagePath, targetPath)
                                self.system(cmd, msg)
                        eggCount += 1
        print "Hatched %d egg(s) in support of mod_python's imp usage." % (
            eggCount
        )

    def createPythonPackageLinks(self, service):
        pass
        
    def writeScriptRunnerScript(self, service):
        print "Writing scriptrunner...."
        scriptRunnerPath = self.makeScriptRunnerPath(service)
        print scriptRunnerPath
        try:
            file = open(scriptRunnerPath, 'w')
        except IOError, inst:
            raise Exception("Couln't write scriptrunner: %s" % inst)
        
        djangoSettingsModuleName = self.getDjangoSettingsModuleName()
        file.write('#!/usr/bin/env sh\n')
        file.write('export DJANGO_SETTINGS_MODULE=%s\n' % (
                djangoSettingsModuleName
            )
        )
        file.write('export PYTHONPATH=%s\n' % self.makeLibPythonPath(service))
        serviceSettingsEnvvarName = self.getServiceSettingsEnvvarName()
        installPath = self.makeInstallPath(service)
        relConfigPath = self.relConfigPath()
        file.write('export %s=%s\n' % (
                serviceSettingsEnvvarName,
                os.path.join(
                    installPath,
                    relConfigPath,
                )
            )
        )
        file.write('$1\n')
        file.close()
        cmd = 'chmod +x %s' % scriptRunnerPath
        msg = "set execute permission on script runner: %s" % scriptRunnerPath
        self.system(cmd, msg)

    def getDjangoSettingsModuleName(self):
        return '%s.django.settings.main' % self.domainObject.name
    
    def getServiceSettingsEnvvarName(self):
        return '%s_SETTINGS' % self.domainObject.name.upper()
    
    def setExecutables(self, service):
        pass

    def setTemplates(self, service):
        pass

    def setConfigFile(self, service):
        print "Setting up application service config file...."
        self.generateNewConfigFile(service)
        self.checkConfigFileExists(service)
        print "Updating config file values...."
        updateLines = self.getUpdateLines(service)
        self.rewriteConfigFile(service, updateLines)

    def generateNewConfigFile(self, service):
        self.copyExampleConfig(service)

    def copyExampleConfig(self, service):
        configContent = self.readExampleConfigFile(service)
        self.writeNewConfigFile(service, configContent)

    def readExampleConfigFile(self, service):
        examplePath = self.makeExampleConfigPath(service)
        if not os.path.exists(examplePath):
            msg = "Example config file not found on: %s" % examplePath
            raise Exception(msg)
        exampleFile = open(examplePath, 'r')
        configContent = exampleFile.read()
        exampleFile.close()
        return configContent

    def makeExampleConfigPath(self, service):
        installPath = self.makeInstallPath(service)
        return os.path.join(installPath, self.relExampleConfigPath())

    def relExampleConfigPath(self):
        return os.path.join('etc', '%s.conf.new' % self.domainObject.name)

    def getUpdateLines(self, service):
        lines = []
        lines.append('[DEFAULT]')
        lines.append('domain_name = %s' % self.makeDomainName(service))
        lines += self.getUpdateLinesDefault(service)
        lines.append('[db]')
        lines.append('name = %s' % self.makeDbName(service))
        lines.append('user = %s' % self.makeDbUser(service))
        lines.append('pass = %s' % self.makeDbPass(service))
        lines.append('[logging]')
        lines.append('log_file = %s' % self.makeLogFilePath(service))
        lines.append('[www]')
        lines.append('apache_config_file = %s' % self.makeApacheConfigPath(service))
        lines.append('media_root = %s' % self.makeMediaRoot(service))
        lines.append('uri_prefix = %s' % self.makeUriPrefix(service))
        lines.append('media_prefix = %s' % self.makeMediaPrefix(service))
        lines.append('[django]')
        lines.append('templates_dir = %s' % self.makeTemplatesPath(service))
        lines.append('secret_key = %s' % self.makeSecretKey())
        return lines

    def makeSecretKey(self, keyLength=60):
        characterList = string.letters + string.digits
        secretKey = ''
        for i in range(keyLength):
            secretKey += random.choice(characterList)
        return secretKey

    def makeDomainName(self, service):
        purpose = self.getServicePurpose(service)
        return self.purposeLocator.getFQDN(purpose)

    def getUpdateLinesDefault(self, service):
        return []

    #def makeObjectImagesPath(self, service):
    #    return os.path.join(self.makeInstallPath(service), 'var', 'images')

    def makeDbName(self, service):
        return '%s-%s-%s-%s' % (
            self.dictionary[DB_NAME],
            service.application.provision.name,
            service.application.name,
            service.name,
        )
        
    def makeDbUser(self, service):
        return self.dictionary[DB_USER]
        
    def makeDbPass(self, service):
        return self.dictionary[DB_PASS]
        
    def makeApacheConfigPath(self, service):
        installPath = self.makeInstallPath(service)
        return os.path.join(installPath, 'etc', 'httpd.conf')

    def makeMediaRoot(self, service):
        return os.path.join(self.makeInstallPath(service), 'media')

    def makeUriPrefix(self, service):
        purpose = self.getServicePurpose(service)
        return self.purposeLocator.getPath(purpose)

    def makeMediaPrefix(self, service):
        uriPrefix = self.makeUriPrefix(service)
        if uriPrefix:
            mediaPrefix = uriPrefix + 'media'
        else:
            mediaPrefix = '/' + service.application.provision.name + 'media'
        return mediaPrefix

    def makeTemplatesPath(self, service):
        return os.path.join(self.makeInstallPath(service), 'templates')

    def generateFilesystemData(self, service):
        pass

    def relConfigPath(self):
        return os.path.join('etc', '%s.conf' % self.domainObject.name)
    
    def getBuildApacheConfigCmdLine(self, service):
        return "%s www build" % self.makeAdminScriptPath(service)
        
    def getMigrateFilesDumpCmdLine(self, service, dumpDirPath):
        adminScriptPath = self.makeAdminScriptPath(service)
        return "%s migratedumpfiles %s" % (adminScriptPath, dumpDirPath)

    def getUnitTestCmdLine(self, service):
        return self.makeTestScriptPath(service)


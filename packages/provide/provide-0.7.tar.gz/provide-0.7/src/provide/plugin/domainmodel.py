from provide.plugin.base import DomainModelApplicationPlugin
from provide.dictionarywords import DOJO_PATH, DOJO_PREFIX
import os
import pkg_resources

class Plugin(DomainModelApplicationPlugin):

    def readExampleConfigFile(self, service):
        f = self.getStream(service, 'data/etc/domainmodel.conf.new')
        configContent = f.read()
        f.close()
        return configContent

    def getStream(self, service, filePath):
        libPath = self.makeLibPythonPath(service)
        resPath = os.path.join(libPath, 'dm', filePath)
        return open(resPath, 'r')

    def writeNewConfigFile(self, service, configContent):
        path = self.makeConfigPath(service)
        os.makedirs(os.path.dirname(path))
        super(Plugin, self).writeNewConfigFile(service, configContent)

    def setTemplates(self, service):
        self.setTemplate(service, 'index.html')

    def setTemplate(self, service, templateName):
        f = self.getStream(service, os.path.join('django', 'templates', templateName))
        content = f.read()
        f.close()
        templatesPath = self.makeTemplatesPath(service)
        if not os.path.exists(templatesPath):
            os.makedirs(templatesPath)
        filePath = os.path.join(templatesPath, templateName)
        f = open(filePath, 'w')
        f.write(content)
        f.close()
        os.chmod(filePath, 0444)
    
    def buildApacheConfig(self, service):
        pass

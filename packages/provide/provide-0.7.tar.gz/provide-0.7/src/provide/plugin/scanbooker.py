from provide.plugin.base import DomainModelApplicationPlugin
from provide.dictionarywords import DOJO_PATH, DOJO_PREFIX
import os

class Plugin(DomainModelApplicationPlugin):

    def substituteConfigPaths(self, service):
        super(Plugin, self).substituteConfigPaths(service)
        self.substituteDojoPath(service)
        self.substituteDojoPrefix(service)

    def substituteDojoPath(self, service):
        placeHolder = self.makePlaceHolderDojoPath(service)
        realValue = self.makeRealValueDojoPath(service)
        self.substituteConfig(service, placeHolder, realValue)

    def makePlaceHolderDojoPath(self, service):
        return 'dojo_root\s+\=\s+\S+'

    def makeRealValueDojoPath(self, service):
        return 'dojo_root = %s' % (
            self.getDojoPath(service)
        )

    def substituteDojoPrefix(self, service):
        placeHolder = self.makePlaceHolderDojoPrefix(service)
        realValue = self.makeRealValueDojoPrefix(service)
        self.substituteConfig(service, placeHolder, realValue)

    def makePlaceHolderDojoPrefix(self, service):
        return 'dojo_prefix\s+\=\s+\S+'

    def makeRealValueDojoPrefix(self, service):
        return 'dojo_prefix = %s' % (
            self.getDojoPrefix(service)
        )

    def getDojoPrefix(self, service):
        dojoService = self.getDojoService(service)
        if dojoService:
            prefix = '/%s-%s-%s' % (
                dojoService.application.provision.name,
                dojoService.application.name,
                dojoService.name
            )
        else:
            prefix = self.dictionary[DOJO_PREFIX]
        return prefix

    def getDojoPath(self, service):
        dojoService = self.getDojoService(service)
        if dojoService:
            path = self.makeInstallPath(dojoService)
            # Dojo plugin renames the extracted archive dir to plain 'dojo'.
            path = os.path.join(
                self.makeInstallPath(dojoService),
                'dojo'  
            )
        else:
            path = self.dictionary[DOJO_PATH]
        return path

    def getDojoService(self, service):
        return self.getLinkedService(service, 'dojo')


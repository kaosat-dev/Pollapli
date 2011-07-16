import logging
import sys
import os
from twisted.python import log
from twisted.web.static import File
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.web.resource import NoResource
from twisted.internet import reactor
from twisted.enterprise import adbapi
from twisted.plugin import pluginPackagePaths
from twisted.internet import reactor, defer


from doboz_web.core.components.environments.environment_manager import EnvironmentManager
from doboz_web.core.server.rest.handlers.environment_handlers import EnvironmentsHandler
from doboz_web.core.server.rest.exception_converter import ExceptionConverter

from doboz_web.exceptions import *
from doboz_web.core.file_manager import FileManager
from doboz_web.core.components.addons.addon_manager import AddOnManager
from doboz_web.core.components.drivers.driver import DriverManager

from twisted.application.service import Application
from twisted.python import log
class MainServer():
    def __init__(self,port,rootPath,filePath,dataPath):
        #app = Application("PollapliServer")

        self.port=port
        self.rootPath=rootPath
        self.filePath=filePath
        self.dataPath=dataPath
        self.logPath=self.dataPath
        """""""""""""""""""""""""""""""""""""""""
        Initialize various subsystems /set correct paths
        """
        AddOnManager.addOnPath=os.path.join(self.rootPath,"addons")
        EnvironmentManager.envPath=os.path.join(self.dataPath,"environments")
        FileManager.rootDir=self.dataPath        
        self.environmentManager=EnvironmentManager(self.dataPath)
        
        """"""""""""""""""""""""""""""""""""""
        self.exceptionConverter=ExceptionConverter()
        self.exceptionConverter.add_exception(ParameterParseException,400 ,1,"Params parse error")
        self.exceptionConverter.add_exception(UnhandledContentTypeException,415 ,2,"Bad content type")
        self.exceptionConverter.add_exception(EnvironmentAlreadyExists,409 ,3,"Environment already exists")
        self.exceptionConverter.add_exception(EnvironmentNotFound,404 ,4,"Environment not found")
        self.exceptionConverter.add_exception(UnknownNodeType,500 ,5,"Unknown node type")
        self.exceptionConverter.add_exception(NodeNotFound,404 ,6,"Node not found")
        self.exceptionConverter.add_exception(NoDriverSet,404,7,"Node has no connector")
        self.exceptionConverter.add_exception(UnknownDriver,500,8,"Unknown connector driver type")
        self.exceptionConverter.add_exception(DeviceHandshakeMismatch,500,9,"Device handshake failed to match the on defined by the driver")

        self.setup()
        
    @defer.inlineCallbacks
    def setup(self):
        yield AddOnManager.setup()
        yield DriverManager.setup()
        yield EnvironmentManager.setup()
        
        defer.returnValue(None)
        
    def start(self):
        observer = log.PythonLoggingObserver("pollapli.core")
        observer.start()
       
       # log.startLogging(sys.stdout)
       # logfile=os.path.join(self.logPath,"pollapli.log")
       # log.startLogging(open(logfile, 'w'),setStdout=False)
        
        root = File(self.filePath)
        restRoot=Resource()
        root.putChild("rest",restRoot)
        try:
            restRoot.putChild("environments", EnvironmentsHandler("http://localhost",self.exceptionConverter,self.environmentManager))
        except Exception as inst:
            log.msg("Error in environments resource creation",str(inst), system="server", logLevel=logging.CRITICAL)
         
        factory = Site(root)
        reactor.listenTCP(self.port, factory)
        log.msg("Server started!", system="server", logLevel=logging.CRITICAL)
        reactor.run()
         #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
         #s.connect(('google.com', 0))
         #hostIp=s.getsockname()[0]
    
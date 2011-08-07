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


from doboz_web.core.components.environments.environment import EnvironmentManager
from doboz_web.core.server.rest.handlers.environment_handlers import EnvironmentsHandler
from doboz_web.core.server.rest.handlers.config_handlers import ConfigHandler

from doboz_web.core.server.rest.exception_converter import ExceptionConverter

from doboz_web.exceptions import *
from doboz_web.core.file_manager import FileManager
from doboz_web.core.components.updates.update_manager import UpdateManager
from doboz_web.core.components.drivers.driver import DriverManager
from doboz_web.core.signal_system import SignalHander
from doboz_web.core.tools import checksum_tools

from twisted.application.service import Application
from twisted.python import log
class MainServer():
    def __init__(self,port,rootPath,filePath,dataPath):
        #app = Application("PollapliServer")

        self.port=port
        self.rootPath=rootPath
        self.filePath=filePath
        self.dataPath=dataPath
        self.logPath=dataPath
        self.updatesPath=os.path.join(dataPath,"updates")
        self.addOnsPath=os.path.join(self.rootPath,"addons")
        self.environmentsPath=os.path.join(self.dataPath,"environments")
        
        if not os.path.exists(self.rootPath):
            os.makedirs(self.rootPath)
        if not os.path.exists(self.dataPath):
            os.makedirs(self.dataPath)
        if not os.path.exists(self.updatesPath):
            os.makedirs(self.updatesPath)
        if not os.path.exists(self.addOnsPath):
            os.makedirs(self.addOnsPath)
        if not os.path.exists(self.environmentsPath):
            os.makedirs(self.environmentsPath)

        
        """""""""""""""""""""""""""""""""""""""""
        Initialize various subsystems /set correct paths
        """
        UpdateManager.addOnPath=self.addOnsPath
        UpdateManager.updatesPath=self.updatesPath
        EnvironmentManager.envPath=self.environmentsPath
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
        self.exceptionConverter.add_exception(DeviceHandshakeMismatch,500,9,"Device handshake failed to match the one defined by the driver")
        self.exceptionConverter.add_exception(InvalidFile,500,10,"Invalid File")
        
        self.signalChannel="main_signal_listener"
        self.signalHandler=SignalHander(self.signalChannel)
        self.signalHandler.add_handler(channel="driver_manager")   
        self.signalHandler.add_handler(channel="update_manager")
        self.signalHandler.add_handler(channel="environment_manager")
        self.signalHandler.add_handler(channel="node_manager")
        
        self.setup()
        self.do_stuff()
    @defer.inlineCallbacks
    def do_stuff(self):
        #filePath="D:\\data\\projects\\Doboz\\add_ons_egg_tests\\virtualDevice\\dist\\VirtualDeviceAddOn-0.0.1-py2.6.egg"
        rootAddonsPath="D:\\data\\projects\\Doboz\\add_ons_egg_tests\\"
        filePath=os.path.join(rootAddonsPath,"virtualDevice\\dist\\VirtualDeviceAddOn-0.0.1-py2.6.egg")
        filePath=os.path.join(rootAddonsPath,"arduinoExample\\dist\\ArduinoExampleAddOn-0.0.1-py2.6.egg")
        #filePath=os.path.join(rootAddonsPath,"reprap\\dist\\ReprapAddOn-0.0.1-py2.6.egg")
        
        hash=yield checksum_tools.generate_hash(filePath)
        print ("md5 hash",hash)
        hashCompare=yield checksum_tools.compare_hash("80e157c0f10baef206ee2de03fae7449",filePath)
        print("md5 compare", hashCompare)
    
    def __call__(self,*args,**kwargs):
        print("server recieved message",args,kwargs)
        
    @defer.inlineCallbacks
    def setup(self):
        yield UpdateManager.setup()
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
            restRoot.putChild("config", ConfigHandler("http://localhost",self.exceptionConverter))

        except Exception as inst:
            log.msg("Error in base rest resources creation",str(inst), system="server", logLevel=logging.CRITICAL)
        
        
        factory = Site(root)
        reactor.listenTCP(self.port, factory)
        log.msg("Server started!", system="server", logLevel=logging.CRITICAL)
        reactor.run()
         #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
         #s.connect(('google.com', 0))
         #hostIp=s.getsockname()[0]
    
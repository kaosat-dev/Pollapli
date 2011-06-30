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


from doboz_web.core.components.environments.environment_manager import EnvironmentManager
from doboz_web.core.server.rest.handlers.environment_handlers import EnvironmentsHandler
from doboz_web.core.server.rest.exception_converter import ExceptionConverter

from doboz_web.exceptions import *
from doboz_web.core.file_manager import FileManager
from doboz_web.core.components.addons.addon_manager import AddOnManager


class MainServer():
    def __init__(self,port,rootPath,filePath,dataPath):
        self.port=port
        self.rootPath=rootPath
        self.filePath=filePath
        self.dataPath=dataPath
        FileManager.setRootDir(self.dataPath)
        
        self.environmentManager=EnvironmentManager(self.dataPath)
        reactor.callWhenRunning(self.environmentManager.setup)
        
        self.exceptionConverter=ExceptionConverter()
        self.exceptionConverter.add_exception(ParameterParseException,400 ,1,"Params parse error")
        self.exceptionConverter.add_exception(UnhandledContentTypeException,415 ,2,"Bad content type")
        self.exceptionConverter.add_exception(EnvironmentAlreadyExists,409 ,3,"Environment already exists")
        self.exceptionConverter.add_exception(EnvironmentNotFound,404 ,4,"Environment not found")
        self.exceptionConverter.add_exception(UnknownNodeType,500 ,5,"Unknown node type")
        self.exceptionConverter.add_exception(NodeNotFound,404 ,6,"Node not found")
        self.exceptionConverter.add_exception(NoConnectorSet,404,7,"Node has no connector")
        self.exceptionConverter.add_exception(UnknownConnector,500,8,"Unknown connector type")
        self.exceptionConverter.add_exception(UnknownDriver,500,9,"Unknown connector driver type")
    
        
        AddOnManager.addOnPath=os.path.join(self.rootPath,"addons")
        mainPath=os.path.join(self.rootPath,"addons")
#        print(sys.path)
#        
#        
#        from twisted.plugin import getPlugins
#        from zope.interface import implements
#        from twisted.plugin import IPlugin
#        from doboz_web import idoboz_web
#        import pkgutil
#        truc=pkgutil.walk_packages(path=[mainPath], prefix='')
#        for loader,name,isPkg in truc:
#            if isPkg:
#                #subPackages=
#                mod = pkgutil.get_loader(name).load_module(name)
#                print("mod")
#                try:
#                    for testplugin in getPlugins(idoboz_web.IDriver,mod):
#                        print("testplugin:",testplugin)
#                except Exception as inst:
#                    print("error in fetch plugin",inst)
                        
        
    def start(self):
        observer = log.PythonLoggingObserver("dobozweb.core.server")
        observer.start()
        
        root = File(self.filePath)
        restRoot=Resource()
        root.putChild("rest",restRoot)
        try:
            restRoot.putChild("environments", EnvironmentsHandler("http://localhost",self.exceptionConverter,self.environmentManager))
        except Exception as inst:
            log.msg("Error in environments resource creation",str(inst), logLevel=logging.CRITICAL)
         
        factory = Site(root)
        reactor.listenTCP(self.port, factory)
        log.msg("Server started!", logLevel=logging.CRITICAL)
        reactor.run()
         #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.connect(('google.com', 0))
    #hostIp=s.getsockname()[0]
    
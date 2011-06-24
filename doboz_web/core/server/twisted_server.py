import logging
import sys
import os
from twisted.python import log
from twisted.web.static import File
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.web.resource import NoResource

from twisted.internet import selectreactor
from twisted.internet import reactor
from twisted.enterprise import adbapi

from doboz_web.core.server.rest.environments_handler import EnvironmentsHandler
from doboz_web.core.components.environments.exceptions import EnvironmentAlreadyExists
from doboz_web.core.server.rest.exception_converter import ExceptionConverter
from doboz_web.core.server.rest.exceptions import ParameterParseException,UnhandledContentTypeException

    

class MainServer():
    def __init__(self,port,filepath):
        self.port=port
        self.filePath=filepath
        
        self.exceptionConverter=ExceptionConverter()
        self.exceptionConverter.add_exception(ParameterParseException,400 ,1,"Params parse error")
        self.exceptionConverter.add_exception(UnhandledContentTypeException,415 ,2,"bad content type")
        self.exceptionConverter.add_exception(EnvironmentAlreadyExists,409 ,3,"environment already exists")
    
    def start(self):
        observer = log.PythonLoggingObserver("dobozweb.core.server")
        observer.start()
        #root = File(self.filePath)
        #print(self.filePath)
        root=Resource()
        restRoot=Resource()
        root.putChild("rest",restRoot)
        try:
            restRoot.putChild("environments", EnvironmentsHandler("http://localhost",self.exceptionConverter,self.environmentManager))
        except Exception as inst:
            print("error in  resource creation",inst)
         
        
        factory = Site(root)
        reactor.listenTCP(self.port, factory)
        #webbrowser.open("http://192.168.0.12:8000")
        log.msg("Server started!", logLevel=logging.CRITICAL)
        reactor.run()
    
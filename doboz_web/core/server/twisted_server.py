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

#import webbrowser

from doboz_web.core.server.rest.envs_handler import EnvsRestHandler
from doboz_web.core.server.rest.env_handler import EnvRestHandler

class MainServer():
    def __init__(self,port,filepath):
        self.port=port
        self.filePath=filepath
        
    def start(self):
        observer = log.PythonLoggingObserver("dobozweb.core.server")
        observer.start()
        
        root = File(self.filePath)
        print(self.filePath)
        
        restHandler=Resource()
        try:
            restHandler.putChild("environments", EnvsRestHandler(None,self.environmentManager))
        except Exception as inst:
            print("error in root resource creation",inst)
        root.putChild("REST", restHandler)

        factory = Site(root)
        reactor.listenTCP(self.port, factory)
        #webbrowser.open("http://192.168.0.12:8000")
        reactor.run()
    
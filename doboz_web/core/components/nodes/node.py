"""
.. py:module:: node
   :synopsis: generic node class, parent of hardware and software nodes
"""
import logging
import time
import datetime
import uuid
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from doboz_web.core.components.automation.task_manager import TaskManager

from doboz_web.exceptions import UnknownDriver,NoDriverSet

from twisted.plugin import getPlugins
from doboz_web import idoboz_web
from doboz_web.core.components.addons.addon_manager import AddOnManager


class Node(DBObject):
    """
    Base class for all nodes: a hardware node is a software component handling either a physical device such as a webcam, reprap , arduino etc
    or some software node (pachube etc)
    """
    BELONGSTO = ['environment']
   # HASONE =['reprap_capability']
    def __init__(self,name="node",description="base node",type="node",*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.nodes.node")
        self.name=name
        self.type=type
        self.description=description
        self.isRunning=False  
        self.driver=None 
        self.taskManager=TaskManager(self)
        self.components=[]
        """For Uptime calculation"""
        self.startTime=time.time()
    
    def setup(self):
        def addDriver(drivers,node):
            if len(drivers)>0:
                node.driver=drivers[0] 
                #just a cheap hack for now
                #node.connector.set_driver(TeacupDriver(speed=115200))
                #log.msg("Node with id",self.id,", connector",self.connector.__class__.__name__, "setup successfully", logLevel=logging.CRITICAL)

       # SerialConnector.find(where=['node_id = ?', self.id]).addCallback(addDriver,self)
        
    
    
    def __getattr__(self, attr_name):
        if hasattr(self.taskManager, attr_name):
            return getattr(self.taskManager, attr_name)
        else:
            raise AttributeError(attr_name) 
           
    def _toDict(self):
        return {"node":{"id":self.id,"name":self.name,"description":self.description,"type":self.type,"connector":{"status":{"connected":True},"type":None,"driver":None},"link":{"rel":"node"}}}
   
    
    @defer.inlineCallbacks
    def set_driver(self,type="Serial",driverType="Default",driverParams={},*args,**kwargs):
        """
        Method to set this node's connector 
        Params:
        driver: a connector instance
        
        WARNING: cheap hack for now, always defaults to serial
        connector
        """
        
        #self.connector=yield SerialConnector().save()
        #self.connector.node.set(self)
        
        driver=None
        plugins= (yield AddOnManager.get_plugins(idoboz_web.IDriver))
        print("plugin list",plugins)
        
        for driverKlass in plugins:#(yield AddOnManager.get_plugins(idoboz_web.IDriver)):
            #log.msg("found driver",driverKlass, logLevel=logging.CRITICAL)
            if driverType==driverKlass.__name__.lower():
                self.driver=driverKlass(**driverParams)
                self.driver.set_connector(SerialConnector())   
                print(self.driver)          
                #self.driver.save()  
                log.msg("Set driver of node",self.id, "to serial plus, and driver of type", driverType," and params",str(driverParams), logLevel=logging.CRITICAL)
                break
        if not self.driver:
            raise UnknownDriver()
        
        defer.returnValue(self.driver)
        
#        if hasattr(self.connector, 'events'):    
#             self.connector.events.disconnected+=self._on_connector_disconnected
#             self.connector.events.reconnected+=self._on_connector_reconnected  
#             self.connector.events.OnDataRecieved+=self._on_data_recieved
#        #self.taskManager.connector=self.connector

        
        

            
        
        
    def get_connector(self):
        if self.driver:
            return self.driver 
        else: 
            raise NoDriverSet()

    
    def delete_driver(self):
        if self.driver:
            self.driver.disconnect()     
            self.driver=None
            
        log.msg("Disconnected and removed connector", logLevel=logging.CRITICAL)
   
        
    def start(self):
        """
        start this node
        """
        pass
    def stop(self):
        """stop this node
        """
        
    def add_component(self,component,*args,**kwargs):
        pass
    
    def remove_component(self,component,*args,**kwargs):
        pass
    
    
    def connect(self):
        d=defer.Deferred()
        def doConnect(driver):
            driver.connect()
            return driver
        d.addCallback(doConnect)
        d.callback(self.driver)
        return d
    
           
    def disconnect(self):
        d=defer.Deferred()
        def doDisconnect(driver):
            connector.driver()
            return driver
        d.addCallback(doDisconnect)
        d.callback(self.driver)
        return d
    
    def _on_driver_connected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"  
    
    def _on_driver_disconnected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"
      
    def _on_driver_reconnected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"  


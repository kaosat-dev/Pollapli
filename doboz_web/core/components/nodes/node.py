"""
.. py:module:: node
   :synopsis: generic node class, parent of hardware and software nodes
"""
import logging, time, datetime, uuid,ast
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
from doboz_web.core.components.drivers.driver import Driver,DriverManager

 

class Node(DBObject):
    """
    Base class for all nodes: a hardware node is a software component handling either a physical device such as a webcam, reprap , arduino etc
    or some software node (pachube etc)
    """
    BELONGSTO = ['environment']
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
        
        """this is to ensure no 'asynch clash' occurs when replacing the current driver"""
        self.driverLock=defer.DeferredSemaphore(1)
    
    @defer.inlineCallbacks
    def setup(self):
        
        @defer.inlineCallbacks
        def addDriver(drivers,node):
            if len(drivers)>0:
                driver=drivers[0]               
                driver.options=ast.literal_eval(driver.options)
                self.driver=yield DriverManager.load(driver)
            defer.returnValue(None) 
        yield Driver.find(where=['node_id = ?', self.id]).addCallback(addDriver,self)
        yield self.taskManager.setup()
        log.msg("Node with id",self.id, "setup successfully", logLevel=logging.CRITICAL,system="Node")

        defer.returnValue(None)
        
    def __getattr__(self, attr_name):
        if hasattr(self.taskManager, attr_name):
            return getattr(self.taskManager, attr_name)
        else:
            raise AttributeError(attr_name) 
           
    def _toDict(self):
        return {"node":{"id":self.id,"name":self.name,"description":self.description,"type":self.type,"driver":{"status":{"connected":True},"type":None,"driver":None},"link":{"rel":"node"}}}
   
    
    @defer.inlineCallbacks
    def set_driver(self,params={},*args,**kwargs):
        """
        Method to set this node's connector 
        Params:
        returns : a driver instance
        connector
        """
        
        @defer.inlineCallbacks
        def update():
            yield self.delete_driver()
            self.driver=yield DriverManager.create(parentNode=self,**kwargs)
            
            log.msg("Set driver of node",self.id," with params ", kwargs,system="Node")
            defer.returnValue(None)
        yield self.driverLock.run(update)
     
        
        defer.returnValue(self.driver)
                    
        
    def get_driver(self):
        if self.driver:
            return self.driver 
        else: 
            raise NoDriverSet()
    
    @defer.inlineCallbacks
    def delete_driver(self):
        if self.driver:
            self.driver.disconnect()    
            DriverManager.unregister_driver(self.driver) 
            yield self.driver.delete()
            self.driver=None         
            log.msg("Disconnected and removed driver", logLevel=logging.CRITICAL,system="Node")
        defer.returnValue(None)
        
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
    
    
    def connect(self,*args,**kwargs):
        d=defer.Deferred()
        def doConnect(driver):
            driver.connect(*args,**kwargs)
            return driver
        d.addCallback(doConnect)
        reactor.callLater(0,d.callback,self.driver)
        return d
           
    def disconnect(self):
        d=defer.Deferred()
        def doDisconnect(driver):
            driver.disconnect()
            return driver
        d.addCallback(doDisconnect)
        reactor.callLater(0,d.callback,self.driver)
        return d
    
    def _on_driver_connected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"  
    
    def _on_driver_disconnected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"
      
    def _on_driver_reconnected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"  


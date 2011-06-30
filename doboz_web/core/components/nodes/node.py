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
#from doboz_web.core.components.connectors.hardware.serial.serial_plus import SerialPlus
from doboz_web.core.components.connectors.hardware.serial.serial_connector import SerialConnector
from doboz_web.core.components.connectors.hardware.drivers.reprap.Teacup.teacup_driver import TeacupDriver
from doboz_web.core.components.connectors.hardware.drivers.reprap.FiveD.fived_driver import FiveDDriver
from doboz_web.exceptions import UnknownDriver,NoConnectorSet

from twisted.plugin import getPlugins
from doboz_web import idoboz_web

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
        self.connector=None 
        self.taskManager=TaskManager(self)
        self.components=[]
        """For Uptime calculation"""
        self.startTime=time.time()
    
    def setup(self):
        def addConnector(connectors,node):
            if len(connectors)>0:
                node.connector=connectors[0] 
                #just a cheap hack for now
                node.connector.set_driver(TeacupDriver(speed=115200))
                log.msg("Node with id",self.id,", connector",self.connector.__class__.__name__, "setup successfully", logLevel=logging.CRITICAL)

        SerialConnector.find(where=['node_id = ?', self.id]).addCallback(addConnector,self)
        
    
    
    def __getattr__(self, attr_name):
        if hasattr(self.taskManager, attr_name):
            return getattr(self.taskManager, attr_name)
        else:
            raise AttributeError(attr_name) 
           
    def _toDict(self):
        return {"node":{"id":self.id,"name":self.name,"description":self.description,"type":self.type,"connector":{"status":{"connected":True},"type":None,"driver":None},"link":{"rel":"node"}}}
   
    @defer.inlineCallbacks
    def set_driver(self,driverType="Default",driverParams={},*args,**kwargs):
        pass
    
    @defer.inlineCallbacks
    def set_connector(self,type="Serial",driverType="Default",driverParams={},*args,**kwargs):
        """
        Method to set this node's connector 
        Params:
        connector: a connector instance
        driver=
        WARNING: cheap hack for now, always defaults to serial
        connector
        """
        
        self.connector=yield SerialConnector().save()
        self.connector.node.set(self)
        
        driver=None
        if driverType== "teacup":
            driver=TeacupDriver(**driverParams)
        elif driverType=="fived":
            driver=FiveDDriver(**driverParams)
        if driver:
            self.connector.set_driver(driver) 
        else :
            raise UnknownDriver()
        
        self.connector.save()
        
        log.msg("Set connector of node",self.id, "to serial plus, and driver of type", driverType," and params",str(driverParams), logLevel=logging.CRITICAL)

#        if hasattr(self.connector, 'events'):    
#             self.connector.events.disconnected+=self._on_connector_disconnected
#             self.connector.events.reconnected+=self._on_connector_reconnected  
#             self.connector.events.OnDataRecieved+=self._on_data_recieved
#        #self.taskManager.connector=self.connector

        print("plugin test")
        import doboz_web.plugins as plugins
        for driver in getPlugins(idoboz_web.IDriver,plugins):
            print("driver",driver)
            print("params",driverParams)
            driverInstance=driver(**driverParams)
            print(driverInstance)
            print(driverInstance.tutu())
        
        
    def get_connector(self):
        if self.connector:
            return self.connector 
        else: 
            raise NoConnectorSet()

    
    def delete_connector(self):
        if self.connector:
            self.connector.disconnect()     
            self.connector=None
            
        log.msg("Disconnected and removed connector", logLevel=logging.CRITICAL)
   
    def set_driver(self): 
        """Method to set a this nodes connector's driver 
        Params:
        WARNING: cheap hack for now, always defaults to serial
        connector
        """
        
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
        def doConnect(connector):
            connector.connect()
            return self.connector
        d.addCallback(doConnect)
        d.callback(self.connector)
        return d
    
           
    def disconnect(self):
        d=defer.Deferred()
        def doDisconnect(connector):
            connector.disconnect()
            return self.connector
        d.addCallback(doDisconnect)
        d.callback(self.connector)
        return d
    
    def _on_connector_connected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"  
    
    def _on_connector_disconnected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"
      
    def _on_connector_reconnected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"  


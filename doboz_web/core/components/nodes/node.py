"""
.. py:module:: node
   :synopsis: generic node class, parent of hardware and software nodes
"""
import logging
import time
import datetime
import uuid

from doboz_web.core.components.automation.task_manager import TaskManager

from doboz_web.core.components.connectors.hardware.serial.serial_plus import SerialPlus
from doboz_web.core.components.drivers.reprap.Teacup.teacup_driver import TeacupDriver
from doboz_web.core.components.drivers.reprap.FiveD.fived_driver import FiveDDriver

class Node(object):
    """
    Base class for all nodes: a hardware node is a software component handling either a physical device such as a webcam, reprap , arduino etc
    or some software node (pachube etc)
    """
    def __init__(self):
        self.logger=logging.getLogger("dobozweb.core.components.nodes.node")
        self.isRunning=False  
        self.connector=None 
        self.taskManager=TaskManager()
        self.components=[]
        self.id=-1
        """For Uptime calculation"""
        self.startTime=time.time()
    
    def __getattr__(self, attr_name):
        if hasattr(self.taskManager, attr_name):
            return getattr(self.taskManager, attr_name)
        else:
            raise AttributeError(attr_name)    
    
    def set_connector(self,connectorType="Serial",driverType="Default",driverParams={},*args,**kwargs):
        """
        Method to set this node's connector 
        Params:
        connector: a connector instance
        driver=
        WARNING: cheap hack for now, always defaults to serial
        connector
        """
        self.connector=SerialPlus()
        driver=None
        if driverType== "teacup":
            driver=TeacupDriver(**driverParams)
        elif driverType=="fived":
            driver=FiveDDriver(**driverParams)
        if driver:
            self.connector.set_driver(driver) 
        else :
            raise Exception("Incorrect driver")
        
        self.logger.critical("Set connector of node %d to serial plus, and driver of type %s and params: %s",self.id,driverType,str(driverParams))
        if hasattr(self.connector, 'events'):    
             self.connector.events.disconnected+=self._on_connector_disconnected
             self.connector.events.reconnected+=self._on_connector_reconnected  
             self.connector.events.OnDataRecieved+=self._on_data_recieved
        #self.taskManager.connector=self.connector
        
    def set_driver(self): 
        """Method to set a this nodes connector's driver 
        Params:
        WARNING: cheap hack for now, always defaults to serial
        connector
        """
        
        
    def add_component(self,component,*args,**kwargs):
        pass
    
    def remove_component(self,component,*args,**kwargs):
        pass
    
    def connect(self):
        self.connector.connect()  
               
    def disconnect(self):
        self.connector.disconnect()
        
    def _on_connector_connected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"  
    
    def _on_connector_disconnected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"
      
    def _on_connector_reconnected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"  

       

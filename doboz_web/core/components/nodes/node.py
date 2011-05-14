"""
.. py:module:: node
   :synopsis: generic node class, parent of hardware and software nodes
"""
import logging
import time
import datetime
import uuid

from doboz_web.core.components.automation.task_manager import TaskManager

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
    
    def set_connector(self,connector):
        """
        Sets what connector to use
         
        """
        self.connector=connector
        if hasattr(self.connector, 'events'):    
             self.connector.events.disconnected+=self._on_connector_disconnected
             self.connector.events.reconnected+=self._on_connector_reconnected  
             self.connector.events.OnDataRecieved+=self._on_data_recieved
    
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

       

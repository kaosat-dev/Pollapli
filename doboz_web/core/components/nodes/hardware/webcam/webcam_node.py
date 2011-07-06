
"""
.. py:module:: webcam_node
   :synopsis: hardware node for webcam handling. 
"""
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

from doboz_web.core.tools.event_sys import *
from doboz_web.core.components.nodes.hardware.hardware_node_capability import HardwareNodeCapability
from doboz_web.core.components.nodes.node import Node

from doboz_web.core.tools.event_sys import *

class WebcamNode(DBObject):
    """
    webcam Node class
    """
    BELONGSTO   = ['node','environment'] 
    def __init__(self,*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.logger=logging.getLogger("dobozweb.core.WebcamNode")
        self.logger.setLevel(logging.ERROR)
        HardwareNode.__init__(self)
        self.isRunning=False  
        self.connector=None 
        self.driver=None
        self.automation=None
        self.components=[]
        self.filePath=None
        self.logger.critical("Webcam Node Init Done")
        
    def set_connector(self,connector):
        """Sets what connector to use """
        self.connector=connector
        if hasattr(self.connector, 'events'):    
             #self.connector.events.OnDataRecieved+=self.data_recieved
             self.connector.events.disconnected+=self._on_connector_disconnected
             self.connector.events.reconnected+=self._on_connector_reconnected
        self.connector.start()   
    
    def start(self):
        """
        Sets up the capture process
        """
        self.connector.set_capture(self.filePath)
        self.logger.critical("Starting Webcam Node")
        
    def _on_connector_disconnected(self,args,kargs):
        """
        Function that handles possible Webcam connector disconnection 
        """
        self.logger.critical("Webcam connector disconnected !!!")
        self.isPaused=True
    
       
    def _on_connector_reconnected(self,args,kargs):
        """
        Function that handles possible Webcam connectorreconnection
        """ 
        self.logger.critical("Webcam connectorreconnected !!!")
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from doboz_web.core.tools.event_sys import *

class HardwareConnectorEvents(Events):
    """
    Class defining events associated to HardwareConnector Class
    """
    __events__=('OnDataRecieved','connected', 'disconnected', 'reconnected')


class HardwareConnector(DBObject):
    BELONGSTO = ['node']
    def __init__(self,driver=None,*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.isConnected=False
        self.currentErrors=0
        self.maxErrors=5
        self.driver=None
        self.events=HardwareConnectorEvents()
        
    def set_driver(self,driver):
        """Sets what driver to use : a driver formats the data sent to the connector !!
        And may also contain additional settings for the connector"""
        self.driver=driver
        self.seperator=driver.seperator
        self.speed=driver.speed
        self.reset_seperator()
        
    def connect(self,*args,**kwargs):
        """
        Establish connection to hardware
        """
        raise NotImplementedException()
    
    def disconnect(self):
        raise NotImplementedException()
    
    def fetch_data(self):
        """cheap hack for now"""
        pass
    
    def send_command(self,command):
        """
        Add a command to the hardware abstractions command queue
        """
        raise NotImplementedException()
        
    def add_command(self,command):
        """
        Add a command to the hardware abstractions command queue
        """
        raise NotImplementedException()
    
    def clear_commands(self):
        """
        Clear all the commands of the hardware abstraction's command queue
        """
        raise NotImplementedException()
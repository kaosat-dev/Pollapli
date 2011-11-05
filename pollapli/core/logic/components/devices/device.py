"""
.. py:module:: node
   :synopsis: generic node class, parent of hardware and software nodes, node manager class etc
"""
import logging, time, datetime, uuid,ast
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.plugin import getPlugins

from pollapli import ipollapli
from pollapli.exceptions import UnknownDriver,NoDriverSet
from pollapli.core.logic.components.updates.update_manager import UpdateManager
from pollapli.core.logic.components.drivers.driver import Driver,DriverManager
from pollapli.exceptions import UnknownDeviceType,DeviceNotFound
from pollapli.core.logic.tools.signal_system import SignalHander
from pollapli.core.logic.components.base_component import BaseComponent

class DeviceStatus(object):
    EXPOSE=["isActive"]
    def __init__(self):
        self.isActive=False
        
    def start(self): 
        self.isActive=True
            
    def stop(self):
        self.isActive=False
                
    def _toDict(self):
        return {"status":{"active":self.isActive}}
  
class Device(BaseComponent):
    """
    Base class for all Device: a Device is a software abstraction for a physical device such as a webcam, reprap , arduino etc
    """
    def __init__(self, parent=None, name="base_device",description="base device",*args,**kwargs):
        BaseComponent.__init__(self, parent)
        self._name=name
        self._description=description
        self._status = "inactive"
        self._driver=None 
        #self.status=DeviceStatus()
            
        """this is to ensure no 'asynch clash' occurs when replacing the current driver"""
        self.driverLock=defer.DeferredSemaphore(1)
        #self.rootElement=DeviceComponent("root")

        """this is for internal comms handling"""
        self.signalChannelPrefix=str(self._id)
        self.signalChannel="node"+self.signalChannelPrefix+"."+self._name
        self.signalHandler=SignalHander(self.signalChannel)
        #self.signalHandler.add_handler(handler=self.variable_get,signal="get")
        
    def __eq__(self, other):
        return self._id == other._id and self._name == other._name and self._description == other._description and self._status == other._status
    def __ne__(self, other):
        return not self.__eq__(other)
    
    @defer.inlineCallbacks
    def setup(self):
        self.driver=yield DriverManager.load(parentDevice=self)
        self.signalChannelPrefix="environment_"+str(self._parent._id)+".node_"+str(self._id)
        log.msg("Device with id",self._id, "setup successfully",system="Device", logLevel=logging.CRITICAL)
        
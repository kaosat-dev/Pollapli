"""
.. py:module:: environment
   :synopsis: environment related : environment class and environment manager class.
"""
import os, random, logging,imp,inspect, time, datetime, shutil, imp
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

from pollapli.exceptions import EnvironmentAlreadyExists,EnvironmentNotFound
from pollapli.core.logic.components.base_component import BaseComponent
from pollapli.core.logic.components.devices.device_manager import DeviceManager
from pollapli.core.logic.components.tasks.task_manager import TaskManager
from pollapli.core.logic.tools.signal_system import SignalDispatcher

class Environment(BaseComponent):
    def __init__(self,parent = None, persistenceLayer= None, name="home",description="Add Description here",status="active",*args,**kwargs):
        BaseComponent.__init__(self, parent)
        self._persistenceLayer = persistenceLayer
        self.name=name
        self.description=description
        self.status=status
        self._devices=DeviceManager(self)
        self._tasks=TaskManager(self)
        
    def __eq__(self, other):
        return self.cid == other.cid and self.name == other.name and self.description == other.description and self.status == other.status
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __str__(self):
        return "%s %s %s" %(self.name,self.description,self.status)
    
    def __getattr__(self, attr_name):
        if hasattr(self._devices, attr_name):
            return getattr(self._devices, attr_name)
        elif hasattr(self._tasks, attr_name):
            return getattr(self._tasks, attr_name)
        else:
            raise AttributeError(attr_name)
    """
    ####################################################################################
    Configuration and shutdown methods
    """
    @defer.inlineCallbacks
    def setup(self):
        """
        Method configuring additional elements of the current environment
        """
        yield self._devices.setup()
        yield self._tasks.setup()
        log.msg("Environment ",self.name ,"with id", self.cid," setup correctly", logLevel=logging.CRITICAL, system="environment")

    def teardown(self):
        """
        Tidilly shutdown and cleanup after environment
        """
"""
.. py:module:: reprap_node
   :synopsis: hardware node for reprap handling.
"""
import logging
import time
import datetime
import sys
import os
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


class ReprapCapability(DBObject):     
    """
    A reprap node : hardware node  in the case of a reprap: endstops, temperature sensors, steppers, heaters
    """
    BELONGSTO   = ['node','environment'] 
    def __init__(self,info="mk",*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.info=info
        
        #HardwareNode.__init__(self,name,description,type,*args,**kwargs)
        self.startTime=time.time()
        self.rootPath=None
        self.gcodeSuffix="\n"
        log.msg("Reprap Capability Init Done", system="reprap node", logLevel=logging.CRITICAL)
    
    def __getattr__(self, attr_name):
        try:
            if hasattr(self.node, attr_name) :
                
                return getattr(self.node, attr_name)
            else:
                pass#raise AttributeError(attr_name) 
        except Exception as inst:
            #TODO : only catch ReferenceNotSavedError
            #else: raise AttributeError
            #print("error",inst)
            pass
        

           
   

Registry.register(Node, ReprapCapability)
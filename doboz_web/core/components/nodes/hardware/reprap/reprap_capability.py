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
from doboz_web.core.components.nodes.hardware.hardware_node import HardwareNode
from doboz_web.core.components.nodes.node import Node

"""TODO: Make tasks in tasks be weak refs""" 
class ReprapManagerEvents(Events):
    __events__=('OnLineParsed','OnTotalLinesSet','OnTotalLayersSet','OnPathSet','OnPositionChanged')

class ReprapCapability(DBObject):
    BELONGSTO   = ['node','environment']      
    """
    A reprap node : hardware node  in the case of a reprap: endstops, temperature sensors, steppers, heaters
    """
    def __init__(self,info="mk",*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.info=info
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.nodes.hardware.reprap")
        #HardwareNode.__init__(self,name,description,type,*args,**kwargs)
        self.startTime=time.time()
        self.rootPath=None
        self.events=ReprapManagerEvents() 
        self.gcodeSuffix="\n"
        log.msg("Reprap Capability Init Done", logLevel=logging.CRITICAL)
    
    def __getattr__(self, attr_name):
        print("in getattr",attr_name)
        try:
            if hasattr(self.node, attr_name) :
                
                return getattr(self.node, attr_name)
            else:
                #return getattr(self,attr_name)
                pass#raise AttributeError(attr_name) 
        except Exception as inst:
            #TODO : only catch ReferenceNotSavedError
            #else: raise AttributeError
            print("error",inst)
            pass
        
    def set_paths(self,rootPath):
        """
        Configure paths
        """
        self.rootPath=rootPath

    def startPause(self):
        """
        Switches between active and inactive mode.
        """
        if self.currentTask:
            self.currentTask.startPause()
           
    
    def start(self):
        """
        Start the whole system
        """          
        self.isRunning=True
        self.isStarted=True
        self.totalTime=0
        self.startTime=time.time()  
        log.msg("Starting Reprap Node", logLevel=logging.CRITICAL)
    
    def stop(self):
        """
        Stops the current task and shuts down
        """
        log.msg("stopped Reprap Node", logLevel=logging.CRITICAL)
        self.isPaused=True
        self.serial.tearDown()
        #self.totalTime+=time.time()-self.startTime
    
    def sendText(self,text):
        """
        Simple function to send text over serial
        """
       
        self.serial.send_data(text+self.gcodeSuffix)   
      
    def _on_data_recieved(self,args,kargs):
        self.logger.debug("event recieved from reprap %s",str(kargs))
        try:
            answer=kargs.answer
            if  "T:" in answer:
                try:
                    raw=answer.split(' ')
                    self.headTemp=float(raw[0].split(':')[1])
                    self.bedTemp=float(raw[1].split(':')[1])
                except Exception as inst:
                    log.msg("Error in temperature readout",str(inst), logLevel=logging.CRITICAL)
        except:
            pass
       
        
         #   self.logger.critical("Bed Temperature: %d Extruder Temperature %d",self.bedTemp,self.headTemp)

        
    def _on_connector_disconnected(self,args,kargs):
        """
        Function that handles possible serial port disconnection
        """
        self.logger.critical("Serial port disconnected !!!")
        self.isPaused=True
    
       
    def _on_connector_reconnected(self,args,kargs):
        """
        Function that handles possible serial port reconnection
        """ 
        self.logger.critical("Serial port reconnected !!!")
        
#        if self.lastLine and self.source and self.isStarted:
#            time.sleep(5)
#            self.connector.send_command("G90")
#            self.connector.send_command("G92 "+self.lastLine[2:-1])
#            self.reconnectionCommand="G1 "+self.lastLine[2:-1]
#            print("RE INIT COMMAND",self.reconnectionCommand)     
#            self.connector.send_command(self.reconnectionCommand) 

Registry.register(Node, ReprapCapability)
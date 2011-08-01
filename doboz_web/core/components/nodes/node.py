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
from doboz_web.core.components.automation.task import TaskManager

from doboz_web.exceptions import UnknownDriver,NoDriverSet

from twisted.plugin import getPlugins
from doboz_web import idoboz_web
from doboz_web.core.components.addons.addon_manager import AddOnManager
from doboz_web.core.components.drivers.driver import Driver,DriverManager
from doboz_web.core.tools.point import Point

 
class Node(DBObject):
    """
    Base class for all nodes: a hardware node is a software component handling either a physical device such as a webcam, reprap , arduino etc
    or some software node (pachube etc)
    """
    BELONGSTO = ['environment']
    def __init__(self,type="node",name="base_node",description="base node",options={},*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.nodes.node")
        self.name=name
        self.type=type
        self.description=description
        self.options=options
        self.isRunning=False  
        self.driver=None 
        self.taskManager=TaskManager(self)
        
        #################
        self.variables=[]
        self.elements=[]
        self.tools=[]

        
        """this is to ensure no 'asynch clash' occurs when replacing the current driver"""
        self.driverLock=defer.DeferredSemaphore(1)
    
    @defer.inlineCallbacks
    def setup(self):
        self.driver=yield DriverManager.load(parentNode=self)
        yield self.taskManager.setup()
        log.msg("Node with id",self.id, "setup successfully", logLevel=logging.CRITICAL,system="Node")

        defer.returnValue(None)
    
    
    def elementsandVarsTest(self):
        """test method, for experimental composition of nodes: this creates all the elements for a basic 
        reprap type node"""
        
        """CARTESIAN BOT DEFINITION"""
        """3d Position"""
        pos=Variable(self,"3d_position",Point(['x','y','z']),"vector","mm",None,"memory",3,True,None,None,['x','y','z'])     
        """all the motors/actors controlling the 3d Position"""
        mot1=Actor(type="StepperMotor",name="x_motor",tool="cartesianBot",boundVariable=pos,variableChannel='x')
        mot2=Actor(type="StepperMotor",name="y_motor",tool="cartesianBot",boundVariable=pos,variableChannel='y')
        mot3=Actor(type="StepperMotor",name="z_motor",tool="cartesianBot",boundVariable=pos,variableChannel='z')
        """all the sensors giving feedback on  the 3d Position"""
        endStop1=Sensor(type="end_sensor",name="x_startSensor",tool="cartesianBot",boundVariable=pos,variableChannel='x')
        endStop2=Sensor(type="end_sensor",name="x_endSensor",tool="cartesianBot",boundVariable=pos,variableChannel='x')
        endStop3=Sensor(type="end_sensor",name="y_startSensor",tool="cartesianBot",boundVariable=pos,variableChannel='y')
        endStop4=Sensor(type="end_sensor",name="y_endSensor",tool="cartesianBot",boundVariable=pos,variableChannel='y')
        endStop5=Sensor(type="end_sensor",name="z_startSensor",tool="cartesianBot",boundVariable=pos,variableChannel='z')
        endStop6=Sensor(type="end_sensor",name="z_endSensor",tool="cartesianBot",boundVariable=pos,variableChannel='z')
        """add all these to the current node"""
        self.add_variable(pos)
        self.add_elements([mot1,mot2,mot3,endStop1,endStop2,endStop3,endStop4,endStop5,endStop6])
        pos.attach_sensors([(endStop1,endStop1.channel),(endStop2,endStop2.channel),(endStop3,endStop3.channel),
                            (endStop4,endStop4.channel),(endStop5,endStop5.channel),(endStop6,endStop6.channel)])
        pos.attach_actors([(mot1,mot1.channel),(mot2,mot2.channel),(mot3,mot3.channel)])
        
        """EXTRUDER 1 DEFINITION"""
        """two variables"""
        head_temp=Variable(self,"head_temp",0,"temperature","celcius")
        extrudate_lng=(self,"filament_extrudate",Point(['e']),"vector","mm")
        """all the actors controlling the extrusion of this print head"""
        extrudMot=Actor(type="StepperMotor",name="e_motor1",tool="PrintHead",boundVariable=extrudate_lng,variableChannel='e')
        head_heater=Actor(type="Heater",name="extruder1_heater",tool="PrintHead",boundVariable=head_temp)
        """all the sensors giving feedback on the extrusion of this print head"""
        head_tempSensor=Sensor(type="temperature_sensor",name="extruder1_temp_sensor",tool="PrintHead",boundVariable=head_temp)
     
        extrudate_lng.attach_actor(extrudMot,'e')
        head_temp.attach_both([(head_heater,None)],[(head_tempSensor,None)])
        
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
        
    def add_variable(self,variable,*args,**kwarg):
        self.variables.append(variable)
    def remove_variable(self,variable,*args,**kwargs):
        self.variables.remove(variable)
        
    def add_element(self,element,*args,**kwargs):
        self.elements.append(element)
    def add_elements(self,elements,*args,**kwargs):
        for element in elements:
            self.elements.append(element)
    def remove_element(self,element,*args,**kwargs):
        self.elements.remove(elment)
    
    
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



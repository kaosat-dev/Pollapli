"""
.. py:module:: node
   :synopsis: generic node class, parent of hardware and software nodes, node manager class etc
"""
import logging, time, datetime, uuid,ast
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.plugin import getPlugins

from pollapli import ipollapli
from pollapli.exceptions import UnknownDriver,NoDriverSet
from pollapli.core.logic.components.updates.update_manager import UpdateManager
from pollapli.core.logic.components.drivers.driver import Driver,DriverManager
from pollapli.core.logic.tools.vector import Vector
from pollapli.core.logic.components.nodes.node_elements import NodeComponent,GenericNodeElement,Tool,Variable,Actor,Sensor
from pollapli.core.logic.tools.wrapper_list import WrapperList
from pollapli.exceptions import UnknownNodeType,NodeNotFound
from pollapli.core.logic.tools.signal_system import SignalHander
from pollapli.core.logic.components.base_component import BaseComponent
#from pollapli.core.logic.components.nodes.hardware.reprap.reprap_capability import ReprapCapability

class NodeStatus(object):
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
    def __init__(self,parent=None, name="base_device",description="base device",*args,**kwargs):
        BaseComponent.__init__(self, parent)
        self._name=name
        self._description=description
        self.status = "inactive"
        self._driver=None 
        
    def __eq__(self, other):
        return self.cid == other.cid and self._name == other._name and self._description == other._description and self.status == other.status
    def __ne__(self, other):
        return not self.__eq__(other)

class Node(DBObject):
    """
    Base class for all nodes: a hardware node is a software component handling either a physical device such as a webcam, reprap , arduino etc
    or some software node (pachube etc)
    """
    BELONGSTO = ['environment']
    EXPOSE=["name","description","id","type","status","driver"]
    
    def __init__(self,type="node",name="base_node",description="base node",options={},*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.nodes.node")
        self.name=name
        self.type=type
        self.description=description
        self.extra_params=options
        
        self.status=NodeStatus()
        self.driver=None 
        
        #################
        self.variables=[]
        self.elements=[]
        self.tools=[]

        
        """this is to ensure no 'asynch clash' occurs when replacing the current driver"""
        self.driverLock=defer.DeferredSemaphore(1)
        #self.rootElement=NodeComponent("root")
        
        self.testElement=None
        self.variable_test()
        #self.link_componentToEndpoint()
        #self.linkedElements=[]
        
        """this is for internal comms handling"""
        self.signal_channel_prefix=str(self.id)
        self._signal_channel="node"+self.signal_channel_prefix+"."+self.name
        self.signalHandler=SignalHander(self._signal_channel)
        self.signalHandler.add_handler(handler=self.variable_get,signal="get")
        self.signalHandler.add_handler(handler=self.variable_set,signal="set")
        
    @defer.inlineCallbacks
    def setup(self):
        self.driver=yield DriverManager.load(parentNode=self)
        
        env= (yield self.environment.get())
        self.signal_channel_prefix="environment_"+str(env.id)+".node_"+str(self.id)
        
        log.msg("Node with id",self.id, "setup successfully",system="Node", logLevel=logging.CRITICAL)
        self.elementsandVarsTest()
        defer.returnValue(None)
        
    def add_command(self,command):  
        log.msg("Node with id",self.id, "recieved command",command,system="Node", logLevel=logging.CRITICAL)
        
        
    def link_componentToEndpoint(self):
        self.tempSensor.set_endPoint(self.driver.endpoints[0])
        self.linkedElements.append(self.tempSensor)
        
    def query_driver(self,sender=None):
        #f sender in self.linkedElements:
        if isinstance(sender,Variable):
           sender.attachedSensors["root"].driverEndpoint.get() 
        
        
    def variable_set(self,sender,varName,*args,**kwargs):
        self.variables[varName].set(*args,**kwargs)
    def variable_get(self,sender,varName,*args,**kwargs):
        self.variables[varName].set(*args,**kwargs)
    
    def variable_test(self):
        temp=Variable(self,"temperature",0,float,"celcius",0,"db")   
        tempSensor=Sensor(type="Sensor",name="temperature sensor",tool="testTool") 
        temp.attach_sensor(tempSensor)
        self.tempSensor=tempSensor
        self.testElement=temp
    
    def elementsandVarsTest(self):
        """test method, for experimental composition of nodes: this creates all the elements for a basic 
        reprap type node"""
        
        """CARTESIAN BOT DEFINITION"""
        """3d Position"""
        pos=Variable(self,"position",Vector(['x','y','z']),"vector","mm",None,"memory",3,True,['x','y','z'])     
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
        extrudate_lng=Variable(self,"filament_extrudate",Vector(['e']),"vector","mm")
        """all the actors controlling the extrusion of this print head"""
        extrudMot=Actor(type="StepperMotor",name="e_motor1",tool="PrintHead",boundVariable=extrudate_lng,variableChannel='e')
        head_heater=Actor(type="Heater",name="extruder1_heater",tool="PrintHead",boundVariable=head_temp)
        """all the sensors giving feedback on the extrusion of this print head"""
        head_tempSensor=Sensor(type="temperature_sensor",name="extruder1_temp_sensor",tool="PrintHead",boundVariable=head_temp)
     
        extrudate_lng.attach_actor(extrudMot,'e')
        head_temp.attach_both([(head_heater,None)],[(head_tempSensor,None)])
        
    def elementsandVarsTest2(self):
        """test method, for experimental composition of nodes: this creates all the elements for a basic 
        reprap type node"""
       
        """CARTESIAN BOT DEFINITION"""
        cartesianBot=NodeComponent("cartesian_bot",self.rootElement)
        """3d Position"""
        pos=Variable(self,"3d_position",Vector(['x','y','z']),"vector","mm",None,"memory",3,True,None,None,['x','y','z'])     
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
        """add all these to the current tool"""
        cartesianBot.add_child(pos)
        cartesianBot.add_children([mot1,mot2,mot3,endStop1,endStop2,endStop3,endStop4,endStop5,endStop6])
        
        """EXTRUDER 1 DEFINITION"""
        """two variables"""
        extruder1=Tool("extruder1")
        head_temp=Variable(self,"head_temp",0,"temperature","celcius")
        extrudate_lng=Variable(self,"filament_extrudate",Vector(['e']),"vector","mm")
        """all the actors controlling the extrusion of this print head"""
        extrudMot=Actor(type="StepperMotor",name="e_motor1",tool="PrintHead",boundVariable=extrudate_lng,variableChannel='e')
        head_heater=Actor(type="Heater",name="extruder1_heater",tool="PrintHead",boundVariable=head_temp)
        """all the sensors giving feedback on the extrusion of this print head"""
        head_tempSensor=Sensor(type="temperature_sensor",name="extruder1_temp_sensor",tool="PrintHead",boundVariable=head_temp)
     
        extrudate_lng.attach_actor(extrudMot,'e')
        head_temp.attach_both([(head_heater,None)],[(head_tempSensor,None)])
        
        """EXTRUDER 2 DEFINITION"""
        """two variables"""
        extruder2=Tool("extruder2")
        head_temp2=Variable(self,"head_temp",0,"temperature","celcius")
        extrudate_lng2=Variable(self,"filament_extrudate",Vector(['e']),"vector","mm")
        """all the actors controlling the extrusion of this print head"""
        extrudMot2=Actor(type="StepperMotor",name="e_motor1",tool="PrintHead",boundVariable=extrudate_lng2,variableChannel='e')
        head_heater2=Actor(type="Heater",name="extruder1_heater",tool="PrintHead",boundVariable=head_temp2)
        """all the sensors giving feedback on the extrusion of this print head"""
        head_tempSensor=Sensor(type="temperature_sensor",name="extruder1_temp_sensor",tool="PrintHead",boundVariable=head_temp2)
     
        extrudate_lng2.attach_actor(extrudMot2,'e')
        head_temp2.attach_both([(head_heater2,None)],[(head_tempSensor2,None)])
        
        """"""""""""""""""""""""""""""""
        cartesianBot.add_child(extruder1)
        cartesianBot.add_child(extruder2)
        
        
    
           
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
            DriverManager._unregister_driver(self.driver) 
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

class NodeManager(object):
    """
    Class for managing nodes: works as a container, a handler
    and a central management point for the list of available nodes
    (for future plugin based system)
    
    
     the signal signature for node manager events is as follows: 
     -for example environment_id.node_created : this is for coherence, signal names use underscores, while hierarchy is represented by dots)
    
    """
    nodeTypes={}
    #nodeTypes["reprap"]=ReprapCapability
    
    def __init__(self,parentEnvironment):
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.nodes.nodeManager")
        self.parentEnvironment=parentEnvironment
        self.nodes={}
        self.lastNodeId=0
        self._signal_channel="node_manager"
        self.signalHandler=SignalHander(self._signal_channel)
        self.signal_channel_prefix="environment_"+str(self.parentEnvironment.id)
     
    @defer.inlineCallbacks    
    def setup(self):
       
        @defer.inlineCallbacks
        def addNode(nodes):
            for node in nodes:
                node.environment.set(self.parentEnvironment)
                self.nodes[node.id]=node
                yield node.setup()
               
        yield Node.all().addCallback(addNode)
        defer.returnValue(None)
    
    
    def _send_signal(self,signal="",data=None):
        prefix=self.signal_channel_prefix+"."
        self.signalHandler.send_message(prefix+signal,self,data)    
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of nodes
    """
    @defer.inlineCallbacks
    def add_node(self,name="node",description="",type=None,*args,**kwargs):
        """
        Add a new node to the list of nodes of the current environment
        Params:
        name: the name of the node
        Desciption: short description of node
        type: the type of the node : very important , as it will be used to instanciate the correct class
        instance
        Connector:the connector to use for this node
        Driver: the driver to use for this node's connector
        """
            
        
        node= yield Node(name=name,description=description,type=type).save()
        node.environment.set(self.parentEnvironment)
        self.nodes[node.id]=node
        log.msg("Added  node ",name," with id set to ",str(node.id), logLevel=logging.CRITICAL)
        self._send_signal("node_created", node)
       
        defer.returnValue(node)
        
    
    def get_nodes(self,filter=None):
        """
        Returns the list of nodes, filtered by  the filter param
        the filter is a dictionary of list, with each key beeing an attribute
        to check, and the values in the list , values of that param to check against
        """
        d=defer.Deferred()
        
        def filter_check(node,filter):
            for key in filter.keys():
                if not getattr(node, key) in filter[key]:
                    return False
            return True
      
        def get(filter,nodesList):
            if filter:
                return WrapperList(data=[node for node in nodesList if filter_check(node,filter)],rootType="nodes")
            else:               
                return WrapperList(data=nodesList,rootType="nodes")
            
        d.addCallback(get,self.nodes.values())
        reactor.callLater(0.5,d.callback,filter)
        return d
    
    def get_node(self,id):
        if not id in self.nodes.keys():
            raise NodeNotFound()
        return self.nodes[id]
    
    
    def update_node(self,id,name=None,description=None,*args,**kwargs):
        """Method for node update"""   
        node=self.nodes[id]
        
        @defer.inlineCallbacks
        def _update():
            node.name=name
            node.description=description
            yield node.save()
            self._send_signal("node_updated", node)
            log.msg("updating node ",id,"newname",name,"newdescrption",description,logLevel=logging.CRITICAL)
        _update()
        
        
        defer.succeed(node)

        #self.nodes[id].update()
    
    
    def delete_node(self,id):
        """
        Remove a node : this needs a whole set of checks, 
        as it would delete an node completely 
        Params:
        id: the id of the node
        """
        @defer.inlineCallbacks
        def _remove(id):
            """
             little "trick" for node deletion : to keep the objects id alive (as it gets removed normally before the event 
             has a chance to be dispatched), the id + data of a node to be deleted gets saved, then the event is dispatched using
              this "fake node"'s data 
            """
           
            nodeName=self.nodes[id].name    
            tmpNode=self.nodes[id]
            tmpId=tmpNode.id
            yield self.nodes[id].delete() 
            del self.nodes[id]
            tmpNode.id=tmpId
            self._send_signal("node_deleted", tmpNode)
            log.msg("Removed node ",nodeName,"with id ",id,logLevel=logging.CRITICAL)
        if not id in self.nodes.keys():
            raise NodeNotFound()
        _remove(id)
        defer.succeed(True)
 
            
    
    def clear_nodes(self):
        """
        Removes & deletes ALL the nodes, should be used with care
        """
        @defer.inlineCallbacks
        def _clear():
            for node in self.nodes.values():
                yield self.delete_node(node.id)  
            self._send_signal("nodes_cleared", self.nodes)   
        _clear();  
             
        defer.succeed(True)     

   
    """
    ####################################################################################
    Helper Methods    
    """
        
    def set_driver(self,nodeId,**kwargs):
        """Method to set a nodes connector's driver 
        Params:
        nodeId: the id of the node
        WARNING: cheap hack for now, always defaults to serial
        connector
        """
        #real clumsy, will be switched with better dynamic driver instanciation
        driver=None
        if kwargs["type"]== "teacup":
            del kwargs["type"]
            driver=TeacupDriver(**kwargs)
        elif kwargs["type"]=="fived":
            del kwargs["type"]
            driver=FiveDDriver(**kwargs)
        if driver:
            self.nodes[nodeId].connector.set_driver(driver)  
            self.logger.critical("Set driver for connector of node %d with params %s",nodeId,str(kwargs))
        else:
            raise Exception("unknown driver ")
        
    def start_node(self,nodeId,**kwargs):
        self.nodes[nodeId].start(**kwargs)
        
    def stop_node(self,nodeId):
        self.nodes[nodeId].stop()
    
  

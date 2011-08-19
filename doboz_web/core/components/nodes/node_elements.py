import logging, time, datetime, uuid,ast
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.internet.defer import DeferredQueue

class NodeElement(object):
    """A sub element of a node : such as actor, sensor etc """
    def __init__(self,type="dummy",name="",tool="",boundVariable=None,variableChannel=None):
        self.name=name
        self.type=type
        self.boundVariable=boundVariable #what variable is it bound to
        self.channel=variableChannel

class Actor(NodeElement):
    def __init__(self,type="BaseActor",name="",tool="",boundVariable=None,variableChannel=None):
        NodeElement.__init__(self,type,name,tool,boundVariable,variableChannel)
        
 
class Sensor(NodeElement):
    def __init__(self,type="Sensor",name="",tool="",boundVariable=None,variableChannel=None):
        NodeElement.__init__(self,type,name,tool,boundVariable,variableChannel)
    def compute_value(self):
        pass
    
class GenericNodeElement(object):
    def __init__(self,name="element",parent=None,isLeaf=False):
        self.name=name
        self.children=[]
        self.parent=parent
        self.isLeaf=isLeaf
    def add_child(self,child):
        if not self.isLeaf:
            child.parent=self
            self.children.append(child)
    def add_children(self,children):
        for child in children:
            self.add_child(child)
    
    def remove_child(self,child):
        if not self.isLeaf:
            child.parent=None
            self.children.remove(child)
        

        
class NodeComponent(object):
    def __init__(self,name="element",parent=None,isLeaf=False):
        self.name=name
        self.children=[]
        self.parent=parent
        self.isLeaf=isLeaf
        
        self.variables={}
        self.elements={}
        
    def add_element(self,element):
        self.elements[element.name]=element
        
    def add_variable(self,variable):
        self.variables[variable.name]=variable
        
    def attach_sensor(self,variableName,sensorName,sensor=None,channel=None,*args,**kwargs):
        if self.variables.has_key(variableName):
            if self.elements.has_key(sensorName):
                self.variables[variableName].attach_sensor(self.elements[variableName],channel,*args,**kwargs)
            elif sensor is not None:
                self.variables[variableName].attach_sensor(sensor,channel,*args,**kwargs)
        else:
            raise Exception("Can't attach sensor, This component has not got that variable")
        
    def attach_actor(self,variableName,actor,channel=None,*args,**kwargs):
        if self.variables.has_key(variableName):
            self.variables[variableName].attach_actor(sensor,channel,*args,**kwargs)
        else:
            raise Exception("Can't attach actor,This component has not got that variable")
    
    def add_child(self,child):
        if not self.isLeaf:
            child.parent=self
            self.children.append(child)
    def add_children(self,children):
        for child in children:
            self.add_child(child)
    
    def remove_child(self,child):
        if not self.isLeaf:
            child.parent=None
            self.children.remove(child)
        
class Tool(NodeComponent):
    def __init__(self,name="",parent=None,isLeaf=False):     
        NodeComponent.__init__(self, name, parent, isLeaf)
        
        
class Reading(DBObject):
    #BELONGSTO = ['variable']
    def __init__(self,data=None,dataTime=None,*args,**kwargs):
        self.data=data
        self.dateTime=dataTime or time.time()
        DBObject.__init__(self,**kwargs)
    
class Command(object):
    def __init__(self,type=None,sender=None,params=None):
        self.type=type#numerical value representing the command type
        self.sender=sender
        self.answered=False
        self.completed=False
        self.params=params
        
class Variable(object):
    def __init__(self,node,name,value,type,unit,defaultValue=None,historyStore=None,historyLength=None,implicitSet=False,channels=[]):
        """
        defaultValue: base value to reset the variable to during a reset operation
        historyPersistance/store : None,memory,database,file
        historyLength: how much old values do we store: None, all, or any numeric value
        """
        #Node.__init__(self,name=name,isLeaf=True)
        self.node=node
        self.name=name
        self.value=value
        self.defaultValue=defaultValue or value
        self.targetValue=None
        self.type=type
        
        self.historyStore=historyStore
        self.history=None
        if historyStore=='memory':
            self.history=[]
            self.historyLength=historyLength
            self.historyIndex=0
        elif historyStore=='db':
            pass
        elif historyStore=='file':
            pass
        
        self.implicitSet=implicitSet
        """This defines the fact, that a "set" operation changes the current value to the target value
         even WITHOUT the need for checking it with a sensor read: we TRUST the remote device to do the 
         work correctly
        """
        self.attachedSensors={}
        self.attachedActors={}
        
        self.commanqueue=DeferredQueue()
        
         
    def attach_sensor(self,sensor,channel=None,*args,**kwargs):
        realChannel=None
        if channel:
            realChannel=channel
        else:
            """if no channel was defined , the sensor needs to be attached to the reserved channel "root",
            which means, the variable itself"""
            realChannel="root"    
            
        self.attachedSensors[realChannel]=sensor
        if sensor.channel is None:
            sensor.channel=realChannel
    
    def attach_sensors(self,sensors,*args,**kwargs):
        """in this case, sensors is a list of tupples in the form : (sensor,channel)"""
        for sensor,channel in sensors:
            self.attach_sensor(sensor, channel)
            
    def attach_actor(self,actor,channel=None,*args,**kwargs):
        realChannel=None
        if channel:
            realChannel=channel
        else:
            """if no channel was defined , the actor needs to be attached to the reserved channel "root",
            which means, the variable itself"""
            realChannel="root"    
        self.attachedActors[realChannel]=actor
        if actor.channel is None:
            actor.channel=realChannel
    
    def attach_actors(self,actors,*args,**kwargs):
        """in this case, actors is a list of tupples in the form : (actor,channel)"""
        for actor,channel in actors:
            self.attach_actor(actor, channel)
    def attach_both(self,sensors,actors):
        self.attach_actors(actors)
        self.attach_sensors(sensors)
        
    def get(self,saveToHistory=False,sender=None):
        command=Command(type="get",sender=sender,params={"save":saveToHistory})
        print("Variable",self.name,"asked for get, by ", sender)
        print("variable",self.name, "has current sensors attached")
        for sens in self.attachedSensors.itervalues():
            print(sens.name," ",sens.type) 
        
        self.commanqueue.put(command)
        
        #hack
       # self.node.driver.connect()
        
        self.node.driver.teststuff(self,None,self._updateConfirmed)
        
 #       self.node.driver.variable_get(self)
#        try:
#            getattr(self.node.driver,"get_"+self.name)(value)
#        except Exception as inst:
#            log.mg("Node's driver does not have the request feature",system="Node",logLevel=logging.CRITICAL)
    
    def set(self,value,relative=False,params=None,sender=None):
        """ setting is dependent on the type of  variable
        This is a delayed operation: set just initiates the chain of events leading to an actual update
        it calls the driver set method + this variables type :ie  for a position: set_name_position
        """
        if relative:
            #all variable types need to support adding
            self.targetValue+=value
        else:
            self.targetValue=value
        try:
            getattr(self.node.driver,"set_"+self.name)(value)
        except Exception as inst:
            log.mg("Node's driver does not have the request feature",system="Node",logLevel=logging.CRITICAL)
   
    def enqueue(self,value):
        pass
    
    def refresh(self):
        """
        This is a delayed operation: set just initiates the chain of events leading to an actual update
        """
        pass
    
    def reset(self,value=None):
        if value is not None:
            self.value=value
        else:
            self.value=self.defaultValue
    
    def _updateConfirmed(self,value=None,*args, **kwargs):
        """to be called after a sucessfull get or set with implicit trust"""
        try:
            value=self.type(value)
        except Exception as inst:
            print("failed to cast update data for variable",inst)
            
        log.msg("Variable update confirmed: new value is ",value,logLevel=logging.CRITICAL)
        
        self.value=value
        if self.historyStore=='memory':
            self.historyIndex+=1
            if self.historyIndex>self.historyLength:
                self.historyIndex=0
            self.history[self.historyIndex]=value
        elif self.historyStore=='db':
            Reading(self.value).save()

"""Variable types:
 temperature, pressure, luminosity, humidity,position/distance
"""    

"""units"""
class Unit(object):
    pass
class mm(Unit):
    pass
class inch(Unit):
    pass

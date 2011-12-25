import logging,ast,time
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from zope.interface import Interface, Attribute,implements
from twisted.plugin import IPlugin,getPlugins
from twisted.internet.interfaces import IProtocol
from twisted.internet.protocol import Protocol

from pollapli.exceptions import UnknownDriver,NoDriverSet,DeviceIdMismatch,DeviceNotConnected
from pollapli import ipollapli
from pollapli.core.logic.tools.signal_system import SignalDispatcher


class EndPoint(object):
    def __init__(self,id,type=None,port=None,infos=[],getter=True,funct=None):
        self.id=id
        self.type=type
        self.port=port
        self.infos=infos
        self.getter=getter
        self.funct=funct
 
    def set(self,value):
        if self.getter:
            raise Exception("this is a getter endpoint")
        self.funct(self.port,value)
    def get(self):
        if not self.getter:
            raise Exception("this is a setter endpoint")
        self.funct(self.port)
    

        
class Driver(object):
    """
    Driver class: higher level handler of device connection that formats outgoing and incoming commands
     according to a spec before they get sent to the lower level connector.
     It actually mimics the way system device drivers work in a way.
     You can think of the events beeing sent out by the driver (dataRecieved etc) as interupts of sorts
     
      ConnectionModes :
        0:setup
        1:normal
        2:setId
        3:forced: to forcefully connect devices which have no deviceId stored 
     
    Thoughts for future evolution
    each driver will have a series of endpoints or slots/hooks, which represent the actual subdevices it handles
    for example for reprap type devices, there is a "position" endpoint (abstract), 3 endpoints for the 
    cartesian bot motors , at least an endpoint for head temperature , one for the heater etc
    or this could be in a hiearchy , reflecting the one off the nodes:
    variable endpoint : position, and sub ones for motors
    """
    
    def __init__(self,deviceType="",connectionType="",hardware_interface_klass=None,logicHandlerKlass=None,protocol=None,options={},*args,**kwargs):    
        self.driverType=self.__class__.__name__.lower()
        self.deviceType=deviceType
        self.connectionType=connectionType
        self.extra_params=options
        self.protocol=protocol
        self.hardware_interface_klass=hardware_interface_klass
        self.logicHandlerKlass=logicHandlerKlass

        self.deviceId=None
        """will be needed to identify a specific device, as the system does not work base on ports"""
     
        self._signal_dispatcher=None 
        self.signalChannelPrefix=""
        self._signal_channel=""
        
        self.isConfigured=False#when the port association has not been set
        self.is_handshake_ok=False
        self.is_identification_ok=False
        self.isConnected=False
        self.isPluggedIn=False
        self.autoConnect=False#if autoconnect is set to true, the device will be connected as soon as a it is plugged in and detected
        
       
        self.connectionErrors=0
        self.maxConnectionErrors=2
        self.connectionTimeout=4
         
        self.connectionMode=1
        self.deferred=defer.Deferred()
        
        """just for future reference : this is not implemented but would be a declarative way to 
        define the different "configuration steps" of this driver"
        *basically a dictonary with keys beeing the connection modes, and values a list of strings
        representing the methods to call
        *would require a "validator"  of sorts (certain elements need to be mandatory : such as the
        validation/setting of device ids
        """
        configSteps={}
        configSteps[0]=["_handle_deviceHandshake","_handle_deviceIdInit"]
        configSteps[1]=["_handle_deviceHandshake","_handle_deviceIdInit","some_other_method"]
        
        #just a test
        self._signal_dispatcher=SignalDispatcher("driver_manager")
        
        """for exposing capabilites"""
        self.endpoints=[]
        
        
    def afterInit(self):
       
        """this is a workaround needed when loading a driver from db"""
        try:
            if not isinstance(self.extra_params,dict):
                self.extra_params=ast.literal_eval(self.extra_params)
        except Exception as inst:
            log.msg("Failed to load driver extra_params from db:",inst,system="Driver",logLevel=logging.CRITICAL)

    
    @defer.inlineCallbacks    
    def setup(self,*args,**kwargs):  
        self.hardwareHandler=self.hardware_interface_klass(self,self.protocol,**self.extra_params)
        self.logicHandler=self.logicHandlerKlass(self,**self.extra_params)  
        
        
        node= (yield self.node.get())
        env= (yield node.environment.get())
        self.signalChannelPrefix="environment_"+str(env.id)+".node_"+str(node.id)

        self._signal_dispatcher.add_handler(handler=self.send_command,signal="addCommand")
        log.msg("Driver of type",self.driverType ,"setup sucessfully",system="Driver",logLevel=logging.INFO)
        
    def bind(self,port,setId=True):
        self.deferred=defer.Deferred()
        log.msg("Attemtping to bind driver",self ,"with deviceId:",self.deviceId,"to port",port,system="Driver",logLevel=logging.DEBUG) 
        self.hardwareHandler.connect(setIdMode=setId,port=port)     
        return self.deferred
    
    def connect(self,mode=None,*args,**kwargs):
        if not self.isConnected:
            if mode is not None:
                self.connectionMode=mode
                log.msg("Connecting in mode:",self.connectionMode,system="Driver",logLevel=logging.CRITICAL) 
                if mode==3:
                    """special case for forced connection"""
                    unboundPorts=DriverManager.bindings.get_unbound_ports()
                    if len(unboundPorts)>0:
                        port=unboundPorts[0]
                        log.msg("Connecting in mode:",self.connectionMode,"to port",port,system="Driver",logLevel=logging.CRITICAL)
                        DriverManager.bindings.bind(self,port)
                        self.pluggedIn(port)
                        self.hardwareHandler.connect(port=port)
                        
                else:
                    self.hardwareHandler.connect()
            else:
                self.hardwareHandler.connect()
                
    def reconnect(self,*args,**kwargs):
        self.hardwareHandler.reconnect(*args,**kwargs)
    def disconnect(self,*args,**kwargs):
        self.hardwareHandler.disconnect(*args,**kwargs)
    
    def pluggedIn(self,port):    
        self.send_signal("plugged_In",port)
        self.isPluggedIn=True
        if self.autoConnect:
            #slight delay, to prevent certain problems when trying to send data to the device too fast
            reactor.callLater(1,self.connect,1)
           
    def pluggedOut(self,port):
        self.isConfigured=False  
        self.is_handshake_ok=False
        self.is_identification_ok=False
        self.isConnected=False
        self.isPluggedIn=False
        self.send_signal("plugged_Out",port)
        #self._signal_dispatcher.send_message("pluggedOut",{"data":port})
    
    def send_signal(self,signal="",data=None):
        prefix=self.signalChannelPrefix+".driver."
        self._signal_dispatcher.send_message(prefix+signal,self,data)
    
    def send_command(self,data,sender=None,callback=None,*args,**kwargs):
       # print("going to send command",data,"from",sender)
        if not self.isConnected:
            raise DeviceNotConnected()
        if self.logicHandler:
            self.logicHandler._handle_request(data=data,sender=sender,callback=callback)
    
    def _send_data(self,data,*arrgs,**kwargs):
        self.hardwareHandler.send_data(data)
         
    def _handle_response(self,data):
        if self.logicHandler:
            self.logicHandler._handle_response(data)
    
    """higher level methods""" 
    def startup(self):
        pass
    def shutdown(self):
        pass
    def init(self):
        pass
    def get_firmware_version(self):
        pass
    def set_debug_level(self,level):
        pass
    
    def teststuff(self,params,*args,**kwargs):
        pass
    
    def variable_set(self,variable,params,sender=None,*args,**kwargs):
        pass
    def variable_get(self,variable,params,sender=None,*args,**kwargs):
        pass
    
    """
    ####################################################################################
                                Experimental
    """ 
    def start_command(self):
        pass
    def close_command(self):
        pass
    
    def get_endpoint(self,filter=None):
        """return a list of endpoints, filtered by parameters"""
        d=defer.Deferred()
        
        def filter_check(endpoint,filter):
            for key in filter.keys():
                if not getattr(endpoint, key) in filter[key]:
                    return False
            return True
      
        def get(filter):
            if filter:
                return [endpoint for endpoint in self.endpoints if filter_check(endpoint,filter)]
            else:               
                pass
            
        d.addCallback(get)
        reactor.callLater(0.5,d.callback,filter)
        return d
        
"""
####################################################################################
Driver logic handlers

some things need to be changed:
*twostep handling for commands needs to be changed to multipart (n complete blocks of
recieved data to consider the response done
*for reprap temperature reading, it begs the question of where this would need to be implemented:
the two part is required for 5d and teacup, but is unlikely to be the same for makerbot: so should this kind of 
difference defined in the protocol ? and in that case should we define specific methods in the protocols like:
 "read sensor" ? (read temperature would be waaay to specific)
"""


class Command(object):
    """Base command class, encapsulate all request and answer commands, also has a 'special' flag for commands that do no participate in normal flow of gcodes : i
    ie for example , regular poling of temperatures for display (the "OK" from those commands MUST not affect the line by line sending/answering of gcodes)
    """
    def __init__(self,special=False,multiParts=1,answerRequired=True,request=None,answer=None,sender=None,callback=None):
        """
        Params:
        special: generally used for "system" commands such as M105 (temperature read) as oposed to general, print/movement commands
        TwoStep: used for commands that return data in addition to "Ok"
        AnswerRequired: for commands that return an answer
        AnswerComplete: flag that specified that an answer is complete
        Request: OPTIONAL: the sent command
        Answer: what answer did we get
        """
        self.special=special
        self.multiParts=multiParts
        self.currentPart=1
        self.answerRequired=answerRequired
        self.requestSent=False
        self.answerComplete=False
        self.request=request
        self.answer=answer
        self.sender=sender
        
        self.callback=callback
        
    def callCallback(self):
        if self.callback is not None:
            self.callback(self.answer)
    def __str__(self):
        #return str(self.request)+" "+str(self.answer)
        return str(self.answer)
        #return "Special:"+ str(self.special)+", TwoStep:"+str(self.twoStep) +", Answer Required:"+str(self.answerRequired)+", Request:"+ str(self.request)+", Answer:"+ str(self.answer) 


class CommandQueueLogic(object):
    """
    Implements a command queue system for drivers
    """
    def __init__(self,driver,bufferSize=8,*args,**kwargs):
        self.driver=driver
        self.bufferSize=bufferSize
        self.answerableCommandBuffer=[]
        self.commandBuffer=[]
        self.commandSlots=bufferSize
        #print("in command queue logic , driver:",driver)
    
        
    def _handle_request(self,data,sender=None,callback=None,*args,**kwargs):
        """
        Manages command requests
        """
      
        cmd=Command(**kwargs)
        
        cmd.request=data
        cmd.sender=sender
        cmd.callback=callback
        
        
        if cmd.answerRequired and len(self.commandBuffer)<self.bufferSize:
            log.msg("adding command",cmd,"from",cmd.sender,"callback",callback,system="Driver",logLevel=logging.DEBUG)
            self.commandBuffer.append(cmd)
            if self.commandSlots>1:
                self.commandSlots-=1
            #initial case
            if len(self.commandBuffer)==1:
                self.send_next_command()
            
             
    def _handle_response(self,data):
        """handles only commands that got an answer, formats them correctly and sets necesarry flags
        params: data the raw response that needs to be treated
        """
        cmd=None        
        #print("here",len(self.commandBuffer)>0)
        #self.driver.send_signal("dataRecieved",data)
        if len(self.commandBuffer)>0:
            try:
                if self.commandBuffer[0].currentPart>1:  
                    self.commandBuffer[0].currentPart-=1
                    #self.commandBuffer[0].twoStep=False
                    cmd=self.commandBuffer[0]
                    cmd.answer+=data
                else:
                    cmd=self.commandBuffer[0]
                    del self.commandBuffer[0]
                    cmd.answerComplete=True
                    cmd.answer=data
                    self.commandSlots+=1#free a commandSlot
                    
                    cmd.callCallback()
                    
                    #print("recieved data ",cmd.answer,"command sender",cmd.sender )
                   # self.driver.send_signal(cmd.sender+".dataRecieved",cmd.answer,True)
                   
                    self.send_next_command()       
            except Exception as inst:
                log.msg("Failure in handling command ",str(inst),system="Driver")
        else:
                cmd=Command(answer=data)
                cmd.answerComplete=True   
                #print("recieved data 2",cmd.answer,"command sender",cmd.sender )    
        return cmd
     
    def send_next_command(self):
        """Returns next avalailable command in command queue """
        cmd=None
       # print("in next command: buffer",len(self.commandBuffer),"slots",self.commandSlots)  
        if not self.driver.is_handshake_ok:
            pass
            #raise Exception("Machine connection not established correctly")
        elif self.driver.is_handshake_ok and len(self.commandBuffer)>0 and self.commandSlots>0:        
            tmp=self.commandBuffer[0]
            if not tmp.requestSent:            
                cmd=self.commandBuffer[0].request
                tmp.requestSent=True
                self.driver._send_data(cmd)
                #self.logger.debug("Driver giving next command %s",str(cmd))
        else:
            if len(self.commandBuffer)>0:
                print("pouet")
                #self.logger.critical("Buffer Size Exceed Machine capacity: %s elements in command buffer, CommandSlots %s, CommandBuffer %s",str(len(self.commandBuffer)),str(self.commandSlots),[str(el) for el in self.commandBuffer])
        return cmd 
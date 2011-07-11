import logging
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from zope.interface import Interface, Attribute,implements
from twisted.plugin import IPlugin,getPlugins

from louie import dispatcher,error,Any,All
import louie

from doboz_web.exceptions import UnknownDriver,NoDriverSet,DeviceIdMismatch
from doboz_web import idoboz_web
from doboz_web.core.signal_system import SignalHander
from doboz_web.core.components.addons.addon_manager import AddOnManager
from doboz_web.core.components.drivers.serial.serial_hardware_handler import SerialHardwareHandler
    
class Driver(DBObject):
    """
    Driver class: higher level handler of device connection that formats outgoing and incoming commands
     according to a spec before they get sent to the lower level connector.
     It actually mimics the way system device drivers work in a way.
     You can think of the events beeing sent out by the driver (dataRecieved etc) as interupts of sorts
    """
    BELONGSTO = ['node']
    def __init__(self,driverType=None,hardwareHandler=None,hardwareHandlerType=None,logicHandler=None,logicHandlerType=None,options={},*args,**kwargs):
        self.logger = logging.getLogger("dobozweb.core.components.driver")      
        self.logger.setLevel(logging.INFO)
        DBObject.__init__(self,**kwargs)
        self.options=options
        
        self.deviceId=None
        """will be needed to identify a specific device, as the system does not work base on ports"""
        self.driverType=driverType
        self.hardwareHandler=hardwareHandler
        self.logicHandler=logicHandler
        self.hardwareHandlerType=hardwareHandlerType
        self.logicHandlerType=logicHandlerType
        self.signalHandler=SignalHander("Driver")
        
        self.initalSetup=True
        self.isConfigured=False#when the port association has not been set
        self.isDeviceHandshakeOk=False
        self.isDeviceIdOk=False
        
    def _toDict(self):
        return {"driver":{"hardwareHandler":self.hardwareHandlerType,"logicHandler":self.logicHandlerType,"options":self.options,"link":{"rel":"node"}}}
    
    def set_handlers(self,hardwareHandler=None,logicHandler=None):
        if hardwareHandler:
            self.hardwareHandler=hardwareHandler
            self.hardwareHandlerType=hardwareHandler.__class__.__name__
        if logicHandler:
            self.logicHandler=logicHandler
            self.logicHandlerType=logicHandler.__class__.__name__
            
    def setup(self):
        log.msg("Attemtping to setup driver",system="Driver")
        
        self.hardwareHandler.connect(setupMode=True)#Special(setupMode=True,currentPortAttempted)
        
    def _setupSucceeded(self,params=None):
        DriverManager._deviceMatchFound(self)
        
    def _setupFailed(self,params=None):
        d=defer.Deferred()
        return d
        
    
    def connect(self,*args,**kwargs):
        self.hardwareHandler.connect()
    def disconnect(self,*args,**kwargs):
        self.hardwareHandler.disconnect()
    
    def send_command(self,data):
        if self.logicHandler:
            self.logicHandler._handle_request(data)
        else:
            self.hardwareHandler.send_data(data)
            
    def _handle_response(self,data):
        if self.logicHandler:
            self.logicHandler._handle_response(data)
        else:
            self.signalHandler.send_message(self,"test.driver.dataRecieved",{"data":data})
            self.send_command("a")



        
class DriverManager(object):
    """
    This class acts as factory and manager
    The driver factory assembles a Driver object (the one whose instances are actually stored in db)
    from two objects : 
        * a driver_high object for all higher level functions (ie the ones of the current driver class, mostly)
        * a driver_low object for all lower level functions (ie the ones of the current connector class)
        this lower level driver is for example the actual serial_connector class as we have it currently
    This solve a whole lot of problems at once, since the subobjects will be essentially viewed as one, thanks
    to the getattr method
    """
    """
    For driver class: should there be a notion of "requester" for sending data, so that answers can be dispatche
    to the actual entity that sent the command ? for example : during a reprap 3d print, querying for sensor 
    data is actually completely seperate and should not be part of the print task, therefor, since all requests
    are sent to the same device, there needs to be a way to differenciate between the two when sending back messages
    """
    
    """
    For plug & play managment
    the whole "check and or set device id" procedure should not take place during the normal 
    connect etc process but in a completely seperate set of phases (somethink like a "setup" 
    and used to check for correct device on port /device id 
    
    the hardware manager's connect method needs to be modified:
    - if the device was successfully associated with a port in the p&p detection phase, use that port info
    - if the device was not identified , has no id, etc , then use the current "use the first available port" method
    
    perhaps we should use a method similar to the way drivers are installed on windows:
    - ask for removal of cable if already connected
    - ask for re plug of cable
    - do a diff on the previous/new list of com/tty devices
    - do id generation/association
    """    
    
    
    loaded_drivers=[]
    
    port_to_driver={}
    driver_to_port={}
    
    available_devices={}
    available_devices["serial"]=[]
    toConfigure_drivers=[]
    hardware_handlers={}
    hardware_handlers["serial"]=SerialHardwareHandler
    
    pending_ports=[]
    pending_drivers=[]
    
    
    def __init__(self):
        
        log.msg("starting driver factory", logLevel=logging.CRITICAL)
        """example
        port_to_driver['com4']=a driver instance
        port_to_deviceId['com4]
        or 
        """
    @classmethod 
    @defer.inlineCallbacks
    def setup(self,*args,**kwargs):
        log.msg("Driver Manager setup succesfully",system="Driver Manager")
        yield DriverManager.update_deviceList()
        #reactor.callLater(3,DriverManager.update_deviceList)
        
        
    @classmethod 
    @defer.inlineCallbacks
    def create(cls,driverType=None,driverParams={},*args,**kwargs):   
        driverType=driverType
        plugins= (yield AddOnManager.get_plugins(idoboz_web.IDriver))
        driver=None
        print("found plugins: ",plugins)
        for driverKlass in plugins:
            if driverType==driverKlass.__name__.lower():
                driver=yield Driver(driverType=driverType,options=driverParams).save()
                hardwareHandler=driverKlass.components["hardwareHandler"](driver,**driverParams)
                logicHandler=driverKlass.components["logicHandler"](driver,**driverParams)
                driver.set_handlers(hardwareHandler,logicHandler)
                driver.save()  
                DriverManager.loaded_drivers.append(driver)
                break
        if not driver:
            #defer.returnValue(None)
            raise UnknownDriver()
        
        defer.returnValue(driver)
    
    @classmethod    
    @defer.inlineCallbacks
    def load(cls,driver):
        driverType=driver.driverType
        params=driver.options
        plugins= (yield AddOnManager.get_plugins(idoboz_web.IDriver))
        for driverKlass in plugins:
            if driverType==driverKlass.__name__.lower():
                hardwareHandler=driverKlass.components["hardwareHandler"](driver,**params)
                logicHandler=driverKlass.components["logicHandler"](driver,**params)
                driver.set_handlers(hardwareHandler,logicHandler)
                DriverManager.loaded_drivers.append(driver)
                break
        defer.returnValue(driver)

    @classmethod
    def unregister_driver(cls,driver):
        if driver in DriverManager.loaded_drivers:
            loaded_drivers.remove(driver)
            del DriverManager.driver_to_port[driver]
            
    
    @classmethod
    @defer.inlineCallbacks
    def _deviceMatchFound(self,driver):
        log.msg("Node",(yield driver.node.get()).name,"plugged in to port",driver.hardwareHandler.port,system="Driver")
        DriverManager.port_to_driver[driver.hardwareHandler.port]=driver
        DriverManager.driver_to_port[driver]=driver.hardwareHandler.port
        #print("blaah",DriverManager.driver_to_port)
        defer.returnValue(None)
        
  
    
    @classmethod
    def _next_driverToSetup(self):
        pass      
    
    
    class PortBinderHelper(object):
        def __init__(self,ports,drivers):
            self.ports=ports
            self.drivers=drivers
            self.d=defer.Deferred()
            return  self.d
            
        def _next_driver(self):
            pass 
        
        def driverYielder(self,drivers):
            driverIndex=0
            while driverIndex < len(drivers):
                yield drivers[driverIndex]
                driverIndex += 1
                
        def portYielder(self,ports):
            portIndex=0
            while driverIndex < len(drivers):
                yield drivers[driverIndex]
                driverIndex += 1
        
    @classmethod
    def setup_drivers(cls,ports,drivers):
        pass
    
    @classmethod
    def _driver_setup_failed(cls,*args,**kwargs):
        print("driver setup failed",args,kwargs)
        
    @classmethod
    @defer.inlineCallbacks  
    def update_deviceList(cls):
        """
        Needs to be done with each hardware type with pnp support
        """
        #log.msg("Checking for device changes",system="Driver")
        oldPorts=DriverManager.available_devices["serial"]       
        newPorts=[]
        for handler in DriverManager.hardware_handlers.itervalues():
            newPorts.extend((yield handler.list_availablePorts()))
        
        
        def checkForPortChanges(oldL,newL):
            addedPorts=[]
            """
            we don't do a preliminary "if len(oldL) != len(newL):" since even with the same amount of 
            detected devices, the actual devices in the list could be different
            """
            s1=set(oldL)
            s2=set(newL)
            addedPorts=s2-s1
            removePorts=s1-s2
            return (addedPorts,removePorts)
                
        portChanges=checkForPortChanges(oldPorts,newPorts)
        if len(portChanges[0])>0 or len(portChanges[1])>0:
            DriverManager.available_devices["serial"]=list(portChanges[0])
            if len(portChanges[1])>0:
                #log.msg("These ports were removed",portChanges[1])
                s1=set(DriverManager.port_to_driver.iterkeys())
                disconnectedPorts=s1.intersection(portChanges[1])
                for port in list(disconnectedPorts):
                    driver=DriverManager.port_to_driver[port]
                    log.msg("Node",(yield driver.node.get()).name,"plugged out of port",driver.hardwareHandler.port,system="Driver")
                    del DriverManager.driver_to_port[driver]
                    del DriverManager.port_to_driver[port]
                    driver.isConfigured=False
                    driver.hardwareHandler.protocol.deviceInitOk=False

            if len(portChanges[0])>0:
                log.msg("These ports were added",portChanges[0])
                
                #yield PortBinderHelper(list(portChanges[0]),DriverManager.loaded_drivers)
                #DriverManager._next_driverToSetup()
                
                for driver in DriverManager.loaded_drivers:
                    if not driver.isConfigured:
                        driver.setup()
                        
        reactor.callLater(3,DriverManager.update_deviceList)
        
        
"""
####################################################################################
Driver logic handlers
"""

class Command(object):
    """Base command class, encapsulate all request and answer commands, also has a 'special' flag for commands that do no participate in normal flow of gcodes : i
    ie for example , regular poling of temperatures for display (the "OK" from those commands MUST not affect the line by line sending/answering of gcodes)
    """
    def __init__(self,special=False,twoStep=False,answerRequired=False,request=None,answer=None):
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
        self.twoStep=twoStep
        self.answerRequired=answerRequired
        self.requestSent=False
        self.answerComplete=False
        self.request=request
        self.answer=answer
        
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
        
    def _handle_request(self,data,*args,**kwargs):
        """
        Manages command requests
        """
        cmd=Command(**kwargs)
        cmd.request=data
        
        if cmd.answerRequired and len(self.commandBuffer)<self.bufferSize:
            self.commandBuffer.append(cmd)
            if self.commandSlots>1:
                self.commandSlots-=1
             
    def _handle_response(self,data):
        """handles only commands that got an answer, formats them correctly and sets necesarry flags
        params: data the raw response that needs to be treated
        """
        cmd=None        
        if True:      
            if len(self.commandBuffer)>0:
                try:
                    if self.commandBuffer[0].twoStep:  
                        self.commandBuffer[0].twoStep=False
                        cmd=self.commandBuffer[0]
                    else:
                        cmd=self.commandBuffer[0]
                        del self.commandBuffer[0]
                        cmd.answerComplete=True
                        cmd.answer=data
                        self.commandSlots+=1#free a commandSlot
                       
                        self.send_next_command()
                        
                except Exception as inst:
                    log.msg("Failure in handling command ",str(inst),system="Driver")
                    
            else:
                cmd=Command(answer=data)
                cmd.answerComplete=True
                

        self.driver.signalHandler.send_message(self.driver,"driver.dataRecieved",{"data":cmd.answer})
         ###one command was completed, send next  
        self._handle_request(data="a",answerRequired=True) 
        self.send_next_command()
        return cmd
     
    def send_next_command(self):
        """Returns next avalailable command in command queue """
        cmd=None
       # print("in next command: buffer",len(self.commandBuffer),"slots",self.commandSlots)
        self.deviceHandshakeOk=True   
        if not self.deviceHandshakeOk:
            raise Exception("Machine connection not established correctly")
        elif self.deviceHandshakeOk and len(self.commandBuffer)>0 and self.commandSlots>0:  
            
            tmp=self.commandBuffer[0]
            if not tmp.requestSent:            
                cmd=self.commandBuffer[0].request
                tmp.requestSent=True
                self.driver.hardwareHandler.send_data(cmd)
                #log.msg("")
                #self.logger.debug("Driver giving next command %s",str(cmd))
        else:
            if len(self.commandBuffer)>0:
                print("pouet")
                #self.logger.critical("Buffer Size Exceed Machine capacity: %s elements in command buffer, CommandSlots %s, CommandBuffer %s",str(len(self.commandBuffer)),str(self.commandSlots),[str(el) for el in self.commandBuffer])
        return cmd 
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

from doboz_web.exceptions import UnknownDriver,NoDriverSet
from doboz_web import idoboz_web
from doboz_web.core.signal_system import SignalHander
#from doboz_web.core.components.drivers.serial.serial_driver_low import SerialHardwareHandler,BaseSerialProtocol
from doboz_web.core.components.addons.addon_manager import AddOnManager

    
class Driver(DBObject):
    """
    Driver class: higher level handler of device connection that formats outgoing and incoming commands
     according to a spec before they get sent to the lower level connector.
     It actually mimics the way system device drivers work in a way.
     You can think of the events beeing sent out by the driver (dataRecieved etc) as interupts of sorts
    """
    BELONGSTO = ['node']
    def __init__(self,hardwareHandler=None,logicHandler=None,options={},*args,**kwargs):
        self.logger = logging.getLogger("dobozweb.core.components.driver")      
        self.logger.setLevel(logging.INFO)
        print("driver kwargs",kwargs)
        DBObject.__init__(self,**kwargs)
        self.options=options
        
        #self.errors=0
       # self.maxErrors=5
        
        self.hardwareHandler=hardwareHandler
        self.logicHandler=logicHandler
        self.hardwareHandlerType=None
        self.logicHandlerType=None
        self.signalHandler=SignalHander("Driver")
    
    def set_handlers(self,hardwareHandler=None,logicHandler=None):
        if hardwareHandler:
            self.hardwareHandler=hardwareHandler
            self.hardwareHandlerType=hardwareHandler.__class__.__name__
        if logicHandler:
            self.logicHandler=logicHandler
            self.logicHandlerType=logicHandler.__class__.__name__
            
    
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
#        def __getattr__(self,attrname):
#            try:
#                if hasattr(self.lowDriver,attrname):
#                    return getattr(self.lowDriver,attrname)
#                elif hasattr(self.highDriver,attrname):
#                    return getattr(self.highDriver,attrname)
#            except:
#                pass
        
class DriverFactory(object):
    """
    The driver factory assembles a Driver object (the one whose instances are actually stored in db)
    from two objects : 
        * a driver_high object for all higher level functions (ie the ones of the current driver class, mostly)
        * a driver_low object for all lower level functions (ie the ones of the current connector class)
        this lower level driver is for example the actual serial_connector class as we have it currently
    This solve a whole lot of problems at once, since the subobjects will be essentially viewed as one, thanks
    to the getattr method
    """
    
    def __init__(self):
        
        log.msg("starting driver factory", logLevel=logging.CRITICAL)
    @defer.inlineCallbacks
    def create(self,params={}):        
        
        driverType=params.get("driverType", None)
        plugins= (yield AddOnManager.get_plugins(idoboz_web.IDriver))
        
        driver=Driver(options=params)
        for driverKlass in plugins:#(yield AddOnManager.get_plugins(idoboz_web.IDriver)):
            #log.msg("found driver",driverKlass, logLevel=logging.CRITICAL)
            
            if driverType==driverKlass.__name__.lower():
                #print("found driver",driverType)
                #print("components",getattr(driverKlass,"components"))
                hardwareHandler=driverKlass.components["hardwareHandler"](driver,**params)
                logicHandler=driverKlass.components["logicHandler"](driver,**params)
                driver.set_handlers(hardwareHandler,logicHandler)
                
                #
                

                driver.save()  
                driver.connect()
                #log.msg("Set connector of node",self.id, "to serial plus, and driver of type", driverType," and params",str(driverParams), logLevel=logging.CRITICAL)
                break
        if not driver:
            raise UnknownDriver()
        
        defer.returnValue(driver)


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
                

        self.driver.signalHandler.send_message(self.driver,"test.driver.dataRecieved",{"data":cmd.answer})
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
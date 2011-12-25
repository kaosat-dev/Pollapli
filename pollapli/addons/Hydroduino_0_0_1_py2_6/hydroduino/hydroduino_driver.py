from zope.interface import implements
from twisted.plugin import IPlugin
from pollapli import ipollapli 
from zope.interface import classProvides
from twisted.python import log,failure
from twisted.internet import reactor, defer
import uuid,logging
from pollapli.exceptions import DeviceHandshakeMismatch,DeviceIdMismatch
from pollapli.core.logic.components.drivers.driver import Driver,CommandQueueLogic,EndPoint
from pollapli.core.logic.components.drivers.protocols import BaseTextSerialProtocol
from pollapli.core.logic.components.drivers.serial_hardware_handler import SerialHardwareHandler

class HydroduinoProtocol(BaseTextSerialProtocol):
    """
    Class defining the protocol used by this driver: in this case, the hydroduino protocol
    """
    messages = {
        # Input Messages
        'debug_confirm':      0,     
        'set_id':   99,     # device id set confirm
        'get_id':   2,     # device id get 
        'pin_low':   3,     # pin low confirm 
        'pin_high':   4,     # pin high confirm 
        }     
    def __init__(self,driver=None,is_buffering=True,seperator='\n',*args,**kwargs):
        BaseTextSerialProtocol.__init__(self,driver,is_buffering,seperator)
           
    def _set_hardware_id(self,id=None):
        self.send_data('99'+ " "+ str(self.driver.deviceId))
        
    def _query_hardware_id(self):
        """method for retrieval of device info (for id and more) """
        self.send_data('2')
        
    def _format_data_in(self,data,*args,**kwargs):
        """
        Formats an incomming data block according to some specs/protocol 
        data: the incomming data from the device
        """

        data=data.replace('\n','')
        data=data.replace('\r','')
    
        if not data==self.ref_handshake:
            message=data.split(" ")[0]
            print("full",data,"message",message)
            data="".join(data.split(" ")[1:])
        
        return data
    
    def got_device_id(self):
        pass

class HydroduinoDriver(Driver):
    """Class defining the components of the driver for a basic arduino,using attached firmware """
    classProvides(IPlugin, ipollapli.IDriver) 
    TABLENAME="drivers"   
    def __init__(self,deviceType="Arduino",connectionType="serial",options={},*args,**kwargs):
        """
        very important : the  two args should ALWAYS be the CLASSES of the hardware handler and logic handler,
        and not instances of those classes
        """
        Driver.__init__(self,deviceType,connectionType,SerialHardwareHandler,CommandQueueLogic,HydroduinoProtocol,options,*args,**kwargs)
        self.endpoints.append(EndPoint(0,"device",0,None,True,self.analogRead))
        self.endpoints.append(EndPoint(1,"device",0,None,False,self.analogWrite))
       
        
    def teststuff(self,sender,params=None,callback=None,*args,**kwargs):
        #print("arduino driver teststuff:sender",sender,"params",params,"callback",callback)
        self.send_command(data='5 0',sender=sender,callback=callback)  
    
    
    def start_command(self):
        pass
    def close_command(self):
        pass

    def hello_world(self):
        self.send_command(0)
        
    def set_mode(self,pin,mode):
        self.send_command(" ".join([7, pin, mode]))
        
    def set_Low(self, pin):
        self.send_command(" ".join([3, pin]))

    def set_High(self, pin):
        self.send_command(" ".join([4, pin]))

    def get_State(self, pin):
        self.send_command('g'+str(pin))

    def analogWrite(self, pin, value):
        self.send_command(" ".join([3, pin, value]))
        
    def analogRead(self, pin):
        self.send_command(" ".join([5, pin]))
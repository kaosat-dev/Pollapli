from zope.interface import implements
from twisted.plugin import IPlugin
from doboz_web import idoboz_web 
from zope.interface import classProvides
from twisted.python import log,failure
from twisted.internet import reactor, defer
import uuid
import logging
from doboz_web.exceptions import DeviceHandshakeMismatch,DeviceIdMismatch
from doboz_web.core.components.drivers.driver import Driver,DriverManager,CommandQueueLogic
from doboz_web.core.components.drivers.protocols import BaseTextSerialProtocol
from doboz_web.core.components.drivers.serial.serial_hardware_handler import SerialHardwareHandler



class ArduinoExampleProtocol(BaseTextSerialProtocol):
    """
    Class defining the protocol used by this driver: in this case, the reprap 5D protocol (similar to teacup, but with checksum)
    """
    # these aren't used for anything yet, just sitting here for reference
    messages = {
        # Input Messages
        'debug_confirm':      0,     
        'set_id':   99,     # device id set confirm
        'get_id':   2,     # device id get 
        'pin_low':   3,     # pin low confirm 
        'pin_high':   4,     # pin high confirm 
        }       
    
    def __init__(self,driver=None,isBuffering=True,seperator='\n',*args,**kwargs):
        BaseTextSerialProtocol.__init__(self,driver,isBuffering,seperator)
           
    def _set_deviceId(self,id=None):
         self.send_data('99'+ " "+ str(self.driver.deviceId))
        
    def _query_deviceInfo(self):
        """method for retrieval of device info (for id and more) """
        self.send_data("2")    
        
    def _format_data_in(self,data,*args,**kwargs):
        """
        Formats an incomming data block according to some specs/protocol 
        data: the incomming data from the device
        """
        message=data.split(" ")[1:]
        if " " in data:
            data="".join(data.split(" ")[1:])

        data=data.replace("ok",'')
        data=data.replace(" ",'')
        data=data.replace('\n','')
        data=data.replace('\r','')
        return data  
    
        
class ArduinoExampleHardwareHandler(SerialHardwareHandler):
    classProvides(IPlugin, idoboz_web.IDriverHardwareHandler)
    def __init__(self,*args,**kwargs):
        SerialHardwareHandler.__init__(self,protocol=ArduinoExampleProtocol(*args,**kwargs),*args,**kwargs)


class ArduinoExampleDriver(Driver):
    """Class defining the components of the driver for a basic arduino,using attached firmware """
    classProvides(IPlugin, idoboz_web.IDriver) 
    TABLENAME="drivers"   
    def __init__(self,driverType="ArduinoExample",deviceType="Arduino",deviceId="",connectionType="serial",options={},*args,**kwargs):
        """
        very important : the first two args should ALWAYS be the CLASSES of the hardware handler and logic handler,
        and not instances of those classes
        """
        Driver.__init__(self,ArduinoExampleHardwareHandler,CommandQueueLogic,driverType,deviceType,deviceId,connectionType,options,*args,**kwargs)
        
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

    
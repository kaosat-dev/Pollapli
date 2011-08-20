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
from doboz_web.core.components.drivers.serial.serial_hardware_handler import BaseSerialProtocol,SerialHardwareHandler


class ArduinoExampleProtocol(BaseSerialProtocol):
    """
    Class defining the protocol used by this driver: in this case, the reprap 5D protocol (similar to teacup, but with checksum)
    """
    def __init__(self,driver=None,isBuffering=True,seperator='\n',*args,**kwargs):
        BaseSerialProtocol.__init__(self,driver,isBuffering,seperator)
        
    def _handle_deviceHandshake(self,data):
        """
        handles machine (hardware node etc) initialization
        data: the incoming data from the machine
        """
        log.msg("Attempting to validate device handshake",system="Driver",logLevel=logging.INFO)
        if "start" in data:
            self.driver.isDeviceHandshakeOk=True
            log.msg("Device handshake validated",system="Driver",logLevel=logging.INFO)
            self._query_deviceInfo()
        else:
            log.msg("Device hanshake mismatch",system="Driver",logLevel=logging.INFO)
            self.driver.reconnect()
        
    
    def _handle_deviceIdInit(self,data):
        """
        handles machine (hardware node etc) initialization
        data: the incoming data from the machine
        """
        log.msg("Attempting to configure device Id",system="Driver",logLevel=logging.INFO)
        def validate_uuid(data):
            if len(str(data))==36:
                fields=str(data).split('-')
                if len(fields[0])==8 and len(fields[1])==4 and len(fields[2])==4 and len(fields[3])==4 and len(fields[4])==12:
                    return True
            return False
        if self.driver.connectionErrors>=self.driver.maxConnectionErrors:
            self.driver.disconnect()
            self.driver.d.errback(None)  
        sucess=False
        if self.driver.connectionMode==2 or self.driver.connectionMode==0:
            """if we are trying to set the device id"""    
            if validate_uuid(data):
                """if the remote device has already go a valid id, and we don't, update accordingly"""
                if not self.driver.deviceId :
                    self.driver.deviceId=data
                    sucess=True
                elif self.driver.deviceId!= data:
                    self._set_deviceId()
                    #self._query_deviceInfo()
                    """if we end up here again, it means something went wrong with 
                    the remote setting of id, so add to errors"""
                    self.driver.connectionErrors+=1
                    
                elif self.driver.deviceId==data:
                    sucess=True     
            else:
                if not self.driver.deviceId:
                    self.driver.deviceId=str(uuid.uuid4())
                self.driver.connectionErrors+=1
                self._set_deviceId()
                
        else:
            """ some other connection mode , that still requires id check"""
            if not validate_uuid(data) or self.driver.deviceId!= data:
                log.msg("Device id not set or not valid",system="Driver")
                self.driver.connectionErrors+=1
                self.driver.reconnect()
            else:
                sucess=True
                
        if sucess is True: 
            self.driver.isDeviceIdOk=True
            log.msg("DeviceId match ok: id is ",data,system="Driver")
            self.driver.isConfigured=True 
            self.driver.disconnect()
            self.driver.d.callback(None)      
        
    def _set_deviceId(self,id=None):
         self.send_data('99'+ " "+ str(self.driver.deviceId))
        
    def _query_deviceInfo(self):
        """method for retrieval of device info (for id and more) """
        self.send_data("2")
        
    def _format_data_out(self,data,*args,**kwargs):
        """
        Formats an outgoing data block according to some specs/protocol 
        data: the outgoing data TO the device
        """
        return data+'\n'
    
    def _format_data_in(self,data,*args,**kwargs):
        """
        Formats an incomming data block according to some specs/protocol 
        data: the incomming data FROM the device
        """
        data=data.replace('\n','')
        data=data.replace('\r','')
        return data
    
    def connectionLost(self,reason="connectionLost"):
        self.driver.isDeviceHandshakeOk=False
        BaseSerialProtocol.connectionLost(self,reason)
        
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

    
from zope.interface import implements
from twisted.plugin import IPlugin
from doboz_web import idoboz_web 
from zope.interface import classProvides
from twisted.python import log,failure
from twisted.internet import reactor, defer
import uuid
from doboz_web.exceptions import DeviceHandshakeMismatch,DeviceIdMismatch
from doboz_web.core.components.drivers.driver import Driver,DriverManager,CommandQueueLogic
from doboz_web.core.components.drivers.serial.serial_hardware_handler import BaseSerialProtocol,SerialHardwareHandler


class ArduinoExampleProtocol(BaseSerialProtocol):
    """
    Class defining the protocol used by this driver: in this case, the reprap 5D protocol (similar to teacup, but with checksum)
    """
    def __init__(self,driver=None,isBuffering=True,seperator='\n',*args,**kwargs):
       # print("in  fived Protocol", seperator,driver)
        BaseSerialProtocol.__init__(self,driver,isBuffering,seperator)
        self.deviceHandshakeOk=False
        self.deviceInitOk=False
        
    def _handle_deviceHandshake(self,data):
        """
        handles machine (hardware node etc) initialization
        datab: the incoming data from the machine
        """
        if "start" in data:
            self.deviceHandshakeOk=True
            log.msg("Device handshake validated",system="Driver")
            self._query_deviceInfo()
        else:
            log.msg("Device hanshake mismatch",system="Driver")
            self.driver.reconnect()
            #raise DeviceHandshakeMismatch()
    
    @defer.inlineCallbacks
    def _handle_deviceInit(self,data):
        """
        handles machine (hardware node etc) initialization
        datab: the incoming data from the machine
        """
        def validate_uuid(data):
            if len(str(data))==36:
                fields=str(data).split('-')
                if len(fields[0])==8 and len(fields[1])==4 and len(fields[2])==4 and len(fields[3])==4 and len(fields[4])==12:
                    return True
            return False
        
        if not validate_uuid(data):
            log.msg("Device id not set or not valid",system="Driver")
            self.driver.connectionErrors+=1
            self.driver.reconnect()
#            if not self.driver.deviceId :
#                self.driver.deviceId=str(uuid.uuid4())
#                yield self.driver.save()
#                self._set_deviceId()
#                self._query_deviceInfo()
#                
#            elif self.driver.deviceId!= data: 
#                self.driver.reconnect()
                #raise Exception("Connected to wrong device")
            
        else:
            self.driver.deviceId=data
            yield self.driver.save()
            self.deviceInitOk=True
            log.msg("Device id is ",data,system="Driver")
            self.driver.isConfigured=True 
            self.driver.disconnect()
            self.driver.d.callback(self.driver)    
            #self.driver._setupSucceeded()

        defer.returnValue(None)
        
    def _set_deviceId(self,id=None):
        self.send_data("s"+ self.driver.deviceId)
        
        
    def _query_deviceInfo(self):
        """method for retrieval of device info (for id and more) """
        self.send_data("i")
        
    def _format_data_out(self,data,*args,**kwargs):
        """
        Cleanup gcode : remove comments and whitespaces
        """
        return data+'\n'
    
    def _format_data_in(self,data,*args,**kwargs):
        """
        Formats an incomming data block according to some specs/protocol 
        data: the incomming data from the device
        """
        data=data.replace('\n','')
        data=data.replace('\r','')
        return data
    
    def connectionLost(self,reason="connectionLost"):
        self.deviceHandshakeOk=False
        BaseSerialProtocol.connectionLost(self,reason)
        
class ArduinoExampleHardwareHandler(SerialHardwareHandler):
    classProvides(IPlugin, idoboz_web.IDriverHardwareHandler)
    def __init__(self,*args,**kwargs):
        SerialHardwareHandler.__init__(self,protocol=ArduinoExampleProtocol(*args,**kwargs),*args,**kwargs)




class ArduinoExampleDriver(object):
    """Class defining the components of the driver for a basic arduino,using attached firmware """
    classProvides(IPlugin, idoboz_web.IDriver)
    components={"logicHandler":CommandQueueLogic,"hardwareHandler":ArduinoExampleHardwareHandler}
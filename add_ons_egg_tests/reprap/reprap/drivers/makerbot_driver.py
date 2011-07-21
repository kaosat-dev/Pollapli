from zope.interface import implements
from twisted.plugin import IPlugin
from doboz_web import idoboz_web 
from zope.interface import classProvides
from twisted.python import log,failure
from doboz_web.core.components.drivers.driver import Driver,CommandQueueLogic
from doboz_web.core.components.drivers.serial.serial_hardware_handler import BaseSerialProtocol,SerialHardwareHandler

class MakerbotProtocol(BaseSerialProtocol):
    """
    Class defining the protocol used by this driver: in this case, the reprap teacup protocol 
    which is the most straighforward of reprap protocols (no checksum etc)
    """
    def __init__(self,driver=None,isBuffering=True,seperator='\n',*args,**kwargs):
        BaseSerialProtocol.__init__(self,driver,isBuffering,seperator)
        
        
    def _handle_deviceHandshake(self,data):
        """
        handles machine (hardware node etc) initialization
        datab: the incoming data from the machine
        """
        self.isProcessing=True
        if "start" in data:
            self.driver.isDeviceHandshakeOk=True
            log.msg("Device handshake validated",system="Driver")
            self.isProcessing=False
            self._query_deviceInfo()
        else:
            log.msg("Device hanshake mismatch",system="Driver")
            self.isProcessing=False
            self.driver.reconnect()
         
    def _handle_deviceInit(self,data):
        """
        handles machine (hardware node etc) initialization
        data: the incoming data from the machine
        """
        self.isProcessing=True
        def validate_uuid(data):
            if len(str(data))==36:
                fields=str(data).split('-')
                if len(fields[0])==8 and len(fields[1])==4 and len(fields[2])==4 and len(fields[3])==4 and len(fields[4])==12:
                    return True
            return False
        
        sucess=False
        if self.driver.connectionMode==2 or self.driver.connectionMode==0:
            """if we are trying to set the device id"""    
            if validate_uuid(data):
                """if the remote device has already go a valid id, and we don't, update accordingly"""
                if not self.driver.deviceId :
                    self.driver.deviceId=data
                    sucess=True
                elif self.driver.deviceId!= data:
                    self.isProcessing=False
                    self._set_deviceId()
                    """if we end up here again, it means something went wrong with 
                    the remote setting of id, so add to errors"""
                    self.driver.connectionErrors+=1
                elif self.driver.deviceId==data:
                    sucess=True     
            else:
                if not self.driver.deviceId:
                    self.driver.deviceId=str(uuid.uuid4())
                self.isProcessing=False
                self._set_deviceId()
        else:
            """ some other connection mode , that still requires id check"""
            if not validate_uuid(data) or self.driver.deviceId!= data:
                log.msg("Device id not set or not valid",system="Driver")
                self.driver.connectionErrors+=1
                self.isProcessing=False
                self.driver.reconnect()
            else:
                sucess=True
                
        if sucess is True: 
            self.driver.isDeviceIdOk=True
            log.msg("DeviceId match ok: id is ",data,system="Driver")
            self.driver.isConfigured=True 
            self.isProcessing=False
            self.driver.disconnect()
            self.driver.d.callback(None)      
        
    def _set_deviceId(self,id=None):
        print("attempting to set device id")
        self.isProcessing=True
        self.send_data("s "+ self.driver.deviceId)
        self.isProcessing=False
        
    def _query_deviceInfo(self):
        """method for retrieval of device info (for id and more) """
        self.isProcessing=True
        self.send_data("i")
        self.isProcessing=False
        
    def _format_data_out(self,data,*args,**kwargs):
        """
        Formats an outgoing block of data according to some specs/protocol 
        data: the outgoing data to the device
        """
        data=data.split(';')[0]
        data=data.strip()
        data=data.replace(' ','')
        data=data.replace("\t",'')
        return data+ "\n"
        
    def connectionLost(self,reason="connectionLost"):
        self.driver.isDeviceHandshakeOk=False
        BaseSerialProtocol.connectionLost(self,reason)
        
class HardwareHandler(SerialHardwareHandler):
    classProvides(IPlugin, idoboz_web.IDriverHardwareHandler)
    def __init__(self,*args,**kwargs):
        SerialHardwareHandler.__init__(self,protocol=MakerbotProtocol(*args,**kwargs),speed=38400,*args,**kwargs)

class TeacupDriver(object):
    """Class defining the components of the driver for the teacup reprap firmware """
    classProvides(IPlugin, idoboz_web.IDriver)
    components={"logicHandler":CommandQueueLogic,"hardwareHandler":HardwareHandler}
    
    
    
from zope.interface import implements
from twisted.plugin import IPlugin
from doboz_web import idoboz_web 
from zope.interface import classProvides
from twisted.python import log,failure
from doboz_web.core.logic.components.drivers.driver import Driver,CommandQueueLogic
from doboz_web.core.logic.components.drivers.serial.serial_hardware_handler import BaseSerialProtocol,SerialHardwareHandler

class TeacupProtocol(BaseSerialProtocol):
    """
    Class defining the protocol used by this driver: in this case, the reprap teacup protocol 
    which is the most straighforward of reprap protocols (no checksum etc)
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
                    print("here")
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
        
    def enqueue_point(self,point):
       pass
    def set_extruder_temperature(self,temperature):
       self.send_data("M104S"+temperature)
    def set_bed_temperature(self,temperature):
       self.send_data("M140S"+temperature)
        
class TeacupHardwareHandler(SerialHardwareHandler):
    classProvides(IPlugin, idoboz_web.IDriverHardwareHandler)
    def __init__(self,*args,**kwargs):
        SerialHardwareHandler.__init__(self,protocol=TeacupProtocol(*args,**kwargs),*args,**kwargs)

class TeacupDriver(Driver):
    """Class defining the components of the driver for the teacup reprap firmware """
    classProvides(IPlugin, idoboz_web.IDriver)
    TABLENAME="drivers"   
    def __init__(self,driverType="TeacupDriver",deviceType="3d printer",deviceId="",options={},*args,**kwargs):
        """
        very important : the first two args should ALWAYS be the CLASSES of the hardware handler and logic handler,
        and not instances of those classes
        """
        Driver.__init__(self,TeacupHardwareHandler,CommandQueueLogic,driverType,deviceType,deviceId,options,*args,**kwargs)
   
    """potentially generic"""
    def get_firmware_version(self):
        self.send_command("M115")
    def set_debugLevel(self,level):
        self.send_command("M111")
    def init(self):
        self.send_command("")
        
    def startup(self):
        self.send_command("M190")
    def shutdown(self):
        self.send_command("M191")
    
    def queue_position(self,position,extended=False,absolute=True,rapid=False):
        if rapid:
            self.send_command("G1"+str(position))
            
    def get_position(self,extended=False):
        self.send_command("M114")
        
    def set_position(self,position,extended=False):
        self.send_command("G92"+str(position)) 
    
    def save_homePosition(self):
        self.send_command("G92")       
    def load_homePosition(self):
        """not implemented"""
    def go_homePosition(self):
        self.send_command("G28")
        
    def set_unit(self,unit="mm"):
        if unit=="mm":
            self.send_command("G21")
        elif unit=="inch":
            self.send_command("G20")
    """"""
    #tools
    def tool_query(self,toolIndex):
        pass
    def tool_command(self):
        pass
    def change_tool(self):
        self.send_command("M6")        
    def wait_forTool(self):
        pass

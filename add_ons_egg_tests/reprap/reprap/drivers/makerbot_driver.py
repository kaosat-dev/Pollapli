from zope.interface import implements
from twisted.plugin import IPlugin
from doboz_web import idoboz_web 
from zope.interface import classProvides
from twisted.python import log,failure
from doboz_web.core.components.drivers.driver import Driver,CommandQueueLogic
from doboz_web.core.components.drivers.serial.serial_hardware_handler import BaseSerialProtocol,SerialHardwareHandler

"""
Makerbot protocol infos: (from http://replicat.org/sanguino3g)

A package is used to wrap every command. It ensures that the command received is complete and not corrupted. The package contains the following bytes:

0: start byte, always 0xD5
1: length of the packet, not including the start byte, length byte or the CRC.
2: the command byte - this is the first byte of the payload
*: content of the block, all multibyte values are LSB first (Intel notation)
n-1: the package ends with a single byte CRC checksum of the payload (Maxim 1-Wire CRC)
#            uint8_t 
#            _crc_ibutton_update(uint8_t crc, uint8_t data) 
#            { 
#           uint8_t i; 
#        
#           crc = crc ^ data; 
#           for (i = 0; i < 8; i++) 
#           { 
#               if (crc & 0x01) 
#                   crc = (crc >> 1) ^ 0x8C; 
#               else 
#                   crc >>= 1; 
#           } 
#        
#           return crc; 
#            }
Reply Packages

Reply packages are built just like the command packages. The first byte of the payload is the return code 
for the previous command (see Response Code below). All further bytes depend on the command sent.
"""



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
        data: the incoming data from the machine
        """
        log.msg("Attempting to validate device handshake",system="Driver",logLevel=logging.INFO)
        self.driver.isDeviceHandshakeOk=True
        self._query_deviceInfo()
        
         
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
        self.send_data("s "+ self.driver.deviceId)
        
    def _query_deviceInfo(self):
        """method for retrieval of device info (for id and more) """
        self.send_data("i")
        
    def _format_data_out(self,data,*args,**kwargs):
        """
        Formats an outgoing block of data according to some specs/protocol 
        data: the outgoing data to the device provided as an utf8 string
        """
        
        """ chksum = 0 xor each byte of the gcode (including the line number and trailing space)
        """     
        
        def compute_crc(crc,data):
            crc = crc ^ ord(data)
            for c in range(0,8):
                if crc & ord(0x01):
                    crc=crc >>1 ^ 0x8C
                else:
                    crc>>1
            return crc


        command,args=data
        payload=command+content
    
        dataOut=bytearray()
        dataOut.append(0xD5)
        dataOut.append(len(payload))
        dataOut.append(command)
        dataOut.append(args)
        
        crc = 0
        for c in payload:
            crc=compute_crc(crc,c)
        
        dataOut.append(crc)
        

        return data
    
    def _format_data_in(self,data,*args,**kwargs):
        """
        Formats an incoming data block according to some specs/protocol 
        data: the incoming data from the device
        """
        data=bytearray(data)
        responseCode=data[0]
        responseData=data[1:]
        
        return data
        
    def connectionLost(self,reason="connectionLost"):
        self.driver.isDeviceHandshakeOk=False
        BaseSerialProtocol.connectionLost(self,reason)
        
class HardwareHandler(SerialHardwareHandler):
    classProvides(IPlugin, idoboz_web.IDriverHardwareHandler)
    def __init__(self,*args,**kwargs):
        SerialHardwareHandler.__init__(self,protocol=MakerbotProtocol(*args,**kwargs),speed=38400,*args,**kwargs)

class MakerbotDriver(Driver):
    """Class defining the components of the driver for the teacup reprap firmware """
    classProvides(IPlugin, idoboz_web.IDriver)
    TABLENAME="drivers"   
    def __init__(self,driverType="MakerbotDriver",deviceType="3d printer",deviceId="",options={},*args,**kwargs):
        """
        very important : the first two args should ALWAYS be the CLASSES of the hardware handler and logic handler,
        and not instances of those classes
        """
        Driver.__init__(self,TeacupHardwareHandler,CommandQueueLogic,driverType,deviceType,deviceId,options,*args,**kwargs)
   
    """potentially generic"""
    
    def get_firmware_version(self):
        self.send_command((0x00,None))
    def get_status(self):
        pass
    def get_stats(self):
        pass
    def set_debugLevel(self,level):
        self.send_command((0x76,None))
    def init(self):
        self.send_command((0x01,None))
    def start(self):
        pass
    def stop(self,extended=False,motors=False,queue=False):
        if extended:
            payload=None
            if motors:
                payload=1
            
            self.send_command((0x22,None))
    def pause(self):
        self.send_command((0x07,None))
    def queue_position(self,position,extended=False,absolute=True):
        if extended:
            self.send_command((0x1,None))
        else:
            self.send_command((0x81,None))
    def get_position(self,extended=False):
        if extended:
            self.send_command((0x21,None))
        else:
            self.send_command((0x07,None))
            
    def set_position(self,position=None,extended=False):
        if extended:
            self.send_command((0x21,None))
        else:
            payload=position
            self.send_command((0x82,None))
            
    def save_homePosition(self):
        pass
    def load_homePosition(self):
        pass
    """"""
    """"""
    def get_range(self,axes=[]):
        pass
    def enableDisable_axes(self,axes={}):
        pass
    def set_position_registers(self):
        pass
    def clear_buffer(self):
        pass
    def get_bufferSize(self):
        pass
   
    def read_eeprom(self):
        pass
    def write_eeprom(self):
        pass
    #tools
    def tool_query(self,toolIndex):
        pass
    def tool_command(self):
        pass
    def change_tool(self):
        pass#self.send_command("M6")
        
    def wait_forTool(self):
        pass
    def enable_axes(self):
        pass
    
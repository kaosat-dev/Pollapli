from zope.interface import implements
from twisted.plugin import IPlugin
from pollapli import ipollapli 
from zope.interface import classProvides
from twisted.python import log,failure
from twisted.internet import reactor, defer
import uuid,logging
from pollapli.exceptions import DeviceHandshakeMismatch,DeviceIdMismatch
from pollapli.core.logic.components.drivers.driver import Driver,DriverManager,CommandQueueLogic,EndPoint
from pollapli.core.logic.components.drivers.protocols import BaseTextSerialProtocol
from pollapli.core.logic.components.drivers.serial_hardware_handler import SerialHardwareHandler

class ReprapBaseProtocol(BaseTextSerialProtocol):
    """
    Class defining the protocol used by this driver: in this case, the reprap teacup protocol 
    which is the most straighforward of reprap protocols (no checksum etc)
    """
    def __init__(self,driver=None,is_buffering=True,seperator='\n',*args,**kwargs):
        BaseTextSerialProtocol.__init__(self,driver,is_buffering,seperator)
        
   
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
        
class BaseReprapDriver(Driver):
    """Class defining the components of the driver for the teacup reprap firmware """
    #classProvides(IPlugin, ipollapli.IDriver)
    TABLENAME="drivers"   
    def __init__(self,deviceType="3d printer",connectionType="serial",options={},*args,**kwargs):
        """
        very important : the first two args should ALWAYS be the CLASSES of the hardware handler and logic handler,
        and not instances of those classes
        """
        Driver.__init__(self,deviceType,connectionType,SerialHardwareHandler,CommandQueueLogic,ReprapBaseProtocol,options,*args,**kwargs)
  
    """ generic"""
    def get_firmware_version(self):
        self.send_command("M115")
    def set_debug_level(self,level):
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

from zope.interface import implements
from twisted.plugin import IPlugin
from doboz_web import idoboz_web 
from zope.interface import classProvides
from twisted.python import log,failure
from doboz_web.core.components.drivers.driver import Driver,CommandQueueLogic
from doboz_web.core.components.drivers.serial.serial_hardware_handler import BaseSerialProtocol,SerialHardwareHandler


class FiveDProtocol(BaseSerialProtocol):
    """
    Class defining the protocol used by this driver: in this case, the reprap 5D protocol (similar to teacup, but with checksum)
    """
    def __init__(self,driver=None,isBuffering=True,seperator='\n',*args,**kwargs):
       # print("in  fived Protocol", seperator,driver)
        BaseSerialProtocol.__init__(self,driver,isBuffering,seperator)
        self.deviceHandshakeOk=False
        self.currentLine=1
        
    def _handle_deviceHandshake(self,data):
        """
        handles machine (hardware node etc) initialization
        datab: the incoming data from the machine
        """
        if "start" in data:
            self.deviceHandshakeOk=True
            log.msg("Device handshake validated",system="Driver")
            #self.logger.critical("Machine Initialized")
        else:
            raise Exception("Machine NOT INITIALIZED")
        
    def _format_data_out(self,data,*args,**kwargs):
        """
        Cleanup gcode : remove comments and whitespaces
        """
        
        data=data.split(';')[0]
        data=data.strip()
        data=data.replace(' ','')
        data=data.replace("\t",'')

        """RepRap Syntax: N<linenumber> <cmd> *<chksum>\n"""
        data = "N"+str(self.currentLine)+' '+data+''
        
        """ chksum = 0 xor each byte of the gcode (including the line number and trailing space)
        """     
        checksum = 0
        for c in data:
            checksum^=ord(c)
            
        self.currentLine+=1
        
        return data+'*'+str(checksum)+"\n"
    
    def connectionLost(self,reason="connectionLost"):
        self.deviceHandshakeOk=False
        BaseSerialProtocol.connectionLost(self,reason)
        
class FiveDHardwareHandler(SerialHardwareHandler):
    classProvides(IPlugin, idoboz_web.IDriverHardwareHandler)
    def __init__(self,*args,**kwargs):
        SerialHardwareHandler.__init__(self,protocol=FiveDProtocol(*args,**kwargs),*args,**kwargs)




class FiveDDriver(object):
    """Class defining the components of the driver for the 5D reprap firmware """
    classProvides(IPlugin, idoboz_web.IDriver)
    components={"logicHandler":CommandQueueLogic,"hardwareHandler":FiveDHardwareHandler}
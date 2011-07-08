from zope.interface import implements
from twisted.plugin import IPlugin
from doboz_web import idoboz_web 
from zope.interface import classProvides
from twisted.python import log,failure
from doboz_web.core.components.drivers.driver import Driver,CommandQueueLogic
from doboz_web.core.components.drivers.serial.serial_hardware_handler import BaseSerialProtocol,SerialHardwareHandler



class TeacupProtocol(BaseSerialProtocol):
    def __init__(self,driver=None,isBuffering=True,seperator='\n',*args,**kwargs):
       # print("in  teacup Protocol", seperator,driver)
        BaseSerialProtocol.__init__(self,driver,isBuffering,seperator)
        self.deviceHandshakeOk=False
        
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
        Formats an outgoing block of data according to some specs/protocol 
        data: the outgoing data to the device
        """
        data=data.split(';')[0]
        data=data.strip()
        data=data.replace(' ','')
        data=data.replace("\t",'')
        return data+ "\n"
    
    def connectionLost(self,reason="connectionLost"):
        self.deviceHandshakeOk=False
        BaseSerialProtocol.connectionLost(self,reason)
        
    

class HardwareHandler(SerialHardwareHandler):
    classProvides(IPlugin, idoboz_web.IDriverHardwareHandler)
    def __init__(self,*args,**kwargs):
        SerialHardwareHandler.__init__(self,protocol=TeacupProtocol(*args,**kwargs),*args,**kwargs)

class TeacupDriver(object):
    classProvides(IPlugin, idoboz_web.IDriver)
    components={"logicHandler":CommandQueueLogic,"hardwareHandler":HardwareHandler}
    
    
    
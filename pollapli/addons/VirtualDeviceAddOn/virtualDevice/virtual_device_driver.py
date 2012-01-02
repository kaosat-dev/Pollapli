from zope.interface import implements
from twisted.plugin import IPlugin
from pollapli import ipollapli 
from zope.interface import classProvides
from twisted.python import log,failure
from twisted.internet import reactor, defer
from twisted.internet.interfaces import IProtocol
import uuid, logging
from pollapli.exceptions import DeviceHandshakeMismatch,DeviceIdMismatch
from pollapli.core.logic.components.drivers.driver import Driver,DriverManager,CommandQueueLogic
from pollapli.core.logic.components.drivers.protocols import BaseProtocol


class VirtualDeviceProtocol(BaseProtocol):
    classProvides(IPlugin, IProtocol)
    """
    Class defining the protocol used by this driver: in this case, the reprap 5D protocol (similar to teacup, but with checksum)
    """
    def __init__(self,driver=None,seperator='\n',*args,**kwargs):
        BaseProtocol.__init__(self,driver)
        self.virtualDevice=VirtualDevice(self)
        
    def connectionMade(self):
        log.msg("Device connected",system="Driver",logLevel=logging.INFO)   
        self.set_connection_timeout()    
        if self.driver.connectionMode == 1 :
            self.driver._send_signal("connected",self.driver.hardwareHandler.port) 
        self.virtualDevice.setup()
        #self.dataReceived(self.virtualDevice.currentResponse)
#        self.driver.is_handshake_ok=True
#        if self.driver.connectionMode==2 or self.driver.connectionMode==0:
#            if not self.driver.deviceId:
#                self.driver.deviceId=str(uuid.uuid4())
#            self.driver.is_authentification_ok=True
#            self.driver.isConfigured=True 
#            self.driver.disconnect()
#            self.driver.deferred.callback(None)  
        
    def _handle_hardware_handshake(self,data):
        """
        handles machine (hardware node etc) initialization
        data: the incoming data from the machine
        """
        """
        handles machine (hardware node etc) initialization
        data: the incoming data from the machine
        """
        log.msg("Attempting to validate device handshake",system="Driver",logLevel=logging.INFO)
        if "start" in data:
            self.driver.is_handshake_ok=True
            log.msg("Device handshake validated",system="Driver",logLevel=logging.INFO)
            self._get_hardware_id()
        else:
            log.msg("Device hanshake mismatch",system="Driver",logLevel=logging.INFO)
            self.driver.reconnect()
    
    def _handle_device_id_init(self,data):
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
        
        sucess=False
        if self.driver.connectionMode==2 or self.driver.connectionMode==0:
            """if we are trying to set the device id"""    
            if validate_uuid(data):
                log.msg("Remote device Id uuid valid",system="Driver",logLevel=logging.DEBUG)
                """if the remote device has already go a valid id, and we don't, update accordingly"""
                if not self.driver.deviceId :
                    self.driver.deviceId=data
                    sucess=True
                elif self.driver.deviceId!= data:
                    self._set_hardware_id()
                    #self._get_hardware_id()
                    """if we end up here again, it means something went wrong with 
                    the remote setting of id, so add to errors"""
                    self.driver.connectionErrors+=1
                elif self.driver.deviceId==data:
                    sucess=True     
            else:
                log.msg("Remote device Id uuid NOT valid",system="Driver",logLevel=logging.DEBUG)
                if not self.driver.deviceId:
                    self.driver.deviceId=str(uuid.uuid4())
                self.driver.connectionErrors+=1
                self._set_hardware_id()
                
        else:
            """ some other connection mode , that still requires id check"""
            if not validate_uuid(data) or self.driver.deviceId!= data:
                log.msg("Device id not set or not valid",system="Driver")
                self.driver.connectionErrors+=1
                self.driver.reconnect()
            else:
                sucess=True
                
        if sucess is True: 
            self.driver.is_authentification_ok=True
            log.msg("DeviceId match ok: id is ",data,system="Driver")
            self.driver.isConfigured=True 
            self.driver.disconnect()
            self.driver.deferred.callback(None)      
        
    def _set_hardware_id(self,id=None):
        self.send_data("s "+ self.driver.deviceId)
        
    def _get_hardware_id(self):
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
          
        
class VirtualDeviceHardwareHandler(object):
    classProvides(IPlugin, ipollapli.IDriverHardwareHandler)
    
    blockedPorts=[]
    avalailablePorts=[]
    avalailablePorts.append("port"+str(uuid.uuid4()))
    
    def __init__(self,driver,protocol,*args,**kwargs):
        self.driver=driver
        self.protocol=protocol(driver,*args,**kwargs)
        self.speed=115200
       
        
    def write(self,data,*args,**kwargs):
        self.protocol.virtualDevice.handle_request(data)
        
    def send_data(self,command):
        self.protocol.send_data(command)
        
    def connect(self,port=None,*args,**kwargs):
        self.driver.connectionErrors=0
        log.msg("Connecting... Port:",port," at speed ",self.speed,system="Driver",logLevel=logging.DEBUG)
        if port:  
            self.port=port
        self._connect(port,*args,**kwargs)
    
    def reconnect(self):
        self.disconnect(clearPort=False)
        self._connect()
        
    def disconnect(self,clearPort=False):   
        self.driver.isConnected=False   
        if clearPort:
            self.port=None
            if self.port in VirtualDeviceHardwareHandler.blockedPorts:
                VirtualDeviceHardwareHandler.blockedPorts.remove(self.port)
        self.protocol.connectionLost()
        self.serial=None
    
    def connectionClosed(self,failure):
        pass
        
    def _connect(self,*args,**kwargs):
        """Port connection/reconnection procedure"""   
        if self.port and self.driver.connectionErrors<self.driver.maxConnectionErrors:
            try:      
                #self.port=str((yield self.scan())[0])   
                if not self.port in VirtualDeviceHardwareHandler.blockedPorts:
                    VirtualDeviceHardwareHandler.blockedPorts.append(self.port)        
                self.driver.isConnected=True
                self.protocol.makeConnection(self)
                #self.serial=SerialWrapper(self.protocol,self.port,reactor,baudrate=self.speed)
                #self.serial.deferred.addCallbacks(callback=self._connect,errback=self.connectionClosed)  
            except Exception as inst:          
                self.driver.isConnected=False
                self.driver.connectionErrors+=1
                
                log.msg("failed to connect virtual driver, attempts left:",self.driver.maxConnectionErrors-self.driver.connectionErrors,"error",inst,system="Driver")
                if self.driver.connectionErrors<self.driver.maxConnectionErrors:
                    reactor.callLater(self.driver.connectionErrors*5,self._connect)
                
        if self.driver.connectionErrors>=self.driver.maxConnectionErrors:
            try:
                self.serial.deferred.cancel()
                self.disconnect(clearPort=True)
            except:pass
            
            if self.driver.connectionMode==1:
                log.msg("cricital error while (re-)starting serial connection : please check your driver settings and device id, as well as cables,  and make sure no other process is using the port ",system="Driver",logLevel=logging.CRITICAL)
            else:
                log.msg("Failed to establish correct connection with device/identify device by id",system="Driver",logLevel=logging.DEBUG)
                reactor.callLater(1,self.driver.deferred.errback,failure.Failure())
                

        
    @classmethod       
    def list_ports(cls):
        """
        Return a list of ports: as this is a virtual device, it returns a random port name
        """
        d=defer.Deferred()
        def _list_ports(*args,**kwargs):
            #foundPorts=[]
            #cls.avalailablePorts.append()
            
            return cls.avalailablePorts 
        reactor.callLater(0.1,d.callback,None)
        d.addCallback(_list_ports)
        return d
    
    
        
class VirtualDevice(object):
    """emulated arduino like device, very hackish for now , but allows for some testing without connecting any 
    real arduino"""
    def __init__(self,protocol):
        self.protocol=protocol
        self.deviceId=""
    
    def setup(self):
        """just like for an actual arduino , the setup function is the first one to get called"""
        self.send_response("start\n")
        
    def handle_request(self,data):
        data=data.replace("\n","")
        data=data.encode('utf-8')
        cmdElems=data.split(" ")
        cmd=cmdElems[0]
        if cmd=="i":
            self.send_response(self.deviceId+"\n")
        elif cmd=="s":
            cmdParam=cmdElems[1]
            self.deviceId=cmdParam
            self.send_response(self.deviceId+"\n")
        
    def send_response(self,data):
        self.protocol.dataReceived(data)

class VirtualDeviceDriver(Driver):
    """Class defining the components of the driver for a basic arduino,using attached firmware """
    classProvides(IPlugin, ipollapli.IDriver) 
    TABLENAME="drivers"   
    def __init__(self,deviceType="Virtual",deviceId="",connectionType="virtual",options={},*args,**kwargs):
        """
        very important : the first two args should ALWAYS be the CLASSES of the hardware handler and logic handler,
        and not instances of those classes
        """
        Driver.__init__(self,deviceType,connectionType,VirtualDeviceHardwareHandler,CommandQueueLogic,VirtualDeviceProtocol,options,*args,**kwargs)

        
    def hello_world(self):
        self.send_command('a')
import logging,ast,time,re
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from zope.interface import Interface, Attribute,implements,classProvides
from twisted.plugin import IPlugin,getPlugins
from twisted.internet.protocol import Protocol
from twisted.internet.interfaces import IProtocol
from uuid import uuid4

class DummyProtocol(Protocol):
    classProvides(IPlugin, IProtocol)
    """used for connection checks"""
    pass


class BaseProtocol(Protocol):
    classProvides(IPlugin, IProtocol)
    """generic base protocol, cannot be used directly"""
    def __init__(self,driver=None, is_buffering=True, seperator=None, handshake=None):             
        self.driver = driver
        self.isBuffering = is_buffering
        self.seperator = seperator
        self.handshake = handshake
        self.buffer = []
        self.timeout = None

    def _timeoutCheck(self, *args, **kwargs):
        if self.driver.isConnected:
            if self.driver.connectionMode == 2:
                log.msg("Here Timeout check at ", time.time(), logLevel=logging.DEBUG)
                self._cancel_timeout()
                self.driver.connectionErrors += 1
                self.driver.reconnect()
            else:
                self._cancel_timeout()
        else:
            self._cancel_timeout()

    def _set_timeout(self):
        if self.driver.connectionMode == 2:
            log.msg("Setting timeout at ",time.time(),logLevel=logging.DEBUG)    
            self.timeout = reactor.callLater(self.driver.connectionTimeout,self._timeoutCheck)

    def _cancel_timeout(self):
            if self.timeout:
                try:
                    self.timeout.cancel()
                    log.msg("Cancel timeout at ", time.time(), logLevel=logging.DEBUG)
                except:pass

    def connectionMade(self):
        log.msg("Device connected",system="Driver",logLevel=logging.INFO)   
        self._set_timeout()    
        if self.driver.connectionMode == 1 :
            self.driver.send_signal("connected",self.driver.hardwareHandler.port) 
            
    def connectionLost(self,reason="connectionLost"):
        self.driver.isDeviceHandshakeOk=False
        log.msg("Device disconnected",system="Driver",logLevel=logging.INFO)  
        if self.driver.connectionMode==1:
            self.driver.send_signal("disconnected",self.driver.hardwareHandler.port)
        if self.timeout:
            try:
                self.timeout.cancel()
            except: pass
            
    def _query_hardware_info(self):
        """method for retrieval of device info (for id and more) """
        pass   
    
    def _set_hardware_id(self,id=None):
        """ method for setting device id: MANDATORY for all drivers/protocols """
        pass
    
    def _handle_deviceHandshake(self,data):
        """
        handles machine (hardware node etc) initialization
        data: the incoming data from the machine
        """
        log.msg("Attempting to validate device handshake",system="Driver",logLevel=logging.INFO)
        if self.handshake is not None:
            if self.handshake in data:
                self.driver.isDeviceHandshakeOk=True
                log.msg("Device handshake validated",system="Driver",logLevel=logging.DEBUG)
                self._query_hardware_info()
            else:
                log.msg("Device hanshake mismatch: expected :",self.handshake,"got:",data,system="Driver",logLevel=logging.DEBUG)
                self.driver.reconnect()
        else:
            self.driver.isDeviceHandshakeOk=True
            self._query_hardware_info()
            
    def _handle_deviceIdInit(self,data):
        """
        handles machine (hardware node etc) initialization
        data: the incoming data from the machine
        """
       
    def _format_data_in(self,data,*args,**kwargs):
        """
        Formats an incoming data block according to some specs/protocol 
        data: the incoming data from the device
        """
        data=data.replace('\n','')
        data=data.replace('\r','')
        return data
    
    def _format_data_out(self,data,*args,**kwargs):
        """
        Formats an outgoing block of data according to some specs/protocol 
        data: the outgoing data to the device
        """
        return data
    
    def dataReceived(self, data):
        self._cancel_timeout()
        data = data.encode('utf-8')
        data = data.replace(' ','')
        data = self._format_data_in(data)
        log.msg("Data recieved <<: ",data,system = "Driver",logLevel = logging.DEBUG)  
                    
        if not self.driver.connectionMode==3:
            if not self.driver.isConfigured:
                if not self.driver.isDeviceHandshakeOk:
                    self._handle_deviceHandshake(data)
                elif not self.driver.isDeviceIdOk:
                    self._handle_deviceIdInit(data)
            else:
                if not self.driver.isDeviceHandshakeOk:
                    self._handle_deviceHandshake(data)
                else:
                    self.driver._handle_response(data)
        else:
            if not self.driver.isDeviceHandshakeOk:
                self._handle_deviceHandshake(data)
            else:
                self.driver._handle_response(data)
                            
    def send_data(self,data,*args,**kwargs):  
        """
        Simple wrapper to send data over serial
        """    
        try:
            log.msg("Data sent >>: ",self._format_data_out(data),system="Driver",logLevel=logging.DEBUG)
            self._set_timeout()
            self.transport.write(self._format_data_out(data))
        except Exception:
            log.msg("serial device not connected or not found on specified port",system="Driver",logLevel=logging.CRITICAL)
        
            
class BaseTextSerialProtocol(BaseProtocol):
    classProvides(IPlugin, IProtocol)
    """basic , text based protocol for serial devices"""
    def __init__(self,driver=None,is_buffering=True,seperator='\r\n',handshake="start"):  
        BaseProtocol.__init__(self, driver, is_buffering, seperator,handshake)
        self.buffer=""
        self.regex = re.compile(self.seperator)
            
    def _handle_deviceIdInit(self,data):
        """
        handles machine (hardware node etc) initialization
        data: the incoming data from the machine
        """
        log.msg("Attempting to configure device Id: recieved data",data,system="Driver",logLevel=logging.DEBUG)
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
                    self.driver.deviceId = data
                    sucess = True
                elif self.driver.deviceId != data:
                    log.msg("Remote and local DeviceId mismatch settind distant device id to",self.driver.deviceId,system="Driver",logLevel=logging.DEBUG)
                    self._set_hardware_id()
                    #self._query_hardware_info()
                    """if we end up here again, it means something went wrong with 
                    the remote setting of id, so add to errors"""
                    self.driver.connectionErrors+=1
                    
                elif self.driver.deviceId==data:
                    sucess = True     
            else:
                log.msg("Remote Device id was not valid:",data,system="Driver",logLevel=logging.DEBUG)
                if not self.driver.deviceId:
                    self.driver.deviceId=str(uuid4())
                    log.msg("Device id was not set, generating a new one",self.driver.deviceId,system="Driver",logLevel=logging.DEBUG)
                self.driver.connectionErrors+=1
                self._set_hardware_id()
                
        else:
            """ some other connection mode , that still requires id check"""
            if not validate_uuid(data) or self.driver.deviceId!= data:
                log.msg("Device id not set or not valid",system="Driver",logLevel=logging.DEBUG)
                self.driver.connectionErrors+=1
                self.driver.reconnect()
            else:
                sucess = True
                
        if sucess is True: 
            self.driver.isDeviceIdOk=True
            log.msg("DeviceId match ok: id is ",data,system="Driver",logLevel=logging.DEBUG)
            self.driver.isConfigured=True 
            self.driver.disconnect()
            self.driver.d.callback(None)    
                  
    def _format_data_in(self,data,*args,**kwargs):
        """
        Formats an incoming data block according to some specs/protocol 
        data: the INCOMMING data FROM the device
        """
        data=data.replace('\n','')
        data=data.replace('\r','')
        return data
    
    def _format_data_out(self,data,*args,**kwargs):
        """
        Formats an outgoing block of data according to some specs/protocol 
        data: the OUTGOING data TO the device
        """
        return data+'\n'
        
    def dataReceived(self, data):
        self._cancel_timeout()
        try:
            if self.isBuffering:   
                self.buffer+=str(data.encode('utf-8'))
                #if we have NOT already checked the last state of the data block, then check it
                results = None
                try:
                    results=self.regex.search(self.buffer)        
                except Exception as inst:
                    log.msg("Error while parsing serial data :",self.buffer,"error:",inst,system="driver",logLevel=logging.CRITICAL)
                    
                while results is not None:
                    nDataBlock= self.buffer[:results.start()] 
                    try:
                        nDataBlock=self._format_data_in(nDataBlock)
                    except Exception as inst:
                        log.msg("Error while formatting serial data :",inst,system="Driver",logLevel=logging.CRITICAL)  
                    log.msg("Data recieved <<: ",nDataBlock,system="Driver",logLevel=logging.DEBUG)  
                    self._set_timeout()
                    try:
                        if not self.driver.connectionMode==3:
                            if not self.driver.isConfigured:
                                    if not self.driver.isDeviceHandshakeOk:
                                        self._handle_deviceHandshake(nDataBlock)
                                    elif not self.driver.isDeviceIdOk:
                                        self._handle_deviceIdInit(nDataBlock)
                            else:
                                if not self.driver.isDeviceHandshakeOk:
                                    self._handle_deviceHandshake(nDataBlock)
                                else:
                                    self.driver._handle_response(nDataBlock)
                        else:
                            if not self.driver.isDeviceHandshakeOk:
                                    self._handle_deviceHandshake(nDataBlock)
                            else:
                                self.driver._handle_response(nDataBlock)
                    except Exception as inst:
                        log.msg("Error while handling serial data :",inst,system="Driver",logLevel=logging.CRITICAL)  
                        
                    self.buffer=self.buffer[results.end():]
                    results=None
                    try:
                        results =self.regex.search(self.buffer)
                    except:
                        print("ljklj")
        except Exception as inst:
            log.msg("Critical error in serial, error:",str(inst),system="Driver",logLevel=logging.CRITICAL)
        
    def send_data(self,data,*args,**kwargs):  
        """
        Simple wrapper to send data over serial
        """    
        try:
            import unicodedata       
            data = self._format_data_out(data)
            if isinstance(data,unicode):
                data = unicodedata.normalize('NFKD', data).encode('ascii','ignore')
            log.msg("Data sent >>: ",data," done",system="Driver",logLevel=logging.DEBUG)
            self._set_timeout()
            self.transport.write(data)
        except OSError:
            log.msg("serial device not connected or not found on specified port",system="Driver",logLevel=logging.CRITICAL)
        


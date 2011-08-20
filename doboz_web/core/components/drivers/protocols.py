import logging,ast,time
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from zope.interface import Interface, Attribute,implements
from twisted.plugin import IPlugin,getPlugins
from twisted.internet.protocol import Protocol

class BaseProtocol(Protocol):
    """generic base protocol, cannot be used directly"""
    def __init__(self,driver=None):       
        self.driver=driver
        self.timeout=None
        
    def _timeoutCheck(self,*args,**kwargs):
        if self.driver.isConnected:
            log.msg("Driver timed out at ",time.time(),logLevel=logging.DEBUG)
            self.cancel_timeout()
            self.driver.connectionErrors+=1
            self.driver.reconnect()
        else:
            self.cancel_timeout()

    def set_timeout(self):
        if self.driver.connectionMode==2:
            log.msg("Setting timeout at ",time.time(),logLevel=logging.DEBUG)    
            self.timeout=reactor.callLater(self.driver.connectionTimeout,self._timeoutCheck)
        
    def cancel_timeout(self):
        if self.driver.connectionMode==2:
            if self.timeout:
                try:
                    self.timeout.cancel()
                    log.msg("Cancel timeout at ",time.time(),logLevel=logging.DEBUG)
                except:pass
                
                
    def connectionMade(self):
        log.msg("Device connected",system="Driver",logLevel=logging.INFO)   
        self.set_timeout()    
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
            
    def _query_deviceInfo(self):
        """method for retrieval of device info (for id and more) """
        pass   
    
    def _set_deviceId(self,id=None):
        """ method for setting device id: MANDATORY for all drivers/protocols """
        pass
    
    def _handle_deviceHandshake(self,data):
        """
        handles machine (hardware node etc) initialization
        data: the incoming data from the machine
        """
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
        data=data.encode('utf-8')
        data=data.replace(' ','')
        data=self._format_data_in(data)
        self.cancel_timeout()
        log.msg("Data recieved <<: ",data,system="Driver",logLevel=logging.DEBUG)  
                    
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
            self.set_timeout()
            self.transport.write(self._format_data_out(data))
        except Exception:
            self.logger.critical("serial device not connected or not found on specified port")


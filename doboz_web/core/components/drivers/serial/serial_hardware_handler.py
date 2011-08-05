from twisted.internet.protocol import Protocol, Factory
#from twisted.internet.serialport import SerialPort
from doboz_web.core.patches._win32serialport import SerialPort
import re
import sys
import itertools
import time
import logging
from twisted.internet import reactor, defer
from twisted.internet.task import LoopingCall
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.plugin import IPlugin
from zope.interface import implements,classProvides
from doboz_web import idoboz_web
from doboz_web.exceptions import NoAvailablePort


class SerialHardwareHandler(object):
    classProvides(IPlugin, idoboz_web.IDriverHardwareHandler)
    blockedPorts=[]
    blackListPorts=["COM3"]
    availablePorts=[]

    def __init__(self,driver=None,protocol=None,speed=19200,*args,**kwargs):
        self.logger=logging.getLogger("pollapli.core.components.driver")
        self.driver=driver
        self.serial=None    
        self.protocol=protocol
        self.speed=speed
        self.port=None
        self.isConnected=False
        self.notMyPorts=[]
        self.setupMode=False
           
            
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
            if self.port in SerialHardwareHandler.blockedPorts:
                SerialHardwareHandler.blockedPorts.remove(self.port)
        try:
            if self.serial:
                try:
                    self.serial.d.cancel()
                except:pass
                try:
                    self.serial.loseConnection()
                except:pass
                self.serial=None
        except Exception as inst:
            print("error in serial disconnection",str(inst))
    
    def connectionClosed(self,failure):
        pass
        
    def _connect(self,*args,**kwargs):
        """Port connection/reconnection procedure"""   
        if self.port and self.driver.connectionErrors<self.driver.maxConnectionErrors:
            try:      
                #self.port=str((yield self.scan())[0])   
                if not self.port in SerialHardwareHandler.blockedPorts:
                    SerialHardwareHandler.blockedPorts.append(self.port)        
                self.driver.isConnected=True
                self.serial=SerialWrapper(self.protocol,self.port,reactor,baudrate=self.speed)
                self.serial.d.addCallbacks(callback=self._connect,errback=self.connectionClosed)  
            except Exception as inst:          
                #log.msg("cricital error while (re-)starting serial connection : please check your driver speed,  cables,  and make sure no other process is using the port ",str(inst))
                self.driver.isConnected=False
                self.driver.connectionErrors+=1
                log.msg("failed to connect serial driver, attempts left:",self.driver.maxConnectionErrors-self.driver.connectionErrors,system="Driver")
                if self.driver.connectionErrors<self.driver.maxConnectionErrors:
                    reactor.callLater(self.driver.connectionErrors*5,self._connect)
                
        if self.driver.connectionErrors>=self.driver.maxConnectionErrors:
            try:
                self.serial.d.cancel()
                self.disconnect(clearPort=True)
            except:pass
            
            if self.driver.connectionMode==1:
                log.msg("cricital error while (re-)starting serial connection : please check your driver settings and device id, as well as cables,  and make sure no other process is using the port ",system="Driver",logLevel=logging.CRITICAL)
            else:
                log.msg("Failed to establish correct connection with device/identify device by id",system="Driver",logLevel=logging.DEBUG)
                reactor.callLater(1,self.driver.d.errback,failure.Failure())
                

        
    @classmethod       
    def list_ports(cls):
        """
        Return a list of ports
        """
        d=defer.Deferred()
        def _list_ports(*args,**kwargs):
            foundPorts=[]
            if sys.platform == "win32":
                import _winreg as winreg
                path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                except WindowsError:
                    raise EnvironmentError
                for i in itertools.count():
                    try:
                        val = winreg.EnumValue(key, i)
                        port=str(val[1])
                        if port not in cls.blackListPorts: 
                            foundPorts.append(port)
                    except EnvironmentError:
                        break
            else:
                foundPorts= glob.glob('/dev/ttyUSB*')+ glob.glob('/dev/cu*') 
                log.msg("Serial Ports on  system:",+str(foundPorts),system="Driver",logLevel=logging.DEBUG)
            return foundPorts
        
        reactor.callLater(0.1,d.callback,None)
        d.addCallback(_list_ports)
        return d
    
    @classmethod
    @defer.inlineCallbacks 
    def list_availablePorts(cls):
        """scan for available ports.
        Returns a list of actual available ports"""        
        available = []
        serial=None
        for port in (yield cls.list_ports()):  
            if port not in cls.blackListPorts: 
                try:
                    serial = SerialWrapper(DummyProtocol(),port,reactor) 
                    available.append(serial._serial.name)
                    #if port not in cls.availablePorts:
                    #    cls.availablePorts.append(serial._serial.name)
                    serial.loseConnection()  
                except Exception as inst:pass
                    #log.msg("Error while opening port",port,"Error:",inst)
        defer.returnValue(available)
        
    """The next methods are at least partially deprecated and not in use """   
    def reset_seperator(self):
        self.regex = re.compile(self.seperator)
    
    def upload(self):
        avrpath="/home/ckaos/data/Projects/Doboz/doboz_web/core/tools/avr"
        cmd=os.path.join(avrpath,"avrdude")
        conf=os.path.join(avrpath,"avrdude.conf")
        
    def tearDown(self):
        """
        Clean shutdown function
        """
        try:
            SerialHardwareHandler.blockedPorts.remove(self.port)
        except:
            pass
        self.driver.isConnected=False        
        self.logger.critical("Serial shutting down")

        
class DummyProtocol(Protocol):
    pass



class BaseSerialProtocol(Protocol):
    """basic , text based protocol for serial devices"""
    def __init__(self,driver=None,isBuffering=True,seperator='\r\n'):       
        self.seperator=seperator
        self.isBuffering=isBuffering
        self.buffer=""
        self.regex = re.compile(self.seperator)
        self.driver=driver
        self.timeout=None
        
    def _timeoutCheck(self,*args,**kwargs):
        if self.driver.isConnected:
            log.msg("Timeout check at ",time.time(),logLevel=logging.DEBUG)
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
            
    def connectionLost(self,reason="connectionLost"):
        log.msg("Device disconnected",system="Driver",logLevel=logging.INFO)  
        if self.driver.connectionMode==1:
            self.driver.send_signal("disconnected",self.driver.hardwareHandler.port)
        if self.timeout:
            try:
                self.timeout.cancel()
            except: pass
        
    def connectionMade(self):
        log.msg("Device connected",system="Driver",logLevel=logging.INFO)   
        self.set_timeout()    
        if self.driver.connectionMode == 1 :
            self.driver.send_signal("connected",self.driver.hardwareHandler.port)
            
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
        self.cancel_timeout()
        try:
            if self.isBuffering:
                self.buffer+=str(data.encode('utf-8'))
                self.set_timeout()
                #if we have NOT already checked the last state of the data block, then check it
                results=None
                try:
                    results=self.regex.search(self.buffer)        
                except Exception as inst:
                    self.logger.critical("Error while parsing serial data :%s",str(inst))
                            
                while results is not None:
                    nDataBlock= self.buffer[:results.start()] 
                    nDataBlock=self._format_data_in(nDataBlock)
                    log.msg("Data recieved <<: ",nDataBlock,system="Driver",logLevel=logging.DEBUG)  
                    
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
                        
                    self.buffer=self.buffer[results.end():]
                    results=None
                    try:
                        results =self.regex.search(self.buffer)
                    except:
                        pass      
        except Exception as inst:
            log.msg("Critical error in serial",str(inst),system="Driver",logLevel=logging.CRITICAL)
        
    def send_data(self,data,*args,**kwargs):  
        """
        Simple wrapper to send data over serial
        """    
        try:
            log.msg("Data sent >>: ",self._format_data_out(data)," done",system="Driver",logLevel=logging.DEBUG)
            self.set_timeout()
            self.transport.write(self._format_data_out(data).encode('utf-8'))
        except OSError:
            self.logger.critical("serial device not connected or not found on specified port")
        
            
class SerialWrapper(SerialPort):
      def __init__(self,*args,**kwargs):
          SerialPort.__init__(self,*args,**kwargs)
          self._tempDataBuffer=[]
          self.d=defer.Deferred()
      def writeSomeData(self,*args,**kwargs):
          pass
      
      def connectionLost(self,reason="connectionLost"):
          SerialPort.connectionLost(self,reason)
          self.d.callback("connection failure")
    
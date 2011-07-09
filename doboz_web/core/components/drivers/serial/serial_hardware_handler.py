from twisted.internet.protocol import Protocol, Factory
#from twisted.internet.serialport import SerialPort
from doboz_web.core.patches._win32serialport import SerialPort
import re
import sys
import itertools
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.plugin import IPlugin
from zope.interface import implements,classProvides
from doboz_web import idoboz_web
from doboz_web.exceptions import NoAvailablePort

class SerialHardwareHandler(object):
    classProvides(IPlugin, idoboz_web.IDriverHardwareHandler)
    blockedPorts=["COM3"]
    #implements(IPlugin, idoboz_web.IDriverHardwareHandler)
    def __init__(self,driver=None,protocol=None,speed=19200,*args,**kwargs):
        self.driver=driver
        self.serial=None    
        self.protocol=protocol
        self.speed=speed
        self.port=None
        self.isConnected=False
        self.currentErrors=0
        self.maxErrors=2
                
    def send_data(self,command):
        self.protocol.send_data(command)
        
    def connect(self):
        self._connect()
    
    def disconnect(self):      
        try:
            if self.serial:
                try:
                    SerialHardwareHandler.blockedPorts.remove(self.port)
                except:
                    pass
                try:
                    self.serial.d.cancel()
                except:pass
                self.serial.loseConnection()
                self.serial=None
        except Exception as inst:
            print("error in serial disconnection",str(inst))
    
    def connectionClosed(self,failure):
        pass
    
    @defer.inlineCallbacks     
    def _connect(self,*args,**kwargs):
        """Port connection/reconnection procedure"""    
        
        def get_port():
            pass
        try:
            SerialHardwareHandler.blockedPorts.remove(self.port)
        except:
            pass
        self.port=None
        
        if self.port is None and self.currentErrors<self.maxErrors:
            try:      
                self.port=str((yield self.scan())[0])        
                SerialHardwareHandler.blockedPorts.append(self.port)        
                self.currentErrors=0
                self.isConnected=True
                self.serial=SerialWrapper(self.protocol,self.port,reactor,baudrate=self.speed)
                self.serial.d.addCallbacks(callback=self._connect,errback=self.connectionClosed)  
#            except OutofRangeException:
#                raise NoAvailablePort()   
            except Exception as inst:
               
                #log.msg("cricital error while (re-)starting serial connection : please check your driver speed,  cables,  and make sure no other process is using the port ",str(inst))
                self.isConnected=False
                self.currentErrors+=1
                reactor.callLater(self.currentErrors*5,self._connect)

        if not self.port :
            log.msg("failed to connect serial driver, attempts left:",self.maxErrors-self.currentErrors,system="Driver")
            if self.currentErrors>=self.maxErrors:
                log.msg("cricital error while (re-)starting serial connection : please check your driver speed,  cables,  and make sure no other process is using the port ",system="Driver")
                try:
                    self.serial.d.cancel()
                except:pass
            #self.tearDown()
            
    def list_ports(self):
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
                        foundPorts.append(str(val[1]))
                    except EnvironmentError:
                        break
            else:
                foundPorts= glob.glob('/dev/ttyUSB*')+ glob.glob('/dev/cu*')
            return foundPorts
        #self.logger.info("Serial Ports on  system:",+str(foundPorts))
        reactor.callLater(0,d.callback,None)
        d.addCallback(_list_ports)
        return d
    
    @defer.inlineCallbacks        
    def scan(self):
        """scan for available ports.
        Returns a list of actual available ports"""        
        available = []
        serial=None
        for port in (yield self.list_ports()):  
            if port not in SerialHardwareHandler.blockedPorts: 
                try:
                    serial = SerialWrapper(DummyProtocol(),port,reactor) 
                    available.append(serial._serial.name)
                    serial.loseConnection()  
                except Exception as inst:
                    log.msg("Error while opening port",port,"Error:",inst)
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
        self.isConnected=False        
        self.logger.critical("Serial shutting down")

        
class DummyProtocol(Protocol):
    pass
 
class BaseSerialProtocol(Protocol):
    def __init__(self,driver=None,isBuffering=True,seperator='\r\n'):
        self.seperator=seperator
        self.isBuffering=isBuffering
        self.buffer=""
        self.regex = re.compile(self.seperator)
        self.deviceHandshakeOk=True
        self.driver=driver
        
    def connectionLost(self,reason="connectionLost"):
        log.msg("Device disconnected",system="Driver")   
        
    def connectionMade(self):
        log.msg("Device connected",system="Driver") 
          
    def _query_deviceInfo(self):
        """method for retrieval of device info (for id and more) """
        pass   
    
    def _handle_deviceHandshake(self,data):
        """
        handles machine (hardware node etc) initialization
        datab: the incoming data from the machine
        """
        
    def _format_data_in(self,data,*args,**kwargs):
        """
        Formats an incomming data block according to some specs/protocol 
        data: the incomming data from the device
        """
        return data
    
    def _format_data_out(self,data,*args,**kwargs):
        """
        Formats an outgoing block of data according to some specs/protocol 
        data: the outgoing data to the device
        """
        return data
        
    def dataReceived(self, data):
        try:
            if self.isBuffering:
                self.buffer+=str(data)
                #if we have NOT already checked the last state of the data block, then check it
                results=None
                try:
                    results=self.regex.search(self.buffer)        
                except Exception as inst:
                    self.logger.critical("Error while parsing serial data :%s",str(inst))
                            
                while results is not None:
                    nDataBlock= self.buffer[:results.start()] 
                    #log.msg("serial data block",nDataBlock)
                    
                    if not self.deviceHandshakeOk:
                        self._handle_deviceHandshake(nDataBlock)
                    else:
                        nDataBlock=self._format_data_in(nDataBlock)
                        log.msg("Data recieved <<: ",nDataBlock,system="Driver")  
                        self.driver._handle_response(nDataBlock)
                    self.buffer=self.buffer[results.end():]
                    results=None
                    try:
                        results =self.regex.search(self.buffer)
                    except:
                        pass      
            
        except Exception as inst:
            print("error in serial",str(inst))
            
    def send_data(self,data,*args,**kwargs):  
        """
        Simple wrapper to send data over serial
        """    
        try:
            #log.msg("Data sent >>: ",data,system="Driver")
            self.transport.write(self._format_data_in(data))
            
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
        self.d.callback("arrgh")
        #log.msg("Device disconnectedsdfsdf",system="Driver") 
    
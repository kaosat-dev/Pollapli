from twisted.internet.protocol import Protocol, Factory

"""necessary workaround for win32 serial port bugs in twisted"""
import re, sys, itertools,time, logging,glob
if sys.platform == "win32":
    from pollapli.core.logic.patches._win32serialport import SerialPort
else:
    from twisted.internet.serialport import SerialPort
    
from twisted.internet import reactor, defer
from twisted.internet.task import LoopingCall
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.plugin import IPlugin
from zope.interface import implements,classProvides
from pollapli import ipollapli
from pollapli.exceptions import NoAvailablePort


class SerialWrapper(SerialPort):
      """wrapper around the twisted SerialPort class, for convenience and bugfix"""
      def __init__(self,*args,**kwargs):
          SerialPort.__init__(self,*args,**kwargs)
          self._tmp_data_buffer=[]
          self.deferred=defer.Deferred()
     
      def connectionLost(self,reason="connectionLost"):
          SerialPort.connectionLost(self,reason)
          self.deferred.callback("connection failure")

class SerialHardwareHandler(object):
    classProvides(IPlugin, ipollapli.IDriverHardwareHandler)
    blockedPorts=[]
    blackListPorts=["COM3"]
    availablePorts=[]

    def __init__(self,driver=None,protocol=None,speed=115200,*args,**kwargs):
        self.driver=driver
        self.serial=None    
        self.protocol=protocol(self.driver,*args,**kwargs)
        self.speed=speed
        self.port=None
        self.isConnected=False
        self.notMyPorts=[]
        self.setup_mode=False
           
            
    def send_data(self,command):
        self.protocol.send_data(command)
        
    def connect(self,port=None,*args,**kwargs):
        self.driver.connectionErrors=0
        log.msg("Connecting... to port:",port," at speed ",self.speed, " in mode ",self.driver.connectionMode, system="Driver",logLevel=logging.DEBUG)
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
                    self.serial.deferred.cancel()
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
                self.serial.deferred.addCallbacks(callback=self._connect,errback=self.connectionClosed)  
            except Exception as inst:          
                #log.msg("cricital error while (re-)starting serial connection : please check your driver speed,  cables,  and make sure no other process is using the port ",str(inst))
                self.driver.isConnected=False
                self.driver.connectionErrors+=1
                log.msg("failed to connect serial driver,because of error" ,inst,"attempts left:",self.driver.maxConnectionErrors-self.driver.connectionErrors,system="Driver")
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
                reactor.callLater(0.1,self.driver.deferred.errback,failure.Failure())
                

        
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
            #log.msg("Serial Ports on  system:",str(foundPorts),system="Driver",logLevel=logging.DEBUG)
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
        
        
    def pulseDTR(self,target):
        """emulation of the pulse DTR method"""
        if self.driver.isConnected:
            self.serial.setDTR(1)
            def _set_dtr(*args,**kwargs):
                self.serial.setDTR(0)
            reactor.callLater(0.5,_set_dtr)#not sure this would work as time.sleep replacement
            self.disconnect()


    """The next methods are at least partially deprecated and not in use """   
    def reset_seperator(self):
        self.regex = re.compile(self.seperator)
    
    def upload(self):
        avrpath="/home/ckaos/data/Projects/Doboz/pollapli/core/tools/avr"
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

        
            

    
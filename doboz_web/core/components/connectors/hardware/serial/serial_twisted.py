from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

from doboz_web.core.components.connectors.hardware.hardware_connector import HardwareConnector,HardwareConnectorEvents
from twisted.internet import protocol
from twisted.internet.serialport import SerialPort

class fixedSerialPort(SerialPort):
    def connectionLost(self, reason):
        SerialPort.connectionLost(self, reason)
        self.protocol.connectionLost(reason)

class BaseProtocolTest(protocol.Protocol):
    def dataReceived(self, data):
        try:
            block=""
            for c in data:
                block+=c
                if "\n" in block:
                    print(block)
                    block=""
        except Exception as inst:
            print("error in serial",str(inst))
            #self.state = getattr(self, 'state_'+self.state)(byte)
    def connectionLost(self, reason='connectionDone'):
        print (reason)

class SerialTwistedBasic():
    def __init__(self):
        self.port="Com4"
        self.speed=115200
        self.serial=fixedSerialPort(BaseProtocolTest(),self.port,reactor,baudrate=self.speed)
    def _toDict(self):
        return {"connector":{"type":"SerialTwistedBasic","params":{"speed":self.speed,"port":self.port},"link":{"rel":"connector"}}}
class SerialTwisted():
    blockedPorts=["COM3"]
    """A class level list of all , already in use serial ports: neeeded for multiplatform correct behaviour of serial ports """
    
    def __init__(self,port=None,isBuffering=True,seperator='\r\n',Speed=115200,bannedPorts=None,maxErrors=5,waitForAnswer=False):
        """ Inits the Serial port
        Arguments:
            port -- serial port to be used, if none, will scan for available ports and 
            select the first one.
            isBuffering -- should it buffer up recieved serial data.
            seperator --only used with isBuffering: if specified, buffered data
            will be split by this seperator : each time a seperator is found, all data
            up until it is dispatched via an event
            speed -- serial port speed
        """
        self.waitForAnswer=waitForAnswer
        self.pseudoName=pseudoName
        self.port=port
        self.speed=Speed
        
        self.seperator=seperator
        self.isBuffering=isBuffering
        self.buffer=""
        
        self.finished=Event()
        self.connectionRequested=False
        self.isStarted=False
        
        if bannedPorts:
            for bPort in bannedPorts:
                if not bPort in serial.blockedPorts:
                    serial.blockedPorts.append(bPort)

        self.serial=None
        self.lastCommand=""
        self.serial=fixedSerialPort(BaseProtocolTest(),self.port,reactor,baudrate=self.speed)
 
        
    def connect(self):
        if not self.isStarted:
            self.isStarted=True
        self.connectionRequested=True
        
    def disconnect(self):
        self.connectionRequested=False
        self.isConnected=False
        
    def _connect(self):
        """Port connection/reconnection procedure"""    
        try:
            serial.blockedPorts.remove(self.port)
        except:
            pass
        try:
            self.finished.clear()
        except:
            pass
        self.currentErrors=0
        self.port=None
        while self.port is None and self.currentErrors<5:
            try:      
                self.port=str(self.scan()[0])
                #TODO: weird: port init fails if following line is removed
                #print("Ports:",self.scan())
                SerialPlus.blockedPorts.append(self.port)        
                self.logger.critical("selecting port %s",str(self.port))
                self.serial=Serial(self.port,self.speed)
                
            except Exception as inst:
                self.logger.critical("cricital error while (re-)starting serial connection : please check your driver speed,  cables,  and make sure no other process is using the port ")
                self.currentErrors+=1
                time.sleep(self.currentErrors*5)
        if not self.port :
            self.tearDown()
        else:
            self.logger.info("(re)starting serial listener")
            if self.isConnected:
                self.events.reconnected(self,None)
            else:
                self.isConnected=True
                #self.start()
                
    def list_ports(self):
        """
        Return a list of ports
        """
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
                    #foundPorts.append((str(val[1])), str(val[0]))#returns tuple: simpleName, fullName
                    foundPorts.append(str(val[1]))
                except EnvironmentError:
                    break
        else:
            foundPorts= glob.glob('/dev/ttyUSB*')+ glob.glob('/dev/cu*')
        #self.logger.info("Serial Ports on  system:",+str(foundPorts))
        return foundPorts
    
    def scan(self):
        """scan for available ports.
        Returns a list of actual available ports"""
        available = []
        
        for port in self.list_ports():  
            if port not in SerialPlus.blockedPorts: 
                try:
                    s = Serial(port) 
                    available.append(s.portstr)
                    s.close()   
                except SerialException:
                    pass
        if s is None:
            self.logger.info("failed to get port")
     
        #for n in available:
        #    print " %s" % (n)
        return available
    
        
    
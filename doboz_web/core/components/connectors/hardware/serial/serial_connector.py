from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

from doboz_web.core.components.connectors.hardware.hardware_connector import HardwareConnector,HardwareConnectorEvents
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.serialport import SerialPort
import logging
import  time
import datetime
import logging
import os
import glob
import re
import sys
import itertools
import traceback

class PortWrapper(SerialPort):
      def __init__(self,*args,**kwargs):
          SerialPort.__init__(self,*args,**kwargs)
          self._tempDataBuffer=[]
      def writeSomeData(self,*args,**kwargs):
          pass
      #def connectionLost(self, reason):
      #  SerialPort.connectionLost(self, reason)
      #  self.protocol.connectionLost(reason)
        

class SerialConnector(HardwareConnector,DBObject):
    blockedPorts=["COM3"]
    BELONGSTO = ['node']
    def __init__(self,port=None,seperator='\r\n',isBuffering=True,speed=115200,bannedPorts=None,maxErrors=5,waitForAnswer=False,*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        HardwareConnector.__init__(self)
        self.serial=None    
        self.protocol=SerialTwisted()
        self.speed=speed
        self.seperator=seperator
        self.port="Com4"#port
        
    def __getattr__(self,attrname):
        try:
            if hasattr(self.protocol,attrname):
                return getattr(self.protocol,attrname)
        except:
            print("error in serial connector")
            
            
    def connect(self):
        try:
            self.serial=PortWrapper(self.protocol,"Com4",reactor,baudrate=self.speed)
        except Exception as inst:
            print("failed to connect to port",str(inst))
    def disconnect(self):
        #print("disconnecting")
        try:
            if self.serial:
                self.serial.loseConnection()
                self.serial=None
        except Exception as inst:
            print("error in serial disconnection",str(inst))
            
    def _toDict(self):
        return {"connector":{"type":"SerialTwisted","status":{"connected":self.protocol.isConnected},"type":None,"driver":None,"params":{"speed":self.speed,"port":self.port}},"link":{"rel":"connector"}}
   
    def set_driver(self,driver):
        """Sets what driver to use : a driver formats the data sent to the connector !!
        And may also contain additional settings for the connector"""
        self.driver=driver
        self.protocol.driver=driver
        self.seperator=driver.seperator
        self.speed=driver.speed
        self.reset_seperator()


class SerialTwisted(Protocol):
    
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
        self.logger = logging.getLogger("dobozweb.core.connectors.Serial")
        self.waitForAnswer=waitForAnswer
        
        
        self.seperator=seperator
        self.isBuffering=isBuffering
        self.buffer=""
        #self.finished=Event()
        self.connectionRequested=False
        self.isStarted=False
        
        if bannedPorts:
            for bPort in bannedPorts:
                if not bPort in serial.blockedPorts:
                    serial.blockedPorts.append(bPort)

        #self.serial=None
        self.lastCommand=""
        self.reset_seperator()
        self.driver=None
        self.nextCommand=None
        self.isConnected=False
        reactor.callLater(3,self._checkForCommands)
    def _toDict(self):
        return {"connector":{"type":"SerialTwisted","params":{"speed":self.speed,"port":self.port},"link":{"rel":"connector"}}}

    def reset_seperator(self):
        self.regex = re.compile(self.seperator)
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
    
    def connectionLost(self,reason="connectionLost"):
        print("serial port disconnected")
        self.isConnected=False
    
    def connectionMade(self):
        self._validate_connection(self)
        
    def dataReceived(self, data):
        try:
            self._handle_data(data)
        except Exception as inst:
            print("error in serial",str(inst))
    
    def _validate_connection(self,truc):
        #print("truc",truc)
        #self.protocol=truc
        self.isConnected=True
        print ("Arduino connected")
        
      
    def _checkForCommands(self):
        """
        cheap hack, for test
        """
        self.add_command("a")
        self.nextCommand="a"#self.driver.get_next_command()
        
        self._handle_data("")
        
        #reactor.callLater(10,self._checkForCommands)
        
    def _handle_data(self,data):
        if self.isConnected: 
            #print("recieved data",data)  
            newDataTreated=False
         
            
            
            #nextCommand=None
            if self.nextCommand:
                self.send_command(self.nextCommand)
            try:
                if data:
                    self.logger.debug("SERIAL GOT DATA %s", str(data))
                    newDataTreated=False
                    #in the case of buffering we fill the data buffer with all recieved data
                    #and as soon as we find a complete seperator, we split the substring ending with the seperator
                    #from the rest of the string and raise an event, sending the substring as message        
                if self.isBuffering:
                    self.logger.debug("serial buffering")
                    self.buffer+=str(data)
                    #if we have NOT already checked the last state of the data block
                    #then check it
                    if newDataTreated is False:
                        results=None
                        try:
                            results=self.regex.search(self.buffer)
                            
                        except Exception as inst:
                            self.logger.critical("Error while parsing serial data :%s",str(inst))
                        
                        while results is not None:
                            nDataBlock= self.buffer[:results.start()]
                            self.lastCommand=nDataBlock       
                            if self.driver:
                                nDataBlock=self.driver.handle_answer(nDataBlock)
                                if nDataBlock:
                                    if nDataBlock.answerComplete:
                                        #self.events.OnDataRecieved(self,nDataBlock)
                                        self.logger.critical("serial data block <<:  %s",(str(nDataBlock)))
                                        self.add_command("a")
                            else:
                                #self.events.OnDataRecieved(self,nDataBlock)
                                self.logger.critical("serial data block <<:  %s",(str(nDataBlock)))
                                #print("block",nDataBlock)
                                #self.add_command("a\n")
                               # self.add_command("b")
                                                 
                            self.buffer=self.buffer[results.end():]
                            results=None
                            try:
                                results =self.regex.search(self.buffer)
                            except:
                                pass      
                        newDataTreated=True
                else:
                        self.logger.debug("standard serial")
                        #self.events.OnDataRecieved(self,data)
            except Exception as inst:
                self.logger.critical("serial Error %s",str(inst))
                traceback.print_exc(file=sys.stdout)
    
    def add_command(self,command,*args,**kwargs):
        """
        Ennqueue/add a command , via the driver:
        """
       
        if self.driver:
            self.driver.handle_request(command,*args,**kwargs)
            #self.send_command(command)
        else:# without driver, no buffer , so just send the command
            self.send_command(command)
        self.logger.debug("new command appended: '%s'",str(command))
        
    def send_command(self,command,*args,**kwargs):  
        """
        Simple wrapper to send data over serial
        """    
        if self.isConnected: 
            try:
                self.logger.critical("serial data block >>: %s ",str(command))
                self.transport.write(command)
            except OSError:
                self.logger.critical("serial device not connected or not found on specified port")

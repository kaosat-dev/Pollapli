import sys,re,os,logging
from glob import glob
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

from doboz_web.core.components.drivers.driver import Driver,DriverManager,CommandQueueLogic
from doboz_web.core.components.drivers.serial.serial_hardware_handler import BaseSerialProtocol,SerialHardwareHandler


class compiler_uploader(object):
    def __init__(self,driver=None,arduinoPath=None,version=None,board=None,triggerMode=None,extraLib):
        self.driver=driver      
        self.env = Environment()
        self.platform = env['PLATFORM']
        
        
        self.avrBinPrefix=None
        self.avrDudeConf=None
        
        self.arduinoPath=arduinoPath or arduinoPath_default()  
        if self.arduinoPath==None:raise Exception("not defined or bad arduino path")
            
        self.arduinoBoard=board or os.environ.get('ARDUINO_BOARD', 'atmega328')
        self.arduinoVersion=version or 22 # Arduino 0022
        self.triggerMode= triggerMode  # use built-in pulseDTR() by default
        self.extraLib  =extraLib  # handy for adding another arduino-lib dir
        
        
        self.arduinoCore = os.path.join(self.arduinoPath,'hardware/arduino/cores/arduino')
        self.arduinoSkel = os.path.join(self.arduinoCore, 'main.cpp')
        self.arduinoConf = os.path.join(self.arduinoPath, 'hardware/arduino/boards.txt')
        
        # Some OSs need bundle with IDE tool-chain
        if platform == 'darwin' or platform == 'win32': 
            self.avrBinPrefix = os.path.join(self.arduinoPath, 'hardware/tools/avr/bin', 'avr-')
            self.avrDudeConf = os.path.join(self.arduinoPath, 'hardware/tools/avr/etc/avrdude.conf')
            
            
        self.arduinoLibs = []
        if self.extraLib is not None:
            self.arduinoLibs += [self.extraLib]
            self.arduinoLibs += [os.path.join(self.arduinoPath, 'libraries')]
        
    def arduinoPath_default(self):
        if self.platform == 'darwin':
            # For MacOS X, pick up the AVR tools from within Arduino.app
            self.arduinoPath = '/Applications/Arduino.app/Contents/Resources/Java'
        elif platform == 'win32':
            # For Windows, use environment variables.
            self.arduinoPath = os.environ.get('ARDUINO_HOME')
        else:
            # For Ubuntu Linux (9.10 or higher)
            self.arduinoPath = '/usr/share/arduino/' #'/home/YOU/apps/arduino-00XX/'
            self.avrBinPrefix= 'avr-'
            
    def check_boardName(self):
        """
         check given board name, ARDUINO_BOARD is valid one
        """
        ptnBoard = re.compile(r'^(.*)\.name=(.*)')
        boards = {}
        for line in open(self.arduinoConf):
            result = ptnBoard.findall(line)
            if result:
                boards[result[0][0]] = result[0][1]
        
        if not self.arduinoBoard in boards.keys():
            log.msg("ERROR! the given board name",self.arduinoBoard,"is not in the supported board list: currently supported devices are: ",\
                    " ".join(boards.keys()), "you can however edit", self.arduinoConf ,"to add a new board",logLevel=logging.CRITICAL )
            raise Exception("unsuported board type")
        
    def get_BoardConf(self,boardStr):
        """ retrieve configuration for current board"""
        ptn = re.compile(boardStr)
        for line in open(self.arduinoConf):
            result = ptn.findall(line)
            if result:
                return result[0]
        assert(False)
     
            
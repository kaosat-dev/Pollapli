import sys,re,os,logging,shutil
from glob import glob
from twisted.internet import protocol, utils, reactor,defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.internet import protocol

from doboz_web.core.logic.components.drivers.driver import Driver,DriverManager,CommandQueueLogic
#from doboz_web.core.logic.components.drivers.serial.serial_hardware_handler import BaseSerialProtocol,SerialHardwareHandler
from doboz_web.core.logic.tools.signal_system import SignalHander


#from doboz_web.dependencies.SCons.Environment import *



class SconsProcessProtocol(protocol.ProcessProtocol):
    def __init__(self,name=None,tmpDir=None,*args,**kwargs):
        self.name=name
        self.outPutBuff=""
        self.tmpDir=tmpDir
    def connectionMade(self):
        log.msg("SconsProcessProtocol connected")     
        #output = utils.getProcessOutput(self.prog)
       # output.addCallbacks(self.writeResponse, self.noResponse)
       
    def noResponse(self,result):
        print("no response")
    def writeResponse(self, resp):
        self.transport.write(resp)
        self.transport.loseConnection() 
        
    def outReceived(self, data):
        print("process recieved data",data)
        fieldLength = len(data) / 3
        lines = int(data[:fieldLength])
        words = int(data[fieldLength:fieldLength*2])
        chars = int(data[fieldLength*2:])
        self.transport.loseConnection()
        self.receiveCounts(lines, words, chars)
        
  
    def errReceived(self, data):
        print ("errReceived! with  bytes!" ,len(data),data)
        
#    def inConnectionLost(self):
#        print "inConnectionLost! stdin is closed! (we probably did it)"
        
#    def errConnectionLost(self):
#        log.msg("process",self.name, "  failed!",logLevel=logging.CRITICAL)
        
        
    def childDataReceived(self, childFD, data):
        log.msg("CompilerUpder ",self.name ," Data recieved",data,logLevel=logging.CRITICAL)
        if "Writing" in data:
            #print("writing in data")
            try:
                tmp=data.split(" ")
                percent=tmp[len(tmp)-2]
                print("Upload Percent:",percent)
            except Exception as inst:
                print("error",inst)
        
#    def processExited(self, reason):
#        log.msg("process ",self.name, " exited : total output:",self.outPutBuff,reason.value.exitCode,logLevel=logging.CRITICAL)
      
    def processEnded(self, status):
        log.msg("process",self.name, " ended",not bool(status.value.exitCode),logLevel=logging.CRITICAL)
       # print("process ended : total output:",self.outPutBuff)
        rc = status.value.exitCode
        if rc == 0:
            self.deferred.callback(self)
        else:
            self.deferred.errback(rc)
        if self.tmpDir is not None:
            if os.path.isdir(self.tmpDir):
                pass
                #shutil.rmtree(self.tmpDir)
                #os.rmdir(self.tmpDir)


class FirmwareInfo(object):pass

class ArduinoFirmwareInfo(FirmwareInfo):
    def __init__(self):
        self.arduinoPath=None
        self.avrBinPrefix=None
        self.avrDudeConf=None

class UploaderDownloader(object):
    
    def __init__(self):
        self.firmwareInfos={}

    


#from SCons.Environment import Environment
#from SCons.Builder import Builder
#
#import SCons.Action
#import SCons.Builder
#import SCons.Tool
#import SCons.Util
#import doboz_web.dependencies.SCons.Environment

#class compiler_uploader(object):
#    def __init__(self,driver=None,arduinoPath=None,version=None,board=None,triggerMode=None,extraLib=None,targetDir=None):
#        self.driver=driver      
#        self.env = Environment()
#        self.platform = self.env['PLATFORM']
#        self.targetDir=targetDir
#        self.target=None
#        self.realTarget=None
#        
#        self.avrBinPrefix=None
#        self.avrDudeConf=None
#        
#        self.arduinoPath=arduinoPath or self.arduinoPath_default()  
#        #temp hack
#        self.avrBinPrefix= 'avr-'
#        if self.arduinoPath==None:raise Exception("not defined or bad arduino path")
#            
#        self.arduinoBoard=board or os.environ.get('ARDUINO_BOARD', 'atmega328')
#        self.arduinoVersion=version or 22 # Arduino 0022
#        self.triggerMode= triggerMode  # use built-in pulseDTR() by default
#        self.extraLib  =extraLib  # handy for adding another arduino-lib dir
#        
#        
#        self.arduinoCore = os.path.join(self.arduinoPath,'hardware/arduino/cores/arduino')
#        self.arduinoSkel = os.path.join(self.arduinoCore, 'main.cpp')
#        self.arduinoConf = os.path.join(self.arduinoPath, 'hardware/arduino/boards.txt')
#        
#        # Some OSs need bundle with IDE tool-chain
#        if self.platform == 'darwin' or self.platform == 'win32': 
#            self.avrBinPrefix = os.path.join(self.arduinoPath, 'hardware/tools/avr/bin', 'avr-')
#            self.avrDudeConf = os.path.join(self.arduinoPath, 'hardware/tools/avr/etc/avrdude.conf')
#            
#            
#        self.arduinoLibs = []
#        if self.extraLib is not None:
#            self.arduinoLibs += [self.extraLib]
#        self.arduinoLibs += [os.path.join(self.arduinoPath, 'libraries')]
#            
#            #/home/ckaos/utilz/Progra/arduino-0022/hardware/arduino
#        log.msg("Arduino Compiler Uploader configured: Params: path",self.arduinoPath,"conf path",self.arduinoConf,logLevel=logging.CRITICAL)
#        
#    def arduinoPath_default(self):
#        if self.platform == 'darwin':
#            # For MacOS X, pick up the AVR tools from within Arduino.app
#            self.arduinoPath = '/Applications/Arduino.app/Contents/Resources/Java'
#        elif self.platform == 'win32':
#            # For Windows, use environment variables.
#            self.arduinoPath = os.environ.get('ARDUINO_HOME')
#        else:
#            # For Ubuntu Linux (9.10 or higher)
#            self.arduinoPath = '/usr/share/arduino/' #'/home/YOU/apps/arduino-00XX/'
#            self.avrBinPrefix= 'avr-'
#        return self.arduinoPath
#            
#    def check_boardName(self):
#        """
#         check given board name, ARDUINO_BOARD is valid one
#        """
#        ptnBoard = re.compile(r'^(.*)\.name=(.*)')
#        boards = {}
#        try:
#            for line in open(self.arduinoConf):
#                result = ptnBoard.findall(line)
#                if result:
#                    boards[result[0][0]] = result[0][1]
#        except IOError as inst:
#            log.msg("Failed to open arduino configuration file:",inst,logLevel=logging.CRITICAL)
#        
#        if not self.arduinoBoard in boards.keys():
#            log.msg("ERROR! the given board name",self.arduinoBoard,"is not in the supported board list: currently supported devices are: ",\
#                    " ".join(boards.keys()), "you can however edit", self.arduinoConf ,"to add a new board",logLevel=logging.CRITICAL )
#            raise Exception("unsuported board type")
#        else:
#            log.msg("Board name",self.arduinoBoard,"validated ",logLevel=logging.CRITICAL)
#        
#    def get_BoardConf(self,boardStr):
#        """ retrieve configuration for current board"""
#        ptn = re.compile(boardStr)
#        for line in open(self.arduinoConf):
#            result = ptn.findall(line)
#            if result:
#                return result[0]
#        assert(False)
#        
#    def do_stuff(self):
#        self.MCU = self.get_BoardConf(r'^%s\.build\.mcu=(.*)'%self.arduinoBoard)
#        self.F_CPU = self.get_BoardConf(r'^%s\.build\.f_cpu=(.*)'%self.arduinoBoard)
#     
#    def check_source_main(self):
#        """ methods checks for main source file :  There should be a file with the same name as the folder and with the extension .pde"""
#        self.target=os.path.basename(os.path.realpath(self.targetDir))
#        assert(os.path.exists(os.path.join(self.targetDir, self.target+'.pde')))
#        self.realTarget=os.path.join(self.targetDir, self.target+'.pde')
#        
#        log.msg("Target directory:",self.targetDir, "validated",logLevel=logging.CRITICAL)
#        
#    def set_flags(self):
#        cFlags = ['-ffunction-sections', '-fdata-sections', '-fno-exceptions',
#    '-funsigned-char', '-funsigned-bitfields', '-fpack-struct', '-fshort-enums',
#    '-Os', '-mmcu=%s'%self.MCU]
#        self.envArduino = Environment(CC = self.avrBinPrefix+'gcc', CXX = self.avrBinPrefix+'g++',
#    CPPPATH = ['build/core'], CPPDEFINES = {'F_CPU':self.F_CPU, 'ARDUINO':self.arduinoVersion},
#    CFLAGS = cFlags+['-std=gnu99'], CCFLAGS = cFlags, TOOLS = ['gcc','g++'])
#        
#       
#       
#    def _fnProcessing(self,target, source, env):
#        wp = open ('%s'%target[0], 'wb')
#        wp.write(open(self.arduinoSkel).read())
#        # Add this preprocessor directive to localize the errors.
#        sourcePath = str(source[0]).replace('\\', '\\\\');
#        wp.write('#line 1 "%s"\r\n' % sourcePath)
#        wp.write(open('%s'%source[0]).read())
#        wp.close()
#        return None   
#    
#    def _createBuilders(self):
#
#        self.envArduino.Append(BUILDERS ={'Processing':Builder(action = self._fnProcessing,suffix = '.cpp', src_suffix = '.pde')})
#        self.envArduino.Append(BUILDERS={'Elf':Builder(action=self.avrBinPrefix+'gcc '+'-mmcu=%s -Os -Wl,--gc-sections -o $TARGET $SOURCES -lm'%self.MCU)})
#        self.envArduino.Append(BUILDERS={'Hex':Builder(action=self.avrBinPrefix+'objcopy '+'-O ihex -R .eeprom $SOURCES $TARGET')})
#      
#    def _gatherSources(self):  
#        pass
#        
#    def addArduinoCore(self):
#        # add arduino core sources
#        self.envArduino.VariantDir('build/core', self.arduinoCore)
#        gatherSources = lambda x: glob(os.path.join(x, '*.c'))+\
#                glob(os.path.join(x, '*.cpp'))+\
#                glob(os.path.join(x, '*.S'))
#        self.core_sources = gatherSources(self.arduinoCore)
#        self.core_sources = filter(lambda x: not (os.path.basename(x) == 'main.cpp'), self.core_sources)
#        self.core_sources = map(lambda x: x.replace(self.arduinoCore, 'build/core/'), self.core_sources)
#        log.msg("added arduino core files: core sources:",self.core_sources,logLevel=logging.CRITICAL)
#        
#    def addArduinoLibs(self):
#        # add libraries
#        gatherSources = lambda x: glob(os.path.join(x, '*.c'))+\
#                glob(os.path.join(x, '*.cpp'))+\
#                glob(os.path.join(x, '*.S'))
#        
#        
#        libCandidates = []
#        ptnLib = re.compile(r'^[ ]*#[ ]*include [<"](.*)\.h[>"]')
#        for line in open (os.path.join(self.targetDir,self.target+'.pde')):
#            result = ptnLib.findall(line)
#            if result:
#                libCandidates += result
#                
#        log.msg("added arduino library candiddates: ",libCandidates,logLevel=logging.CRITICAL)
#        # Hack. In version 20 of the Arduino IDE, the Ethernet library depends
#        # implicitly on the SPI library.
#        if self.arduinoVersion >= 20 and 'Ethernet' in libCandidates:
#            libCandidates += ['SPI']
#            
#        self.all_libs_sources = []
#        index = 0
#        for orig_lib_dir in self.arduinoLibs:
#            lib_sources = []
#            lib_dir = 'build/lib_%02d'%index
#            self.envArduino.VariantDir(lib_dir, orig_lib_dir)
#            for libPath in filter(os.path.isdir, glob(os.path.join(orig_lib_dir, '*'))):
#                libName = os.path.basename(libPath)
#                if not libName in libCandidates:
#                    continue
#                self.envArduino.Append(CPPPATH = libPath.replace(orig_lib_dir, lib_dir))
#                lib_sources = gatherSources(libPath)
#                utilDir = os.path.join(libPath, 'utility')
#                if os.path.exists(utilDir) and os.path.isdir(utilDir):
#                    lib_sources += gatherSources(utilDir)
#                    envArduino.Append(CPPPATH = utilDir.replace(orig_lib_dir, lib_dir))
#                lib_sources = map(lambda x: x.replace(orig_lib_dir, lib_dir), lib_sources)
#                self.all_libs_sources += lib_sources
#            index += 1
#        log.msg("added arduino library files: lib sources:",self.all_libs_sources,logLevel=logging.CRITICAL)
#       
#    def do_convert(self):
#        """Convert sketch(.pde) to cpp"""
#        self.envArduino.Processing('build/'+self.target+'.cpp', 'build/'+self.target+'.pde')
#        self.envArduino.VariantDir('build', '.')
#        
#        self.sources = ['build/'+self.target+'.cpp']
#        self.sources += self.all_libs_sources
#        self.sources += self.core_sources   
#        log.msg("conversion pde to cpp done, source:",self.sources,logLevel=logging.CRITICAL)
#       
#        
#    def build(self):
#        """ Finally Build!!"""
#        objs = self.envArduino.Object(self.sources) #, LIBS=libs, LIBPATH='.')
#        self.envArduino.Elf(self.target+'.elf', objs)
#        self.envArduino.Hex(self.target+'.hex', self.target+'.elf')
#        
#        
#        
#        # Print Size
#        # TODO: check binary size
#        MAX_SIZE = self.get_BoardConf(r'^%s\.upload.maximum_size=(.*)'%self.arduinoBoard)
#        print ("maximum size for hex file: %s bytes"%MAX_SIZE)
#        self.envArduino.Command(None, self.target+'.hex', self.avrBinPrefix+'size --target=ihex $SOURCE')
#        
#        
#    def upload(self):
#        """ this will need be somehow tied into the driver system"""
#        # Reset
#        def pulseDTR(target, source, env):
#            import serial
#            import time
#            ser = serial.Serial(ARDUINO_PORT)
#            ser.setDTR(1)
#            time.sleep(0.5)
#            ser.setDTR(0)
#            ser.close()
#        
#        if RST_TRIGGER:
#            reset_cmd = '%s %s'%(RST_TRIGGER, ARDUINO_PORT)
#        else:
#            reset_cmd = pulseDTR
#        
#        #upload
#        UPLOAD_PROTOCOL = getBoardConf(r'^%s\.upload\.protocol=(.*)'%ARDUINO_BOARD)
#        UPLOAD_SPEED = getBoardConf(r'^%s\.upload\.speed=(.*)'%ARDUINO_BOARD)
#        
#        avrdudeOpts = ['-V', '-F', '-c %s'%UPLOAD_PROTOCOL, '-b %s'%UPLOAD_SPEED,
#            '-p %s'%MCU, '-P %s'%ARDUINO_PORT, '-U flash:w:$SOURCES']
#        if AVRDUDE_CONF:
#            avrdudeOpts += ['-C %s'%AVRDUDE_CONF]
#        
#        fuse_cmd = '%s %s'%(pathJoin(os.path.dirname(AVR_BIN_PREFIX), 'avrdude'),
#                             ' '.join(avrdudeOpts))
#        
#        upload = envArduino.Alias('upload', TARGET+'.hex', [reset_cmd, fuse_cmd]);
#        AlwaysBuild(upload)
#        
#    def tearDown(self):
#        """ Clean build directory"""
#        self.envArduino.Clean('all', 'build/')
            
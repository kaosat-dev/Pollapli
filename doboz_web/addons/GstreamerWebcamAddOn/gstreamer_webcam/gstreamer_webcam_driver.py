import uuid, logging,os,sys,time,shutil
from zope.interface import implements
from twisted.plugin import IPlugin
from doboz_web import idoboz_web 
from zope.interface import classProvides
from twisted.python import log,failure
from twisted.internet import reactor, defer
from doboz_web.exceptions import DeviceHandshakeMismatch,DeviceIdMismatch
from doboz_web.core.components.drivers.driver import Driver,DriverManager,CommandQueueLogic


from threading import Event, Thread
import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst

from twisted.internet import threads

        
class GstreamerWebcamHandler(object):
    classProvides(IPlugin, idoboz_web.IDriverHardwareHandler)
    avalailablePorts=[]
    avalailablePorts.append("port"+str(uuid.uuid4()))
    
    def __init__(self,driver,*args,**kwargs):
        self.driver=driver
        
        self.player = gst.Pipeline("testpipeline")
        bus = self.player.get_bus()
        bus.set_sync_handler(self.on_message)
        
        self.finished=Event() 
        self.filePath=None
        self.realPath=None

        self.recordingRequested=False
        self.recordingDone=True
        self.gstdriver="v4l2src"#gstdriver#
        
        
        """
        Configure the gstreamer pipeline element  
        """
        source=gst.element_factory_make(self.gstdriver,"webcam_source")  
            
        if self.gstdriver=="ksvideosrc":  
            source.set_property("device-index", 0)
        else:
            source.set_property("device","/dev/video1")
        #source.set_property("device-index", 0)
            
        ffmpegColorSpace=gst.element_factory_make("ffmpegcolorspace","ffMpeg1")
        ffmpegColorSpace2=gst.element_factory_make("ffmpegcolorspace","ffMpeg2")
        
        
        encoder=gst.element_factory_make("pngenc","png_encoder")
        fileSink= gst.element_factory_make("filesink", "file_destination")
        
        
        self.player.add(source,ffmpegColorSpace,ffmpegColorSpace2, encoder, fileSink)
        gst.element_link_many(source,ffmpegColorSpace,ffmpegColorSpace2, encoder, fileSink)
        
        
        
        
    def on_message(self, bus, message):
        """
        Gstreamer message handling
        """
        try:
            t = message.type       
            if t == gst.MESSAGE_EOS:
                log.msg("Recieved eos message",system="Driver",logLevel=logging.CRITICAL)
                self.recordingDone=True
            elif t == gst.MESSAGE_ERROR:
                self.player.set_state(gst.STATE_NULL)
                err, debug = message.parse_error()
                log.msg("in GStreamer pipeline ",err,debug,"disconnected ",system="Driver",logLevel=logging.CRITICAL)
                self.finished.set()
#                if self.driver.isConnected:
#                    self.isConnected=True
            elif t==gst.MESSAGE_SEGMENT_DONE:
                log.msg("Recieved segment done message ",system="Driver",logLevel=logging.CRITICAL)
            elif t== gst.MESSAGE_ELEMENT:
                log.msg("Recieved message element message ",system="Driver",logLevel=logging.CRITICAL)
            elif t== gst.MESSAGE_STATE_CHANGED:
                old, new, pending = message.parse_state_changed()
                log.msg("Recieved state changed message old",old,"new",new,system="Driver",logLevel=logging.CRITICAL)
            
            return gst.BUS_PASS
        except Exception as inst:
            log.msg("Error in messaging",inst,system="Driver",logLevel=logging.CRITICAL)
        finally:
            return gst.BUS_PASS
    
    def fetch_data(self): 
        self.recordingRequested=True

    def set_capture(self, filePath=None):    
        self.filePath=filePath
        self.newRecording=False
        log.msg("Starting capture to",filePath,system="Driver",logLevel=logging.CRITICAL)
        #self.player.get_by_name("file_destination").set_property("location", "tmp.png") 
        self.player.get_by_name("file_destination").set_property("location", self.filePath+"tmp.png")   
       
       
    def run(self,*args,**kwargs):
        """Main loop"""
        while not self.finished.isSet():

            if self.recordingDone and self.recordingRequested:  
                log.msg("Doing next snapshot",system="Driver",logLevel=logging.CRITICAL)
                #copy the temporary file to the final file name, to prevent display problems when the webserver tries to server a file currently beeing 
                #written by gstreamer fgh
#                if os.path.exists(self.filePath+"tmp.png"):
#                    shutil.copy2(self.filePath+"tmp.png", self.filePath+".png")
                self.player.set_state(gst.STATE_NULL)
                
                self.recordingRequested=False
                self.recordingDone=False
                self.player.set_state(gst.STATE_PLAYING)        
            else:
                time.sleep(0.1)
            if self.recordingDone:
                time.sleep(2)
                self.finished.set()
       
    def send_data(self,command):
        pass
        
    def connect(self,*args,**kwargs):
        self.driver.connectionErrors=0
        log.msg("Connecting... webcam:",system="Driver",logLevel=logging.DEBUG)
        self.driver.isConnected=True
        self.driver.isDeviceHandshakeOk=True
        self.driver.isDeviceIdOk=True
        self.driver.isConfigured=True 
       
        #self._connect(*args,**kwargs)    
    
        #hack !!
        self.set_capture("/home/ckaos/data/Projects/Doboz/doboz_web/data/environments/home/")
        self.fetch_data()
        threads.deferToThread(self.run, None).addBoth(self._runResult)
    
        self.driver.d.callback(None)   
    def _runResult(self,result):
        print("got run result",result)
        try:
            result.printTraceback()
        except:pass
    
    def reconnect(self):
        self.disconnect(clearPort=False)
        self._connect()
        
    def disconnect(self,clearPort=False):   
        self.driver.isConnected=False   
    
    def connectionClosed(self,failure):
        pass
    
        
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
    
    
    
    
        


class GstreamerWebcamDriver(Driver):
    """Class defining the components of the driver for a basic arduino,using attached firmware """
    classProvides(IPlugin, idoboz_web.IDriver) 
    TABLENAME="drivers"   
    def __init__(self,driverType="webcam",deviceType="webcam",deviceId="",connectionType="usb",options={},*args,**kwargs):
        """
        very important : the first two args should ALWAYS be the CLASSES of the hardware handler and logic handler,
        and not instances of those classes
        """
        Driver.__init__(self,GstreamerWebcamHandler,CommandQueueLogic,driverType,deviceType,deviceId,connectionType,options,*args,**kwargs)
        #self.hardwareHandler=ArduinoExampleHardwareHandler(self,*args,**kwargs)
        #self.logicHandler=CommandQueueLogic(self,*args,**kwargs)
        
        
        
        
#class GStreamerCam(Thread,HardwareConnector):
#    """
#    Gstreamer based webcam connector
#    """
#    def __init__(self,driver=None):
#        self.logger=logging.getLogger("dobozweb.core.GStreamerTest")
#        self.logger.setLevel(logging.CRITICAL)
#        Thread.__init__(self)
#        HardwareConnector.__init__(self)
#       
#        
#        
#        self.player = gst.Pipeline("testpipeline")
#        bus = self.player.get_bus()
#        bus.set_sync_handler(self.on_message)
#        
#        self.finished=Event() 
#        self.filePath=None
#        self.realPath=None
#
#        self.recordingRequested=False
#        self.recordingDone=True
#        self.driver=driver#"v4l2src"
#        
#        self.setup()
#      
#     
#    def on_message(self, bus, message):
#        """
#        Gstreamer message handling
#        """
#        try:
#            t = message.type
#          
#            if t == gst.MESSAGE_EOS:
#                self.logger.info("Recieved eos message")
#                #self.finished.set()
#                self.recordingDone=True
#            elif t == gst.MESSAGE_ERROR:
#                self.player.set_state(gst.STATE_NULL)
#                err, debug = message.parse_error()
#                self.logger.error("in GStreamer pipeline  %s: %s disconnected",err,debug)
#                if self.isConnected:
#                     self.events.disconnected(self,None)
#                else:
#                    self.isConnected=True
#            elif t==gst.MESSAGE_SEGMENT_DONE:
#                self.logger.info("Recieved segment done message")
#            elif t== gst.MESSAGE_ELEMENT:
#                self.logger.info("Recieved message element message")
#            elif t== gst.MESSAGE_STATE_CHANGED:
#                old, new, pending = message.parse_state_changed()
#                self.logger.info("Recieved state changed message OLD: %s NEW %s",old,new)
#            
#            return gst.BUS_PASS
#        except Exception as inst:
#            self.logger.critical("Error in messaging: %s",str(inst))
#        finally:
#            return gst.BUS_PASS
#
#        
#    def setup(self):
#        """
#        Configure the gstreamer pipeline element  
#        """
#        source=gst.element_factory_make(self.driver,"webcam_source")  
#            
#        if self.driver=="ksvideosrc":  
#            source.set_property("device-index", 0)
#            
#        ffmpegColorSpace=gst.element_factory_make("ffmpegcolorspace","ffMpeg1")
#        ffmpegColorSpace2=gst.element_factory_make("ffmpegcolorspace","ffMpeg2")
#        
#        clockoverlay=gst.element_factory_make("clockoverlay","clock_overlay") 
#        clockoverlay.set_property("halign", "right")
#        clockoverlay.set_property("valign", "bottom")
#        
#        
#        encoder=gst.element_factory_make("pngenc","png_encoder")
#        fileSink= gst.element_factory_make("filesink", "file_destination")
#        
#        
#        self.player.add(source,ffmpegColorSpace,clockoverlay,ffmpegColorSpace2, encoder, fileSink)
#        gst.element_link_many(source,ffmpegColorSpace,clockoverlay,ffmpegColorSpace2, encoder, fileSink)
#       
#    
#    def run(self):
#        """Main loop"""
#        while not self.finished.isSet():
#            if self.recordingDone and self.recordingRequested:  
#                self.logger.info("Doing next snapshot")
#                #copy the temporary file to the final file name, to prevent display problems when the webserver tries to server a file currently beeing 
#                #written by gstreamer 
#                if os.path.exists(self.filePath+"tmp.png"):
#                    shutil.copy2(self.filePath+"tmp.png", self.filePath+".png")
#                self.player.set_state(gst.STATE_NULL)
#                
#                self.recordingRequested=False
#                self.recordingDone=False
#                self.player.set_state(gst.STATE_PLAYING)        
#            else:
#                time.sleep(0.1)
#         
#    def fetch_data(self): 
#        self.recordingRequested=True
#
#    def set_capture(self, filePath):    
#        self.filePath=filePath
#        self.newRecording=False
#        self.logger.critical("Starting capture to  %s",filePath)
#        self.player.get_by_name("file_destination").set_property("location", self.filePath+"tmp.png")
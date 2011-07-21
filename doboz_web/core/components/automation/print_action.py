from __future__ import division
import os,time,logging
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure

from doboz_web.core.file_manager import FileManager
from doboz_web.exceptions import InvalidFile
from doboz_web import idoboz_web
from doboz_web.core.signal_system import SignalHander
from doboz_web.core.tools.gcode_parser import GCodeParser
#from doboz_web.core.components.automation.task import ActionStatus

class ActionStatus(object):
    def __init__(self,progressIncrement=0,progress=0):
        self.isStarted=False
        self.isPaused=False
        self.progressIncrement=progressIncrement
        self.progress=progress
        self.startTime=0       
        self.totalTime=0
        
    def start(self): 
        self.isStarted=True
        self.isPaused=False
        self.progress=0
        self.startTime=time.time()
            
    def stop(self):
        self.isPaused=True#should it be paused or should is running be set  to false?
        self.isStarted=False
        
    def update_progress(self,value=None,increment=None):
        if value:
            self.progress=value
        elif increment:
            self.progress+=increment
        else:
            self.progress+=self.progressIncrement
            
        self.totalTime=time.time()-self.startTime
        if self.progress==100:
            self.isPaused=True#should it be paused or should is running be set  to false?
            self.isStarted=False
        
    def _toDict(self):
        return {"status":{"isStarted":self.isStarted,"isPaused":self.isPaused,"progress":self.progress,\
                          "progressIncrement":self.progressIncrement,"timeStarted":self.startTime,"timeTotal":self.totalTime}}
 

class PrintAction(DBObject): 
    """"
    should a printstep action return a specific data structure ? for exam^ple :
    - 3D data from parsing
    - treated gcode ?
     should  things like the gcode history be stored in the action or the task (i say the task,
     since an action is not supposed to be aware of the tasks global state
     -vectors/positions should be normalized
     things that seem to belong in the task,not the action:
        if z!=self.currentLayerValue:
                                self.currentLayer+=1
                                self.currentLayerValue=z
                                self.pointCloud.add_point(Point(x/20,y/20,z/20)) 
    """
    BELONGSTO   = ['task']
    TABLENAME ="actions" 
    
    def __init__(self,actionType="print",parentTask=None,printFile=None,fileType="gcode",params={},*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.actionType=actionType
        
        self.parentTask=parentTask
        self.params=params
        self.status=ActionStatus()
        
        self.fileType=fileType
        self.printFileName=printFile
        self.printFilePath=None  
        self.printFile=None
          
        self.line=""
        self.lineIndex=0
        self.lineCount=0
        self.curentLine=None
        self.fileParser=None
        self.startTime=0
        
        if fileType=="gcode":
            self.fileParser=GCodeParser()
        
        
        #for chaining ?
        self.nextTask=None
     
    def setup(self,params={},*args,**kwargs):
        self.printFileName=params.get("file")
        self.fileType=params.get("fileType")
        self.params=params 
        self.printFilePath=os.path.join(FileManager.rootDir,"printFiles",self.printFileName)   
        if self.fileType=="gcode":
            self.fileParser=GCodeParser()
        log.msg("Print action setup: file",self.printFileName,"type",self.fileType,"filepath",self.printFilePath,\
                "fileParser",self.fileParser,system="Action",logLevel=logging.DEBUG)
       
        
    def _toDict(self):
        return {"task":{"id":self.id,"name":self.name,"description":self.description,"status":self.status._toDict(),"link":{"rel":"task"}}}
  
    
    @defer.inlineCallbacks    
    def start(self):
        if not self.status.isStarted:
            """only allow start if not already started"""
            self.status.start()
            def do_start(result):
                self.startTime=time.time()    
                self.printFile=file(self.printFilePath,"r")
                self._do_step(self.printFile).addBoth(self._step_done) 
            yield self._getLineCount().addCallback(do_start)
         
    def pause(self):
        d=defer.Deferred()
        def do_pause_unpause(result):
            if self.status.isPaused:
                """was paused, unpausing"""
                self.status.isPaused=False
                self._do_step(self.printFile).addBoth(self._step_done)
            else:
                """was not paused, pausing"""
                self.status.isPaused=False
                
        d.addCallback(do_pause_unpause)
        reactor.callLater(0,d.callback,None)
        return d
    
    def stop(self):
        d=defer.Deferred()
        def do_stop(result):
            self.status.stop()
            self.printFile.close()
            return self.status
        
        d.addCallback(do_stop)
        reactor.callLater(0,d.callback,None)
        return d
    
    def _getLineCount(self):
        d=defer.Deferred()
        def lineCountDone(result,*args,**kwargs):
            if isinstance(result,failure.Failure):
                log.msg("Failed to get lines in file",logLevel=logging.CRITICAL)
                raise InvalidFile()
            else:
                self.lineCount=result
                self.status.progressIncrement=float(1/self.lineCount)*100
                log.msg("Total Lines in file",self.lineCount,logLevel=logging.INFO)
                
        def countLines(result):
            lineCount=0
            f=file(self.printFilePath,"r")
            for line in f:
                lineCount+=1
            f.close()
            return lineCount
        
        d.addCallback(countLines)
        d.addBoth(lineCountDone)
        reactor.callLater(0.1,d.callback,None)
        return d
    
    def _data_recieved(self,data,*args,**kwargs):
        log.msg("Print action recieved ",data,args,kwargs,logLevel=logging.DEBUG)
        if self.status.isStarted:
            self._do_step(self.printFile).addBoth(self._step_done)
            
    def _step_done(self,result,*args,**kwargs):      
        """gets called when an actions is finished """            
        if isinstance(result,failure.Failure):
            self.printFile.close()
            self.status.update_progress(value=100)  
            log.msg("Finished print action. Status:",self.status._toDict(),system="PrintAction",logLevel=logging.CRITICAL)
            #raise event "action finished" 
            self.parentTask.send_signal("action"+self.id+".actionDone")    
        else:
            line,position=result
            self.lineIndex+=1
            self.status.update_progress()
            log.msg("Finished print action step. Status:",self.status._toDict(),system="PrintAction",logLevel=logging.CRITICAL)

            if self.lineIndex%1000==0:
                log.msg("1000 steps done in",time.time()-self.startTime,"s",logLevel=logging.CRITICAL)
                self.startTime=time.time()
            
         
    def _do_step(self,printFile,*args,**kwargs):
        """
        gets the next line in the gCode file, sends it via serial
        and then increments the currentLine counter
        this action returns a tuple of the current line + the parsed position
        
        The sending of data to the driver might need to be moved elsewhere
        * we also need to specify WHO sent the request to the driver,
        * channels need to have some notion of id ? 
        * what of these ? 
            * self.connector.add_command(line,answerRequired=True)          
            * send_command(self,data,sender=None):
        """
        d=defer.Deferred()
        def parseAndSend(printFile):
                if self.status.isStarted and not self.status.isPaused:
                    line=printFile.next()      
                    if line!= "":    
                        line=line.replace('\n','')
                        self.parentTask.send_signal(self.parentTask.driverChannel+".addCommand",line,True)
                        log.msg("Task",self.id,"sent signal addCommand to node's driver",logLevel=logging.DEBUG)
                        pos=self.fileParser.parse(line)  
                    return (line,pos)

        d.addCallback(parseAndSend)
        reactor.callLater(0,d.callback,printFile) 
        return d
    
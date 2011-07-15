from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from doboz_web.core.file_manager import FileManager
#from doboz_web.exceptions import UnknownDriver,NoDriverSet,DeviceIdMismatch
from doboz_web import idoboz_web
from doboz_web.core.signal_system import SignalHander

class ActionStatus(object):
    def __init__(self):
        self.isStarted=False
        self.isPaused=False

class PrintAction(): 
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
    TABLENAME="actions" 
    
    def __init__(self,printFile=None,fileType="GCode",*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.params=[printFile,fileType]
        self.printFileName=printFile
        self.printFilePath=os.path.join(FileManager.rootDir,"printFiles",printFileName)      
        self.line=""
        self.lineIndex=0
        self.lineCount=0
        self.curentLine=None
        self.fileParser=None
        
        if fileType=="GCode":
            self.fileParser=GCodeParser()
        self.signalHandler=SignalHander("PrintAction")   
        #there needs to be a way to bind a specific signal to a specific function call
        
    def setup(self):
        pass
        
    def start(self):
        self._getLineCount()
        self.printFile=file(self.printFilePath,"r")
        self._do_step(printFile).addCallback(_step_done)
        #reactor.callLater(0,self.do_step,self.printFile)  
    
    def stop(self):
        pass
    
    def pause(self):
        pass
    
    def _getLineCount(self):
        d=defer.Deferred()
        def countLines(result):
            f=file(self.printFilePath,"r")
            for line in f:
                self.lineCount+=1
            f.close()
        d.addCallback(countLines)
        reactor.callLater(0.2,d.callback)
        return d
        
    def _step_done(self,result):
        """gets called when an actions is finished """
        self.totalTime+=time.time()-self.startTime
        self.startTime=time.time()
                
        if isinstance(result,Failure):
            self.progress=100
        else:
            line,position=result
            self.lineIndex+=1
            """progress need to be computed base on the number of actions needed for this task to complete"""
            self.progress+=self.progressFraction
            #self._do_action_step()
        #need to set status somewhere
        #self.status="F"
        #self.events.OnExited(self,"OnExited")
                 
    def _do_step(self,printFile,*args,**kwargs):
        """
        gets the next line in the gCode file, sends it via serial, updates the logFile
        and then increments the currentLine counter
        
        The sending of data to the driver might need to be moved elsewhere
        * we also need to specify WHO sent the request to the driver,
        * channels need to have some notion of id ? 
        * what of these ? 
            * self.connector.add_command(line,answerRequired=True)          
            * send_command(self,data,sender=None):
        """
        d=defer.Deferred()
        def parseAndSend(printFile):
            try:
                line=printFile.next()      
                if line!= "":    
                    self.signalHandler.send_message(self,"action.print.plugged in",{"data":line})                              
                    #self.logger.debug("Sent command "+ line)
                    pos=self.fileParser.parse(line)  
                """this action returns a tuple of the current line + the parsed position"""
                return (line,pos)
            except StopIteration:
                print("at end of file")
        reactor.callLater(0,parseAndSend,printFile) 
        return d
    

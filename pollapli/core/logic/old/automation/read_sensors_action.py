import os,time,logging
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure


from pollapli import ipollapli
from pollapli.core.logic.tools.signal_system import SignalHander
from pollapli.core.logic.components.automation.task import ActionStatus

class ReadSensorsAction(DBObject): 
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
    
    def __init__(self,actionType="sensoread",sensorsToRead=[],params={},*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.actionType=actionType
        
        self.parentTask=parentTask
        self.params=params
        self.status=ActionStatus()
        
        #for chaining ?
        self.nextTask=None
     
    def setup(self,params={},*args,**kwargs):
        self.print_file_name=params.get("file")
        self.file_type=params.get("file_type")
        self.params=params
        
    def _toDict(self):
        return {"task":{"id":self.id,"name":self.name,"description":self.description,"status":self.status._toDict(),"link":{"rel":"task"}}}
  
    
    @defer.inlineCallbacks    
    def start(self):
        if not self.status.is_started:
            """only allow start if not already started"""
            self.status.start()
            def do_start(result):
                self._do_step().addBoth(self._step_done) 
            
         
    def pause(self):
        d=defer.Deferred()
        def do_pause_unpause(result):
            if self.status.is_paused:
                """was paused, unpausing"""
                self.status.is_paused=False
                self._do_step().addBoth(self._step_done)
            else:
                """was not paused, pausing"""
                self.status.is_paused=False
                
        d.addCallback(do_pause_unpause)
        reactor.callLater(0,d.callback,None)
        return d
    
    def stop(self):
        d=defer.Deferred()
        def do_stop(result):
            self.status.stop()
            return self.status
        
        d.addCallback(do_stop)
        reactor.callLater(0,d.callback,None)
        return d
    
    def _data_recieved(self,data,*args,**kwargs):
        log.msg("Print action recieved ",data,args,kwargs,logLevel=logging.DEBUG)
        if self.status.is_started:
            self._do_step().addBoth(self._step_done)
            
    def _step_done(self,result,*args,**kwargs):      
        """gets called when an actions is finished """            
        if isinstance(result,failure.Failure):
            self.print_file.close()
            self.status.update_progress(value=100)  
            log.msg("Finished print action. Status:",self.status._toDict(),system="PrintAction",logLevel=logging.CRITICAL)
            #raise event "action finished" 
            self.parentTask._send_signal("action"+self.id+".actionDone")    
        else:
            line,position=result
            self.line_index+=1
            self.status.update_progress()
            log.msg("Finished print action step. Status:",self.status._toDict(),system="PrintAction",logLevel=logging.CRITICAL)

            if self.line_index%1000==0:
                log.msg("1000 steps done in",time.time()-self.start_time,"s",logLevel=logging.CRITICAL)
                self.start_time=time.time()
            
         
    def _do_step(self,print_file,*args,**kwargs):
        d=defer.Deferred()
        def parse_and_send(print_file):
                if self.status.is_started and not self.status.is_paused:
                    line=print_file.next()      
                    if line!= "":    
                        line=line.replace('\n','')
                        self.parentTask._send_signal(self.parentTask.driverChannel+".addCommand",line,True)
                        log.msg("Task",self.id,"sent signal addCommand to node's driver",logLevel=logging.DEBUG)
                        pos=self.file_parser.parse(line)  
                    return (line,pos)

        d.addCallback(parse_and_send)
        reactor.callLater(0,d.callback,print_file) 
        return d

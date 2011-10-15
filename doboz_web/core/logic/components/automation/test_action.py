from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure

class UpdateSensorDataAction(DBObject):
    BELONGSTO   = ['task']
    TABLENAME ="actions" 
    
    def __init__(self,actionType="test",targetNode,targetComponent=None,targetVariable=None,*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.targetNode=targetNode
        self.targetComponents=targetComponent
        self.targetVariable=targetVariable
        self.actionType=actionType
        
    def start(self):
        pass
    def stop(self):
        pass
    def pause(self):
        pass
    
    def _data_recieved(self,data,*args,**kwargs):
        log.msg("action recieved ",data,args,kwargs,logLevel=logging.DEBUG)
        if self.status.isStarted:
            self._do_step().addBoth(self._step_done)
            
    def _step_done(self,result,*args,**kwargs):      
        """gets called when an actions is finished """            
        if isinstance(result,failure.Failure):
            self.status.update_progress(value=100)  
            log.msg("Finished print action. Status:",self.status._toDict(),system="Action",logLevel=logging.CRITICAL)
            self.parentTask.send_signal("action"+self.id+".actionDone")    
        else:
        
            self.status.update_progress()
            log.msg("Finished print action step. Status:",self.status._toDict(),system="Action",logLevel=logging.CRITICAL)

         
    def _do_step(self,*args,**kwargs):
        """
        """
        d=defer.Deferred()
        def thingy(*args,**kwargs):
            self.targetVariable.get()
        
        d.addCallback()
        reactor.callLater(0,d.callback,None) 
        return d


    
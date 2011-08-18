class Task_old(DBObject):
    BELONGSTO   = ['environment']      
    """
    Base class for tasks
    """
    def __init__(self,name="task",description="a task",taskType="task",options={},*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.logger=logging.getLogger("dobozweb.core.components.automation.task")
        
        self.name=name
        self.description=description
        self.taskType=taskType
        self.params=options
        
        """progress need to be computed base on the number of actions needed for this task to complete"""
        self.status=TaskStatus()
        self.actions=None
        self.signalHandler=None
        #self.signalhandler=SignalHander("task",[("driver.dataRecieved",Any,[self.__call__])])

    def __call__(self,*args,**kwargs):
        pass
        
    def _toDict(self):
        return {"task":{"id":self.id,"name":self.name,"description":self.description,"status":self.status._toDict(),"link":{"rel":"task"}}}
    
    @defer.inlineCallbacks  
    def setup(self):
        self.signalChannelPrefix=str((yield self.environment.get()).id)
        self.signalChannel="environment"+self.signalChannelPrefix+".task"+str(self.id)
        self.driverChannel="environment"+self.signalChannelPrefix+".driver"
        self.signalHandler=SignalHander(self.signalChannel)
        log.msg("Task setup sucessfully",system="Task",logLevel=logging.CRITICAL) 
    
    @defer.inlineCallbacks 
    def start(self):
        if self.actions:
            yield self.actions.start()  
            defer.returnValue(True)
        else:
            defer.returnValue(False)  
            
    @defer.inlineCallbacks       
    def pause(self):
        if self.actions:
            yield self.actions.pause()  
            defer.returnValue(True)
        else:
            defer.returnValue(False)
    
    @defer.inlineCallbacks
    def stop(self):
        if self.actions:
            yield self.actions.stop()  
            defer.returnValue(True)
        else:
            defer.returnValue(False)  
    
    def send_signal(self,signal="",data=None,out=False):
        self.signalHandler.send_message(signal,{"data":data},out)
   
    def _data_recieved(self,data,*args,**kwargs):
        self.actions._data_recieved(*args,**kwargs)
   
    def set_action(self,action):
        """Sets the first action"""
        self.actions=action
        #self.signalHandler.add_handler2(handler=self.actions._data_recieved,signal=self.driverChannel+".dataRecieved")
        self.signalHandler.add_handler(handler=self.actions._data_recieved,signal="dataRecieved")
        
    def check_conditions(self):
        """
        method in charge of verifying all of the tasks conditions
        for a task to start/continue running, all of its conditions must evaluate to True 
        """
        [condtion.check() for condition in self.conditions]
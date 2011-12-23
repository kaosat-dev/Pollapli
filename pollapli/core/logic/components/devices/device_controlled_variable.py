class DeviceControlledVariable(object):
    def __init__(self, device, name, value, type, unit, defaultValue=None, historyStore=None, historyLength=None, implicitSet=False, channels=[]):
        """
        defaultValue: base value to reset the variable to during a reset operation
        historyPersistance/store : Where will the data be stored None, memory, database, file
        historyLength: how much old values do we store: None, all, or any numeric value
        """
        self.device = device
        self.name = name
        self.value = value
        self.defaultValue = defaultValue or value
        self.targetValue = None
        self.type = type
        
        self.historyStore = historyStore
        self.history = None
        if historyStore == 'memory':
            self.history = []
            self.historyLength = historyLength
            self.historyIndex = 0
        elif historyStore =='db':
            pass
        elif historyStore=='file':
            pass
        
        self.implicitSet=implicitSet
        """This defines the fact, that a "set" operation changes the current value to the target value
         even WITHOUT the need for checking it with a sensor read: we TRUST the remote device to do the 
         work correctly
        """
        self.attachedSensors={}
        self.attachedActors={}
        
        self._commanqueue=DeferredQueue()
        self.commandqueue=deque()
         
    def attach_sensor(self,sensor,channel=None,*args,**kwargs):
        realChannel=None
        if channel:
            realChannel=channel
        else:
            """if no channel was defined , the sensor needs to be attached to the reserved channel "root",
            which means, the variable itself"""
            realChannel="root"    
            
        self.attachedSensors[realChannel]=sensor
        if sensor.channel is None:
            sensor.channel=realChannel
    
    def attach_sensors(self,sensors,*args,**kwargs):
        """in this case, sensors is a list of tupples in the form : (sensor,channel)"""
        for sensor,channel in sensors:
            self.attach_sensor(sensor, channel)
            
    def attach_actor(self,actor,channel=None,*args,**kwargs):
        realChannel=None
        if channel:
            realChannel=channel
        else:
            """if no channel was defined , the actor needs to be attached to the reserved channel "root",
            which means, the variable itself"""
            realChannel="root"    
        self.attachedActors[realChannel]=actor
        if actor.channel is None:
            actor.channel=realChannel
    
    def attach_actors(self,actors,*args,**kwargs):
        """in this case, actors is a list of tupples in the form : (actor,channel)"""
        for actor,channel in actors:
            self.attach_actor(actor, channel)
    def attach_both(self,sensors,actors):
        self.attach_actors(actors)
        self.attach_sensors(sensors)
        
    def get(self,saveToHistory=False,sender=None):
        command=Command(type="get",sender=sender,params={"save":saveToHistory})
        self.commandqueue.append(command)
        #self.commanqueue.put(command)
        print("lskjfsdlfkj")
        
       # self.node.driver.teststuff(self,None,self._updateConfirmed)
        #self.node.query_driver(self)
       
        
 #       self.node.driver.variable_get(self)
#        try:
#            getattr(self.node.driver,"get_"+self.name)(value)
#        except Exception as inst:
#            log.mg("Node's driver does not have the request feature",system="Node",logLevel=logging.CRITICAL)
        return command.d
    
    def set(self,value,relative=False,params=None,sender=None):
        """ setting is dependent on the type of  variable
        This is a delayed operation: set just initiates the chain of events leading to an actual update
        it calls the driver set method + this variables type :ie  for a position: set_name_position
        """
        if relative:
            #all variable types need to support adding
            self.targetValue+=value
        else:
            self.targetValue=value
        try:
            getattr(self.node.driver,"set_"+self.name)(value)
        except Exception as inst:
            log.mg("Node's driver does not have the request feature",system="Node",logLevel=logging.CRITICAL)
   
    def enqueue(self,value):
        pass
    
    def refresh(self):
        """
        This is a delayed operation: set just initiates the chain of events leading to an actual update
        """
        pass
    
    def reset(self,value=None):
        if value is not None:
            self.value=value
        else:
            self.value=self.defaultValue
    
    def _updateConfirmed(self,value=None,*args, **kwargs):
        """to be called after a sucessfull get or set with implicit trust"""
     
        originalCmd=self.commandqueue.pop()
       # print("in update confirmed: command",originalCmd)
        
        try:
            value=self.type(value)
        except Exception as inst:
            print("failed to cast update data for variable",inst)
            
        log.msg("Variable update confirmed: new value is ",value,logLevel=logging.DEBUG)
        
        if self.implicitSet or originalCmd.type=="get":
            self.value=value
               
        if self.historyStore=='memory':
            self.historyIndex+=1
            if self.historyIndex>self.historyLength:
                self.historyIndex=0
            self.history[self.historyIndex]=value
        elif self.historyStore=='db':
            pass
            Reading(self.value).save()
        
        
        reactor.callLater(0,originalCmd.d.callback,self.value)
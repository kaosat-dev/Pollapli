import logging,ast,time
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from zope.interface import Interface, Attribute,implements
from twisted.plugin import IPlugin,getPlugins
from twisted.internet.interfaces import IProtocol
from twisted.internet.protocol import Protocol


from pollapli.exceptions import UnknownDriver,NoDriverSet,DeviceIdMismatch,DeviceNotConnected
from pollapli import ipollapli

#from pollapli.core.logic.components.updates.update_manager import UpdateManager




class EndPoint(object):
    def __init__(self,id,type=None,port=None,infos=[],getter=True,funct=None):
        self.id=id
        self.type=type
        self.port=port
        self.infos=infos
        self.getter=getter
        self.funct=funct
 
    def set(self,value):
        if self.getter:
            raise Exception("this is a getter endpoint")
        self.funct(self.port,value)
    def get(self):
        if not self.getter:
            raise Exception("this is a setter endpoint")
        self.funct(self.port)
    

    
        
class Driver(DBObject):
    """
    Driver class: higher level handler of device connection that formats outgoing and incoming commands
     according to a spec before they get sent to the lower level connector.
     It actually mimics the way system device drivers work in a way.
     You can think of the events beeing sent out by the driver (dataRecieved etc) as interupts of sorts
     
      ConnectionModes :
        0:setup
        1:normal
        2:setId
        3:forced: to forcefully connect devices which have no deviceId stored 
     
    Thoughts for future evolution
    each driver will have a series of endpoints or slots/hooks, which represent the actual subdevices it handles
    for example for reprap type devices, there is a "position" endpoint (abstract), 3 endpoints for the 
    cartesian bot motors , at least an endpoint for head temperature , one for the heater etc
    or this could be in a hiearchy , reflecting the one off the nodes:
    variable endpoint : position, and sub ones for motors
    """
    BELONGSTO = ['node']
    EXPOSE=["driverType","deviceType","deviceId","options","isConnected","isPluggedIn"]
    
    def __init__(self,deviceType="",connectionType="",hardwareHandlerKlass=None,logicHandlerKlass=None,protocol=None,options={},*args,**kwargs):    
        self.driverType=self.__class__.__name__.lower()
        self.deviceType=deviceType
        self.connectionType=connectionType
        self.options=options
        self.protocol=protocol
        self.hardwareHandlerKlass=hardwareHandlerKlass
        self.logicHandlerKlass=logicHandlerKlass
        DBObject.__init__(self,**kwargs)
               

        self.deviceId=None
        """will be needed to identify a specific device, as the system does not work base on ports"""
     
        self._signalDispatcher=None 
        self.signalChannelPrefix=""
        self.signalChannel=""
        
        self.isConfigured=False#when the port association has not been set
        self.isDeviceHandshakeOk=False
        self.isDeviceIdOk=False
        self.isConnected=False
        self.isPluggedIn=False
        self.autoConnect=False#if autoconnect is set to true, the device will be connected as soon as a it is plugged in and detected
        
       
        self.connectionErrors=0
        self.maxConnectionErrors=2
        self.connectionTimeout=4
         
        self.connectionMode=1
        self.d=defer.Deferred()
        
        """just for future reference : this is not implemented but would be a declarative way to 
        define the different "configuration steps" of this driver"
        *basically a dictonary with keys beeing the connection modes, and values a list of strings
        representing the methods to call
        *would require a "validator"  of sorts (certain elements need to be mandatory : such as the
        validation/setting of device ids
        """
        configSteps={}
        configSteps[0]=["_handle_deviceHandshake","_handle_deviceIdInit"]
        configSteps[1]=["_handle_deviceHandshake","_handle_deviceIdInit","some_other_method"]
        
        #just a test
        self._signalDispatcher=SignalHander("driver_manager")
        
        """for exposing capabilites"""
        self.endpoints=[]
        
        
    def afterInit(self):
       
        """this is a workaround needed when loading a driver from db"""
        try:
            if not isinstance(self.options,dict):
                self.options=ast.literal_eval(self.options)
        except Exception as inst:
            log.critical("Failed to load driver options from db:",inst,system="Driver",logLevel=logging.CRITICAL)

    
    @defer.inlineCallbacks    
    def setup(self,*args,**kwargs):  
        self.hardwareHandler=self.hardwareHandlerKlass(self,self.protocol,**self.options)
        self.logicHandler=self.logicHandlerKlass(self,**self.options)  
        
        
        node= (yield self.node.get())
        env= (yield node.environment.get())
        self.signalChannelPrefix="environment_"+str(env.id)+".node_"+str(node.id)

        self._signalDispatcher.add_handler(handler=self.send_command,signal="addCommand")
        log.msg("Driver of type",self.driverType ,"setup sucessfully",system="Driver",logLevel=logging.INFO)
        
    def bind(self,port,setId=True):
        self.d=defer.Deferred()
        log.msg("Attemtping to bind driver",self ,"with deviceId:",self.deviceId,"to port",port,system="Driver",logLevel=logging.DEBUG) 
        self.hardwareHandler.connect(setIdMode=setId,port=port)     
        return self.d
    
    def connect(self,mode=None,*args,**kwargs):
        if not self.isConnected:
            if mode is not None:
                self.connectionMode=mode
                log.msg("Connecting in mode:",self.connectionMode,system="Driver",logLevel=logging.CRITICAL) 
                if mode==3:
                    """special case for forced connection"""
                    unboundPorts=DriverManager.bindings.get_unboundPorts()
                    if len(unboundPorts)>0:
                        port=unboundPorts[0]
                        log.msg("Connecting in mode:",self.connectionMode,"to port",port,system="Driver",logLevel=logging.CRITICAL)
                        DriverManager.bindings.bind(self,port)
                        self.pluggedIn(port)
                        self.hardwareHandler.connect(port=port)
                        
                else:
                    self.hardwareHandler.connect()
            else:
                self.hardwareHandler.connect()
                
    def reconnect(self,*args,**kwargs):
        self.hardwareHandler.reconnect(*args,**kwargs)
    def disconnect(self,*args,**kwargs):
        self.hardwareHandler.disconnect(*args,**kwargs)
    
    def pluggedIn(self,port):    
        self.send_signal("plugged_In",port)
        self.isPluggedIn=True
        
        if self.autoConnect:
            #slight delay, to prevent certain problems when trying to send data to the device too fast
            reactor.callLater(1,self.connect,1)
           
        
    def pluggedOut(self,port):
        self.isConfigured=False  
        self.isDeviceHandshakeOk=False
        self.isDeviceIdOk=False
        self.isConnected=False
        self.isPluggedIn=False
        self.send_signal("plugged_Out",port)
        #self._signalDispatcher.send_message("pluggedOut",{"data":port})
    
    def send_signal(self,signal="",data=None):
        prefix=self.signalChannelPrefix+".driver."
        self._signalDispatcher.send_message(prefix+signal,self,data)
    
    def send_command(self,data,sender=None,callback=None,*args,**kwargs):
       # print("going to send command",data,"from",sender)
        if not self.isConnected:
            raise DeviceNotConnected()
        if self.logicHandler:
            self.logicHandler._handle_request(data=data,sender=sender,callback=callback)
    
    def _send_data(self,data,*arrgs,**kwargs):
        self.hardwareHandler.send_data(data)
         
    def _handle_response(self,data):
        if self.logicHandler:
            self.logicHandler._handle_response(data)
    
    """higher level methods""" 
    def startup(self):
        pass
    def shutdown(self):
        pass
    def init(self):
        pass
    def get_firmware_version(self):
        pass
    def set_debugLevel(self,level):
        pass
    
    def teststuff(self,params,*args,**kwargs):
        pass
    
    def variable_set(self,variable,params,sender=None,*args,**kwargs):
        pass
    def variable_get(self,variable,params,sender=None,*args,**kwargs):
        pass
    
    """
    ####################################################################################
                                Experimental
    """ 
    def start_command(self):
        pass
    def close_command(self):
        pass
    
    def get_endpoint(self,filter=None):
        """return a list of endpoints, filtered by parameters"""
        d=defer.Deferred()
        
        def filter_check(endpoint,filter):
            for key in filter.keys():
                if not getattr(endpoint, key) in filter[key]:
                    return False
            return True
      
        def get(filter):
            if filter:
                return [endpoint for endpoint in self.endpoints if filter_check(endpoint,filter)]
            else:               
                return nodesList
            
        d.addCallback(get)
        reactor.callLater(0.5,d.callback,filter)
        return d
        

    
    
class PortDriverBindings(object):
    """
    Helper class for setting and unseting driver /port bindings
    It relies on a "pseudo bidictionary": the elements dicts  contains keys for both
    drivers and ports 
    
    also add a secondary dict of "invalid devices":
    Devices that have been tried for every driver, and failed
    This dict's contents get reset if that port is removed
    or if a new driver is added
    """
    
    def __init__(self):
        self.elements={}     
        self.tested={}
    
    def add_toTested(self,driver,port):
        if not port in self.tested[driver]:
            self.tested[driver].append(port)
        try:
            if not driver in self.tested[port]:
                self.tested[port].append(driver)
        except KeyError:pass
        
    def remove_fromTested(self,driver,port):
        if port in self.tested[driver]:
            self.tested[driver].remove(port)
        
    def get_driverUntestedPorts(self,driver):
        "should be modified whenever a new port is added or removed"
        testeds=set([port for port in self.tested[driver]])
        return set(self.get_unboundPorts())-testeds
            
    def add_drivers(self,drivers):
        for driver in drivers:
            self.elements.__setitem__(driver,None)
            self.tested[driver]=[]
            
        #[self.elements.__setitem__(driver,None) for driver in drivers]
    def add_ports(self,ports):
        for port in ports:
            self.elements.__setitem__(port,None)
            self.tested[port]=[]
        #[self.elements.__setitem__(port,None) for port in ports]   
           
    def remove_drivers(self,drivers):
        """
        unbind and delete the specified drivers
        """
        for driver in drivers:
            self.unbind(driver=driver)
        for driver in drivers:
            try:
                del self.elements[driver]
            except KeyError:pass
            try:
                for port in self.tested[driver]:
                    try:
                        self.tested[port].remove(driver)
                    except Exception :pass
                del self.tested[driver]
            except KeyError:pass
            
    def remove_ports(self,ports):
        """
        unbind and delete the specified ports
        """
        for port in ports:
            #drv=self.elements[port]
            self.unbind(port=port)
        for port in ports:
            try:
                del self.elements[port]
            except KeyError:pass
            try:
                for driver in self.tested[port]:
                    try:
                        self.tested[driver].remove(port)
                    except Exception :pass
                    #self.tested[port].remove(driver)
                del self.tested[port]
            except KeyError:pass
            
    def get_bindingInfo(self,elementKey):
        """
        get the  value associated either with the driver or port
        """
        try:
            return self.elements[elementKey]
        except KeyError:
            return None
       
        
    def get_unboundPorts(self):
        """
        return a list of unbound ports: basically  all ports that have a value of None associated with
        them
        """
        
        return [port for port,driver in self.elements.iteritems() if port.__class__==str and not driver]
    
    def get_unboundDrivers(self):
        """
        return a list of unbound drivers: basically  all driver that have a value of None associated with
        them
        """
        return [driver for driver,port in self.elements.iteritems() if driver.__class__!=str and not port]
    def get_boundPorts(self):
        """
        return a list of bound ports: basically  all ports that have a driver (not None) associated with
        them
        """
        return [port for port,driver in self.elements.iteritems() if port.__class__==str and driver]
    def get_boundDrivers(self):
        """
        return a list of bound drivers: basically  all driver that have a port (not None ) associated with
        them
        """
        return [driver for driver,port in self.elements.iteritems() if driver.__class__!=str and port]
    def get_ports(self):
        """
        return a list of all ports: basically  all keys that are NOT of type "Driver"
        """
        return [port for port in self.elements.iterkeys() if port.__class__==str]
        
    def get_drivers(self):
        """
        return a list of all drivers: basically  all keys that are of type "Driver"
        """
        return [driver for driver in self.elements.iterkeys() if driver.__class__!=str]
        #return [driver for driver,port in self.elements.iteritems() if driver.__class__==Driver]
    
    def bind(self,driver=None,port=None):
        """ create a binding between a driver and a port : inserts two key value pairs into the elements
        dict : one driver->port and another port->driver"""
        self.elements[port]=driver
        self.elements[driver]=port    
        
    def unbind(self,driver=None,port=None):
        """ remove a binding between a driver and a port : deletes the two key value pairs from the elements
        dict : the driver->port and the port->driver pairs"""
        if port is not None and driver is not None:
            self.elements[port]=None
            self.elements[driver]=None
        elif port is not None and not driver:
            try:
                drv=self.elements[port]
                if drv:
                    self.elements[drv]=None
                self.elements[port]=None
            except KeyError:pass
        elif not port and driver is not None:
            prt=self.elements[driver]
            if prt:
                self.elements[prt]=None
            self.elements[driver]=None

class ConnectionInfo(object):
    """helper class encapsulating a binding and a list of hardwareManagers"""
    def __init__(self,hardwareHandlerKlass):
        self.bindings=PortDriverBindings()
        self.hardwareHandlerKlass=hardwareHandlerKlass
        
    def __getattr__(self, attr_name):
        if hasattr(self.bindings, attr_name):
            return getattr(self.bindings, attr_name)
        elif hasattr(self.hardwareHandlerKlass, attr_name):
            return getattr(self.hardwareHandlerKlass, attr_name)
        else:
            raise AttributeError(attr_name)   
        

class DriverManager(object):
    """
    This class acts as factory and manager
    The driver factory assembles a Driver object (the one whose instances are actually stored in db)
    from two objects : 
        * a driver_high object for all higher level functions (ie the ones of the current driver class, mostly)
        * a driver_low object for all lower level functions (ie the ones of the current connector class)
        this lower level driver is for example the actual serial_connector class as we have it currently
    This solve a whole lot of problems at once, since the subobjects will be essentially viewed as one, thanks
    to the getattr method
    """
    """
    For driver class: should there be a notion of "requester" for sending data, so that answers can be dispatche
    to the actual entity that sent the command ? for example : during a reprap 3d print, querying for sensor 
    data is actually completely seperate and should not be part of the print task, therefor, since all requests
    are sent to the same device, there needs to be a way to differenciate between the two when sending back messages
    """
    
    """
    For plug & play managment
    the whole "check and or set device id" procedure should not take place during the normal 
    connect etc process but in a completely seperate set of phases (somethink like a "setup" 
    and used to check for correct device on port /device id 
    
    the hardware manager's connect method needs to be modified:
    - if the device was successfully associated with a port in the p&p detection phase, use that port info
    - if the device was not identified , has no id, etc , then use the current "use the first available port" method
    
    perhaps we should use a method similar to the way drivers are installed on windows:
    - ask for removal of cable if already connected
    - ask for re plug of cable
    - do a diff on the previous/new list of com/tty devices
    - do id generation/association
    """    
    
    
    hardware_handlers=[]
     
    driverLock=defer.DeferredSemaphore(1)    
    bindings=PortDriverBindings()
    bindings2={}
    connectionsInfos={}
    pollFrequency=3
    
 
    """"""""""""""""""
    
    
    @classmethod 
    def setup(cls,*args,**kwargs):
        log.msg("Driver Manager setup succesfully",system="Driver Manager",logLevel=logging.CRITICAL)
        d=defer.Deferred()
        reactor.callLater(cls.pollFrequency,DriverManager.update_deviceList)
        d.callback(None)        
        return d      
        
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for drivers
    """    
    @classmethod 
    @defer.inlineCallbacks
    def create(cls,parentNode=None,driverType=None,driverParams={},*args,**kwargs):   
        plugins= (yield UpdateManager.get_plugins(ipollapli.IDriver))
        driver=None
        for driverKlass in plugins:
            if driverType==driverKlass.__name__.lower():
                driver=yield driverKlass(options=driverParams,**driverParams).save()
                yield driver.save()  
                driver.node.set(parentNode)
                yield driver.setup()
                cls.register_driver(driver,creation=True)
                break
        if not driver:
            raise UnknownDriver()
        defer.returnValue(driver)
    
    @classmethod    
    @defer.inlineCallbacks
    def load_old(cls,driver):
        driverType=driver.driverType
        params=driver.options
        plugins= (yield UpdateManager.get_plugins(ipollapli.IDriver))
        for driverKlass in plugins:
            if driverType==driverKlass.__name__.lower():
                hardwareHandler=driverKlass.components["hardwareHandler"](driver,**params)
                logicHandler=driverKlass.components["logicHandler"](driver,**params)
                driver.set_handlers(hardwareHandler,logicHandler)
                cls.register_driver(driver)
                yield driver.setup()
                break
        defer.returnValue(driver)
        
    @classmethod    
    @defer.inlineCallbacks
    def load(cls,driverId=None,parentNode=None):
        dbconfig = Registry.getConfig()
        plugins= (yield UpdateManager.get_plugins(ipollapli.IDriver))
        
        @defer.inlineCallbacks
        def find(drvType):
            for driverKlass in plugins:
                if drvType==driverKlass.__name__.lower():
                    driver=yield driverKlass.find(where=['node_id = ?', parentNode.id],limit=1)
                    yield driver.setup()
                    cls.register_driver(driver)
                    defer.returnValue(driver)
        
        if driverId is not None:
            driverType=yield  dbconfig.select(tablename="drivers", id=driverId,where=['node_id = ? ', parentNode.id,driverId],limit=1)["driverType"]
            drv=yield find(driverType)
            log.msg("Found and loaded driver:",drv,logLevel=logging.DEBUG,system="Driver")
            defer.returnValue(drv)
            
        elif parentNode is not None:  
            driver=None
            try:
                driverType=(yield  dbconfig.select(tablename="drivers",where=['node_id = ?', parentNode.id],limit=1))["driverType"]             
                driver=yield find(driverType)
                log.msg("Found and loaded driver:",driver,logLevel=logging.DEBUG,system="Driver")
            except:pass
            defer.returnValue(driver)
        
        
        
    @classmethod 
    @defer.inlineCallbacks
    def update(cls,driver,driverType=None,driverParams={},*args,**kwargs):   
        """ updates the given driver with the new params"""
        driverType=driverType
        plugins= (yield UpdateManager.get_plugins(ipollapli.IDriver))
        for driverKlass in plugins:
            if driverType==driverKlass.__name__.lower():
                driver.driverType=driverType
                driver.options=driverParams
                hardwareHandler=driverKlass.components["hardwareHandler"](driver,**driverParams)
                logicHandler=driverKlass.components["logicHandler"](driver,**driverParams)
                driver.set_handlers(hardwareHandler,logicHandler)
                yield driver.save()  
                yield driver.setup()
                break
        if not driver:
            raise UnknownDriver()    
        defer.returnValue(driver)
    
    """
    ####################################################################################
    The following are the plug&play and registration methods for drivers
    """
    @classmethod
    @defer.inlineCallbacks
    def get_driverTypes(cls,*args,**kwargs): 
        
        driverTypesTmp= yield UpdateManager.get_plugins(ipollapli.IDriver)   
        driverTypes=[driverTypeInst() for driverTypeInst in driverTypesTmp]
        defer.returnValue(driverTypes)
    
    @classmethod
    def register_driver(cls,driver,creation=False):
        log.msg("Registering driver",driver,logLevel=logging.DEBUG,system="Driver")
        if not driver.connectionType in cls.connectionsInfos:
            cls.connectionsInfos[driver.connectionType]=ConnectionInfo(driver.hardwareHandler.__class__)
        cls.connectionsInfos[driver.connectionType].add_drivers([driver])
        driver.connectionMode=2
        #driver.connectionMode=0
            #cls.set_remoteId(driver)
        #cls._start_bindAttempt(driver)
            
    @classmethod
    def unregister_driver(cls,driver):
        """for driver removal from the list of registered drivers"""
        cls.connectionsInfos[driver.connectionType].remove_drivers([driver])

    @classmethod
    @defer.inlineCallbacks
    def set_remoteId(cls,driver,port=None):
        print("setting remote id")
        """this method is usually used the first time a device is connected, to set
        its correct device id"""
        if not port:
            unbPorts=cls.bindings.get_unboundPorts()
            if unbPorts>0:
                port=unbPorts[0]
                driver.connectionMode=2
                yield driver.bind(port).addCallbacks(callback=cls._driver_binding_succeeded\
                            ,callbackKeywords={"driver":driver,"port":port},errback=cls._driver_binding_failed)
        else:
            log.msg("Impossible to do device binding, no ports available",system="Driver")
        driver.connectionMode=1
        defer.returnValue(True)
        
    @classmethod
    @defer.inlineCallbacks
    def setup_drivers(cls,connectionType):
        """
        method to iterate over driver and try to bind them to the correct available port
        the only "blocking/waiting" element is with drivers with the same connection type:
        ie : serial devices need to be done one by one, same with webcams, etc
        BUT !!
        you can have these at the same time:
        -bind serial devices
        -bind webcams
        """
        
        unbndDrivers=cls.connectionsInfos[connectionType].get_unboundDrivers()
        if len(unbndDrivers)>0:
         
            log.msg("Setting up drivers",logLevel=logging.INFO)
            for driver in unbndDrivers:   
                yield cls._start_bindAttempt(driver,cls.connectionsInfos[connectionType].bindings) 
        defer.returnValue(True)
        
        
    @classmethod
    @defer.inlineCallbacks
    def _start_bindAttempt(cls,driver,binding):
        """this methods tries to bind a given driver to a correct port
        should it fail, it will try to do the binding with the next available port,until either:
        * the port binding was sucessfull
        * all driver/port combos were tried
        """
        for port in binding.get_driverUntestedPorts(driver):#get_unboundPorts():
            if driver.isConfigured:
                break
            else:
               yield driver.bind(port).addCallbacks(callback=cls._driver_binding_succeeded\
                        ,callbackKeywords={"driver":driver,"port":port,"binding":binding},errback=cls._driver_binding_failed\
                        ,errbackKeywords={"driver":driver,"port":port,"binding":binding})
      
        defer.returnValue(True)
        
    @classmethod
    def _driver_binding_failed(cls,result,driver,port,*args,**kwargs):
        """call back method for driver binding failure"""
        cls.connectionsInfos[driver.connectionType].add_toTested(driver,port)
        log.msg("failed to plug ",driver,"to port",port,system="Driver",logLevel=logging.DEBUG)

    
    @classmethod
    @defer.inlineCallbacks
    def _driver_binding_succeeded(cls,result,driver,port,*args,**kwargs):
        """call back method for driver binding success
        also sets the global binding (binding helper) of the port/driver combo
        """
        cls.connectionsInfos[driver.connectionType].bind(driver,port)
       
        yield driver.save()
        log.msg("Node",(yield driver.node.get()).name,"plugged in to port",port,system="Driver",logLevel=logging.DEBUG)
        driver.pluggedIn(port)
        
    @classmethod
    @defer.inlineCallbacks  
    def update_deviceList(cls):
        """
        Method that gets called regularly, scans for newly plugged in/out devices
        and either 
        * tries to start the binding process if new devices were found
        * does all the necessary to remove a binding/do the cleanup, if a device was disconnected
        """
        
        def checkForPortChanges(oldL,newL):
            addedPorts=[]
            """
            we don't do a preliminary "if len(oldL) != len(newL):" since even with the same amount of 
            detected devices, the actual devices in the list could be different
            """
            s1=set(oldL)
            s2=set(newL)
            addedPorts=s2-s1
            removedPorts=s1-s2
            if len(addedPorts)==0:
                addedPorts=None
            if len(removedPorts)==0:
                removedPorts=None
            return (addedPorts,removedPorts)
        
        
        portListing={}#old, new as tupples of lists

        for connectionType,connectionInfo in cls.connectionsInfos.items() :
            oldPorts=connectionInfo.get_ports()
            newPorts=(yield connectionInfo.list_ports())
            addedPorts,removedPorts=checkForPortChanges(oldPorts,newPorts)
            portListing[connectionType]=(connectionInfo.get_ports(),(yield connectionInfo.list_ports()))     
        
            if addedPorts:  
                log.msg("Ports added:",addedPorts," to connection type",connectionType,system="Driver",logLevel=logging.DEBUG)          
                connectionInfo.add_ports(list(addedPorts))
            if addedPorts or (len(connectionInfo.get_unboundDrivers())>0 and len(connectionInfo.get_unboundPorts())>0):
                #log.msg("New ports/drivers detected: These ports were added",addedPorts,logLevel=logging.DEBUG)   
                cls.driverLock.run(cls.setup_drivers,connectionType)
            if removedPorts:    
                log.msg("Ports removed:",removedPorts,logLevel=logging.DEBUG)             
                oldBoundDrivers=connectionInfo.get_boundDrivers()
                connectionInfo.remove_ports(list(removedPorts)) 
                newBoundDrivers=connectionInfo.get_boundDrivers()
            
                for driver in set(oldBoundDrivers)-set(newBoundDrivers):
                    port=driver.hardwareHandler.port
                    log.msg("Node",(yield driver.node.get()).name,"plugged out of port",port," in connection type",connectionType,system="Driver") 
                    driver.pluggedOut(port)
              
                
     

        
        #if addedPorts is None and removedPorts is None:
        reactor.callLater(1,DriverManager.update_deviceList)
        
        
"""
####################################################################################
Driver logic handlers

some things need to be changed:
*twostep handling for commands needs to be changed to multipart (n complete blocks of
recieved data to consider the response done
*for reprap temperature reading, it begs the question of where this would need to be implemented:
the two part is required for 5d and teacup, but is unlikely to be the same for makerbot: so should this kind of 
difference defined in the protocol ? and in that case should we define specific methods in the protocols like:
 "read sensor" ? (read temperature would be waaay to specific)
"""


class Command(object):
    """Base command class, encapsulate all request and answer commands, also has a 'special' flag for commands that do no participate in normal flow of gcodes : i
    ie for example , regular poling of temperatures for display (the "OK" from those commands MUST not affect the line by line sending/answering of gcodes)
    """
    def __init__(self,special=False,multiParts=1,answerRequired=True,request=None,answer=None,sender=None,callback=None):
        """
        Params:
        special: generally used for "system" commands such as M105 (temperature read) as oposed to general, print/movement commands
        TwoStep: used for commands that return data in addition to "Ok"
        AnswerRequired: for commands that return an answer
        AnswerComplete: flag that specified that an answer is complete
        Request: OPTIONAL: the sent command
        Answer: what answer did we get
        """
        self.special=special
        self.multiParts=multiParts
        self.currentPart=1
        self.answerRequired=answerRequired
        self.requestSent=False
        self.answerComplete=False
        self.request=request
        self.answer=answer
        self.sender=sender
        
        self.callback=callback
        
    def callCallback(self):
        if self.callback is not None:
            self.callback(self.answer)
    def __str__(self):
        #return str(self.request)+" "+str(self.answer)
        return str(self.answer)
        #return "Special:"+ str(self.special)+", TwoStep:"+str(self.twoStep) +", Answer Required:"+str(self.answerRequired)+", Request:"+ str(self.request)+", Answer:"+ str(self.answer) 


class CommandQueueLogic(object):
    """
    Implements a command queue system for drivers
    """
    def __init__(self,driver,bufferSize=8,*args,**kwargs):
        self.driver=driver
        self.bufferSize=bufferSize
        self.answerableCommandBuffer=[]
        self.commandBuffer=[]
        self.commandSlots=bufferSize
        #print("in command queue logic , driver:",driver)
    
        
    def _handle_request(self,data,sender=None,callback=None,*args,**kwargs):
        """
        Manages command requests
        """
      
        cmd=Command(**kwargs)
        
        cmd.request=data
        cmd.sender=sender
        cmd.callback=callback
        
        
        if cmd.answerRequired and len(self.commandBuffer)<self.bufferSize:
            log.msg("adding command",cmd,"from",cmd.sender,"callback",callback,system="Driver",logLevel=logging.DEBUG)
            self.commandBuffer.append(cmd)
            if self.commandSlots>1:
                self.commandSlots-=1
            #initial case
            if len(self.commandBuffer)==1:
                self.send_next_command()
            
             
    def _handle_response(self,data):
        """handles only commands that got an answer, formats them correctly and sets necesarry flags
        params: data the raw response that needs to be treated
        """
        cmd=None        
        #print("here",len(self.commandBuffer)>0)
        #self.driver.send_signal("dataRecieved",data)
        if len(self.commandBuffer)>0:
            try:
                if self.commandBuffer[0].currentPart>1:  
                    self.commandBuffer[0].currentPart-=1
                    #self.commandBuffer[0].twoStep=False
                    cmd=self.commandBuffer[0]
                    cmd.answer+=data
                else:
                    cmd=self.commandBuffer[0]
                    del self.commandBuffer[0]
                    cmd.answerComplete=True
                    cmd.answer=data
                    self.commandSlots+=1#free a commandSlot
                    
                    cmd.callCallback()
                    
                    #print("recieved data ",cmd.answer,"command sender",cmd.sender )
                   # self.driver.send_signal(cmd.sender+".dataRecieved",cmd.answer,True)
                   
                    self.send_next_command()       
            except Exception as inst:
                log.msg("Failure in handling command ",str(inst),system="Driver")
        else:
                cmd=Command(answer=data)
                cmd.answerComplete=True   
                #print("recieved data 2",cmd.answer,"command sender",cmd.sender )    
        return cmd
     
    def send_next_command(self):
        """Returns next avalailable command in command queue """
        cmd=None
       # print("in next command: buffer",len(self.commandBuffer),"slots",self.commandSlots)  
        if not self.driver.isDeviceHandshakeOk:
            pass
            #raise Exception("Machine connection not established correctly")
        elif self.driver.isDeviceHandshakeOk and len(self.commandBuffer)>0 and self.commandSlots>0:        
            tmp=self.commandBuffer[0]
            if not tmp.requestSent:            
                cmd=self.commandBuffer[0].request
                tmp.requestSent=True
                self.driver._send_data(cmd)
                #self.logger.debug("Driver giving next command %s",str(cmd))
        else:
            if len(self.commandBuffer)>0:
                print("pouet")
                #self.logger.critical("Buffer Size Exceed Machine capacity: %s elements in command buffer, CommandSlots %s, CommandBuffer %s",str(len(self.commandBuffer)),str(self.commandSlots),[str(el) for el in self.commandBuffer])
        return cmd 
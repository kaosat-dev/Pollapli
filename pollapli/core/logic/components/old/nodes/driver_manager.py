import logging,ast,time
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twisted.python import log,failure





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
    bindings = PortDriverBindings()
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
                driver=yield driverKlass(extra_params=driverParams,**driverParams).save()
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
                driver.extra_params=driverParams
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
    def get_driver_types(cls,*args,**kwargs): 
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
            #cls.set_remote_id(driver)
        #cls._start_bind_attempt(driver)
            
    @classmethod
    def unregister_driver(cls,driver):
        """for driver removal from the list of registered drivers"""
        cls.connectionsInfos[driver.connectionType].remove_drivers([driver])

    @classmethod
    @defer.inlineCallbacks
    def set_remote_id(cls,driver,port=None):
        print("setting remote id")
        """this method is usually used the first time a device is connected, to set
        its correct device id"""
        if not port:
            unbPorts=cls.bindings.get_unbound_ports()
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
                yield cls._start_bind_attempt(driver,cls.connectionsInfos[connectionType].bindings) 
        defer.returnValue(True)
        
        
    @classmethod
    @defer.inlineCallbacks
    def _start_bind_attempt(cls,driver,binding):
        """this methods tries to bind a given driver to a correct port
        should it fail, it will try to do the binding with the next available port,until either:
        * the port binding was sucessfull
        * all driver/port combos were tried
        """
        for port in binding.get_driver_untested_ports(driver):#get_unbound_ports():
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
        cls.connectionsInfos[driver.connectionType].add_to_tested(driver,port)
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
            if addedPorts or (len(connectionInfo.get_unboundDrivers())>0 and len(connectionInfo.get_unbound_ports())>0):
                #log.msg("New ports/drivers detected: These ports were added",addedPorts,logLevel=logging.DEBUG)   
                cls.driverLock.run(cls.setup_drivers,connectionType)
            if removedPorts:    
                log.msg("Ports removed:",removedPorts,logLevel=logging.DEBUG)             
                oldBoundDrivers=connectionInfo.get_bound_drivers()
                connectionInfo.remove_ports(list(removedPorts)) 
                newBoundDrivers=connectionInfo.get_bound_drivers()
            
                for driver in set(oldBoundDrivers)-set(newBoundDrivers):
                    port=driver.hardwareHandler.port
                    log.msg("Node",(yield driver.node.get()).name,"plugged out of port",port," in connection type",connectionType,system="Driver") 
                    driver.pluggedOut(port)
        
        #if addedPorts is None and removedPorts is None:
        reactor.callLater(1,DriverManager.update_deviceList)
        
        
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
    
    def add_to_tested(self,driver,port):
        if not port in self.tested[driver]:
            self.tested[driver].append(port)
        try:
            if not driver in self.tested[port]:
                self.tested[port].append(driver)
        except KeyError:pass
        
    def remove_from_tested(self,driver,port):
        if port in self.tested[driver]:
            self.tested[driver].remove(port)
        
    def get_driver_untested_ports(self,driver):
        "should be modified whenever a new port is added or removed"
        testeds=set([port for port in self.tested[driver]])
        return set(self.get_unbound_ports())-testeds
            
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
            
    def get_binding_info(self,element_key):
        """
        get the  value associated either with the driver or port
        """
        try:
            return self.elements[element_key]
        except KeyError:
            return None
       
        
    def get_unbound_ports(self):
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
    def get_bound_ports(self):
        """
        return a list of bound ports: basically  all ports that have a driver (not None) associated with
        them
        """
        return [port for port,driver in self.elements.iteritems() if port.__class__==str and driver]
    def get_bound_drivers(self):
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
    def __init__(self,hardware_interface_klass):
        self.bindings=PortDriverBindings()
        self.hardware_interface_klass=hardware_interface_klass
        
    def __getattr__(self, attr_name):
        if hasattr(self.bindings, attr_name):
            return getattr(self.bindings, attr_name)
        elif hasattr(self.hardware_interface_klass, attr_name):
            return getattr(self.hardware_interface_klass, attr_name)
        else:
            raise AttributeError(attr_name)   
        

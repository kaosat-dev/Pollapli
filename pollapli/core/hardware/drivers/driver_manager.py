"""Driver manager module for the handling of hardware connection, drivers"""
import logging
from twisted.internet import reactor, defer
from twisted.python import log
from pollapli.exceptions import UnknownDriver


class PortDriverBindings(object):
    """
    Helper class for setting and unseting driver /port bindings
    It relies on a "pseudo bidictionary": the elements dicts  contains keys
    for both drivers and ports.
    Also add a secondary dict of "invalid devices":
    Devices that have been tried for every driver, and failed
    This dict's contents get reset if that port is removed
    or if a new driver is added
    """

    def __init__(self):
        self.elements = {}
        self.tested = {}

    def add_to_tested(self, driver, port):
        """add the driver and port to the list of tested
        bindings"""
        if not port in self.tested[driver]:
            self.tested[driver].append(port)
        try:
            if not driver in self.tested[port]:
                self.tested[port].append(driver)
        except KeyError:
            pass

    def remove_from_tested(self, driver, port):
        """remove the driver and port from the list of tested
        bindings"""
        if port in self.tested[driver]:
            self.tested[driver].remove(port)

    def get_driver_untested_ports(self, driver):
        "should be modified whenever a new port is added or removed"
        testeds = set([port for port in self.tested[driver]])
        return set(self.get_unbound_ports()) - testeds

    def add_drivers(self, drivers):
        """add a list of drivers to the list of drivers"""
        for driver in drivers:
            self.elements.__setitem__(driver, None)
            self.tested[driver] = []
        #[self.elements.__setitem__(driver,None) for driver in drivers]

    def add_ports(self, ports):
        """add a list of ports to the list of ports"""
        for port in ports:
            self.elements.__setitem__(port, None)
            self.tested[port] = []
        #[self.elements.__setitem__(port,None) for port in ports]

    def remove_drivers(self, drivers):
        """
        unbind and delete the specified drivers
        """
        for driver in drivers:
            self.unbind(driver=driver)
        for driver in drivers:
            try:
                del self.elements[driver]
            except KeyError:
                pass
            try:
                for port in self.tested[driver]:
                    try:
                        self.tested[port].remove(driver)
                    except Exception:
                        pass
                del self.tested[driver]
            except KeyError:
                pass

    def remove_ports(self, ports):
        """
        unbind and delete the specified ports
        """
        for port in ports:
            #drv=self.elements[port]
            self.unbind(port=port)
        for port in ports:
            try:
                del self.elements[port]
            except KeyError:
                pass
            try:
                for driver in self.tested[port]:
                    try:
                        self.tested[driver].remove(port)
                    except Exception:
                        pass
                    #self.tested[port].remove(driver)
                del self.tested[port]
            except KeyError:
                pass

    def get_binding_info(self, element_key):
        """
        get the  value associated either with the driver or port
        """
        try:
            return self.elements[element_key]
        except KeyError:
            return None

    def get_unbound_ports(self):
        """
        return a list of unbound ports: basically  all ports that have a value
        of None associated with them
        """
        return [port for port, driver in self.elements.iteritems() if port.__class__ == str and not driver]

    def get_unbound_drivers(self):
        """
        return a list of unbound drivers: basically all driver that have a
        value of None associated with them
        """
        return [driver for driver, port in self.elements.iteritems() if driver.__class__ != str and not port]

    def get_bound_ports(self):
        """
        return a list of bound ports: basically  all ports that have a driver
        (not None) associated with them
        """
        return [port for port, driver in self.elements.iteritems() if port.__class__ == str and driver]

    def get_bound_drivers(self):
        """
        return a list of bound drivers: basically  all driver that have a port
        (not None) associated with them
        """
        return [driver for driver, port in self.elements.iteritems() if driver.__class__ != str and port]

    def get_ports(self):
        """
        return a list of all ports: basically  all keys that are NOT of type
        "Driver"
        """
        return [port for port in self.elements.iterkeys() if port.__class__ == str]

    def get_drivers(self):
        """
        return a list of all drivers: basically  all keys that are of type
        "Driver"
        """
        return [driver for driver in self.elements.iterkeys() if driver.__class__ != str]

    def bind(self, driver=None, port=None):
        """ create a binding between a driver and a port : inserts two
        key-value pairs into the elements dict :
        one driver->port and another port->driver"""
        self.elements[port] = driver
        self.elements[driver] = port

    def unbind(self, driver=None, port=None):
        """ remove a binding between a driver and a port : deletes the two
        key-value pairs from the elements dict :
         the driver->port and the port->driver pairs"""
        if port is not None and driver is not None:
            self.elements[port] = None
            self.elements[driver] = None
        elif port is not None and not driver:
            try:
                drv = self.elements[port]
                if drv:
                    self.elements[drv] = None
                self.elements[port] = None
            except KeyError:
                pass
        elif not port and driver is not None:
            prt = self.elements[driver]
            if prt:
                self.elements[prt] = None
            self.elements[driver] = None


class HardwareInterfaceInfo(object):
    """helper class encapsulating a binding and a list of hardwareManagers"""
    def __init__(self, hardware_interface_klass):
        self.bindings = PortDriverBindings()
        self.hardware_interface_klass = hardware_interface_klass

    def __getattr__(self, attr_name):
        if hasattr(self.bindings, attr_name):
            return getattr(self.bindings, attr_name)
        elif hasattr(self.hardware_interface_klass, attr_name):
            return getattr(self.hardware_interface_klass, attr_name)
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

    For driver class: should there be a notion of "requester" for sending data, so that answers can be dispatche
    to the actual entity that sent the command ? for example : during a reprap 3d print, querying for sensor 
    data is actually completely seperate and should not be part of the print task, therefor, since all requests
    are sent to the same device, there needs to be a way to differenciate between the two when sending back messages

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

    def __init__(self, hardware_poll_frequency=3, *args, **kwargs):
        self.hardware_poll_requency = hardware_poll_frequency
        self._driver_lock = defer.DeferredSemaphore(1)
        self._port_to_driver_bindings = PortDriverBindings()
        self._hardware_interfaces = {}

    def setup(self, *args, **kwargs):
        """setup the driver manager"""
        log.msg("Driver Manager setup succesfully", system="Driver Manager", logLevel=logging.CRITICAL)
        deferred = defer.Deferred()
        reactor.callLater(self.hardware_poll_requency, self.update_device_list)
        deferred.callback(None)
        return deferred

    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for drivers
    """

#    @defer.inlineCallbacks
#    def create(self,parentNode=None,driverType=None,driverParams={},*args,**kwargs):
#        plugins= (yield PackageManager.get_plugins(ipollapli.IDriver))
#        driver=None
#        for driverKlass in plugins:
#            if driverType==driverKlass.__name__.lower():
#                driver = driverKlass(options=driverParams,**driverParams)
#                driver.node.set(parentNode)
#                yield driver.setup()
#                self.register_driver(driver,creation=True)
#                break
#        if not driver:
#            raise UnknownDriver()
#        defer.returnValue(driver)

#    @defer.inlineCallbacks
#    def update(self,driver,driverType=None,driverParams={},*args,**kwargs):   
#        """ updates the given driver with the new params"""
#        driverType=driverType
#        plugins= (yield PackageManager.get_plugins(ipollapli.IDriver))
#        for driverKlass in plugins:
#            if driverType==driverKlass.__name__.lower():
#                driver.driverType=driverType
#                driver.options=driverParams
#                hardwareHandler=driverKlass.components["hardwareHandler"](driver,**driverParams)
#                logicHandler=driverKlass.components["logicHandler"](driver,**driverParams)
#                driver.set_handlers(hardwareHandler,logicHandler)
#                yield driver.setup()
#                break
#        if not driver:
#            raise UnknownDriver()    
#        defer.returnValue(driver)

    def add_driver(self, driver):
        pass

    def get_drivers(self, filters=None):
        """
        Returns the list of drivers, filtersed by  the filters param
        the filters is a dictionary of list, with each key beeing an attribute
        to check, and the values in the list , values of that param to check against
        """
        deferred = defer.Deferred()

        def filters_check(driver, filters):
            for key in filters.keys():
                if not getattr(driver, key) in filters[key]:
                    return False
            return True

        def _get_drivers(filters, driverList):
            if filters:
                return [driver for driver in driverList if filters_check(driver, filters)]
            else:
                return driverList

        deferred.addCallback(_get_drivers, self._port_to_driver_bindings.get_drivers())
        reactor.callLater(0.5, deferred.callback, filters)
        return deferred

    def delete_driver(self, driver_id):
        """
        Remove a driver
        Params:
        driver_id: the driver_id of the driver
        """
        deferred = defer.Deferred()

        def remove(driver_id, drivers):
            driver = None
            for drivr in drivers:
                if drivr.id == driver_id:
                    driver = drivr
                    break
            drivers.remove(driver)
            log.msg("Removed driver %s" % str(driver), logLevel=logging.CRITICAL)
        deferred.addCallback(remove, self._port_to_driver_bindings.get_drivers())
        reactor.callLater(0, deferred.callback, driver_id)
        return deferred

    @defer.inlineCallbacks
    def clear_drivers(self):
        """
        Removes & deletes ALL the drivers (disconnecting them first)
        This should be used with care, as well as checks on client side
        """
        for driver in self._port_to_driver_bindings.get_drivers():
            yield self.delete_driver(driver_id=driver.id)

    """
    ###########################################################################
    The following are the plug&play and registration methods for drivers
    """

    def connect_to_hardware(self, driver_id=None, connection_mode=1):
        """driver_id : the id of the driver to connect
        connection_mode: the mode in which to connect the driver
        """
        driver = None
        if connection_mode == 3:
            """special case for forced connection"""
            unbound_ports = self._port_to_driver_bindings.get_unbound_ports()
            if len(unbound_ports) > 0:
                port = unbound_ports[0]
                log.msg("Connecting in mode:", connection_mode, "to port", port, system="Driver", logLevel=logging.CRITICAL)
                self._port_to_driver_bindings.bind(driver, port)

    def register_driver(self, driver=None):
        if driver is None:
            raise UnknownDriver()
        """register a driver in the system"""
        log.msg("Registering driver", driver, logLevel=logging.DEBUG, system="Driver")
        if not driver.hardware_interface in self._hardware_interfaces:
            self._hardware_interfaces[driver.hardware_interface] = HardwareInterfaceInfo(driver.hardwareHandler.__class__)
        self._hardware_interfaces[driver.hardware_interface].add_drivers([driver])
        driver.connection_mode = 2

    def unregister_driver(self, driver):
        """for driver removal from the list of registered drivers"""
        self._hardware_interfaces[driver.hardware_interface].remove_drivers([driver])

    @defer.inlineCallbacks
    def set_remote_id(self, driver, port=None):
        """this method is usually used the first time a device is connected, to set
        its correct device id"""
        log.msg("Setting remote id", driver, logLevel=logging.DEBUG, system="Driver")
        if not port:
            unbound_ports = self._port_to_driver_bindings.get_unbound_ports()
            if unbound_ports > 0:
                port = unbound_ports[0]
                driver.connection_mode = 2
                yield driver.bind(port).addCallbacks(callback=self._driver_binding_succeeded,\
                                            callbackKeywords={"driver": driver, "port": port}, errback=self._driver_binding_failed)
        else:
            log.msg("Impossible to do device binding, no ports available", system="Driver")
        driver.connection_mode = 1

    @defer.inlineCallbacks
    def setup_drivers(self, hardware_interface):
        """
        method to iterate over drivers and try to bind them to the correct
        available port
        The only "blocking/waiting" element is with drivers with the same
        connection type:
        ie : serial devices need to be done one by one,
        same with webcams, etc
        BUT !!
        you can have these at the same time:
        -bind serial devices
        -bind webcams
        """
        unbound_drivers = self._hardware_interfaces[hardware_interface].get_unbound_drivers()
        if len(unbound_drivers) > 0:
            log.msg("Setting up drivers", logLevel=logging.INFO)
            for driver in unbound_drivers:   
                yield self._start_bind_attempt(driver,self._hardware_interfaces[hardware_interface].bindings) 
        defer.returnValue(True)

    @defer.inlineCallbacks
    def _start_bind_attempt(self, driver, binding):
        """this methods tries to bind a given driver to a correct port
        should it fail, it will try to do the binding with the next
        available port,until either:
        * the port binding was sucessfull
        * all driver/port combos were tried
        """
        for port in binding.get_driver_untested_ports(driver):
            if driver.isConfigured:
                break
            else:
                yield driver.bind(port).addCallbacks(callback = \
        self._driver_binding_succeeded\
        , callbackKeywords={"driver": driver, "port": port, "binding": binding}
        , errback=self._driver_binding_failed\
        , errbackKeywords={"driver": driver, "port": port, "binding": binding})

    def _driver_binding_failed(self, result, driver, port, *args, **kwargs):
        """call back method for driver binding failure"""
        self._hardware_interfaces[driver.hardware_interface].add_to_tested(driver, port)
        log.msg("failed to plug ", driver, "to port", port, system="Driver", logLevel=logging.DEBUG)

    @defer.inlineCallbacks
    def _driver_binding_succeeded(self, result, driver, port, *args, **kwargs):
        """call back method for driver binding success
        also sets the global binding (binding helper) of the port/driver combo
        """
        self._hardware_interfaces[driver.hardware_interface].bind(driver, port)
        log.msg("Node", (yield driver.node.get()).name, "plugged in to port", port, system="Driver", logLevel=logging.DEBUG)
        driver.pluggedIn(port)

    @defer.inlineCallbacks
    def update_device_list(self):
        """
        Method that gets called regularly, scans for newly plugged in/out devices
        and either 
        * tries to start the binding process if new devices were found
        * does all the necessary to remove a binding/do the cleanup, if a device was disconnected
        """
        def check_for_port_changes(old_list, new_list):
            """
            we don't do a preliminary "if len(old_list) != len(new_list):" since even with the same amount of
            detected devices, the actual devices in the list could be different
            """
            set_1 = set(old_list)
            set_2 = set(new_list)
            added_ports = set_2 - set_1
            removed_ports = set_1 - set_2
            if len(added_ports) == 0:
                added_ports = None
            if len(removed_ports) == 0:
                removed_ports = None
            return (added_ports, removed_ports)

        port_listing = {}  # old, new as tupples of lists

        for hardware_interface, connection_info in self._hardware_interfaces.items():
            old_ports = connection_info.get_ports()
            new_ports = (yield connection_info.list_ports())
            added_ports, removed_ports = check_for_port_changes(old_ports, new_ports)
            port_listing[hardware_interface] = (connection_info.get_ports(), (yield connection_info.list_ports()))

            if added_ports:
                log.msg("Ports added:", added_ports, " to connection type", hardware_interface, system="Driver", logLevel=logging.DEBUG)
                connection_info.add_ports(list(added_ports))
            if added_ports or (len(connection_info.get_unbound_drivers()) > 0 and len(connection_info.get_unbound_ports()) > 0):
                #log.msg("New ports/drivers detected: These ports were added",added_ports,logLevel=logging.DEBUG)
                self._driver_lock.run(self.setup_drivers, hardware_interface)
            if removed_ports:
                log.msg("Ports removed:", removed_ports, logLevel=logging.DEBUG)
                oldBoundDrivers = connection_info.get_bound_drivers()
                connection_info.remove_ports(list(removed_ports))
                newBoundDrivers = connection_info.get_bound_drivers()

                for driver in set(oldBoundDrivers) - set(newBoundDrivers):
                    port = driver.hardwareHandler.port
                    log.msg("Node", (yield driver.node.get()).name, "plugged out of port", port, " in connection type", hardware_interface, system="Driver")
                    driver.pluggedOut(port)

        #if added_ports is None and removed_ports is None:
        reactor.callLater(0.2, DriverManager.update_device_list)

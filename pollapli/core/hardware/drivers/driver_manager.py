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
        return [port for port, driver in self.elements.iteritems()
                if port.__class__ == str and not driver]

    def get_unbound_drivers(self):
        """
        return a list of unbound drivers: basically all driver that have a
        value of None associated with them
        """
        return [driver for driver, port in self.elements.iteritems()
                if driver.__class__ != str and not port]

    def get_bound_ports(self):
        """
        return a list of bound ports: basically  all ports that have a driver
        (not None) associated with them
        """
        return [port for port, driver in self.elements.iteritems()
                if port.__class__ == str and driver]

    def get_bound_drivers(self):
        """
        return a list of bound drivers: basically  all driver that have a port
        (not None) associated with them
        """
        return [driver for driver, port in self.elements.iteritems()
                if driver.__class__ != str and port]

    def get_ports(self):
        """
        return a list of all ports: basically  all keys that are NOT of type
        "Driver"
        """
        return [port for port in self.elements.iterkeys()
                if port.__class__ == str]

    def get_drivers(self):
        """
        return a list of all drivers: basically  all keys that are of type
        "Driver"
        """
        return [driver for driver in self.elements.iterkeys()
                if driver.__class__ != str]

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
    def __init__(self, hardware_interface_class):
        self.bindings = PortDriverBindings()
        self.hardware_interface_class = hardware_interface_class

    def __getattr__(self, attr_name):
        if hasattr(self.bindings, attr_name):
            return getattr(self.bindings, attr_name)
        elif hasattr(self.hardware_interface_class, attr_name):
            return getattr(self.hardware_interface_class, attr_name)
        else:
            raise AttributeError(attr_name)


class DriverManager(object):
    """
    This class acts as factory and manager
    For plug & play managment:
    the whole "check and or set device id" procedure should not take place
    during the normal connect etc process but in a completely seperate set
    of phases(something like a "setup" and used to check for correct device
    on port/device id)

    the hardware manager's connect method needs to be modified:
    - if the device was successfully associated with a port in the
    p&p detection phase, use that port info
    - if the device was not identified , has no id, etc
    then use the current "use the first available port" method

    perhaps we should use a method similar to the way drivers are installed
    on mswindows type systems:
    - ask for removal of cable if already connected
    - ask for re plug of cable
    - do a diff on the previous/new list of com/tty devices
    - do id generation/association
    """

    def __init__(self, hardware_poll_frequency=2, *args, **kwargs):
        self.hardware_poll_requency = hardware_poll_frequency
        self._drivers = {}
        self._port_to_driver_bindings = PortDriverBindings()
        self._hardware_interfaces = {}
        self._hardware_poller = None

    def setup(self):
        """setup the driver manager"""
        log.msg("Driver Manager setup succesfully", system="Driver Manager", logLevel=logging.CRITICAL)
        self._hardware_poller = reactor.callLater(self.hardware_poll_requency, self.update_device_list)

    @defer.inlineCallbacks
    def teardown(self):
        if self._hardware_poller is not None:
            self._hardware_poller.cancel()
        yield self.clear_drivers()
        log.msg("Shutting down, goodbye!", system="DriverManager", logLevel=logging.CRITICAL)

    """
    ###########################################################################
    The following are the driver "CRUD" (Create, read, update,delete) methods
    """

    def add_driver(self, driver_class, *args, **kwargs):
        """add a driver to the list of manager drivers
        driver_class : the class of the driver
        params : the parameters to pass to the constructor of the driver
        """
        driver = driver_class(*args, **kwargs)
        if not driver.is_configured:
            driver.connection_mode = 0
        self._register_driver(driver)
        return driver

    def update_driver(self, driver_id=None, *args, **kwargs):
        driver = self.get_driver(driver_id)
        driver.update(*args, **kwargs)

    def get_driver(self, driver_id=None):
        """get a driver, based on its id"""
        if driver_id is None:
            raise UnknownDriver()
        driver = self._drivers.get(driver_id)
        if driver is None:
            raise UnknownDriver()
        return driver

    def get_drivers(self, filters=None):
        """
        Returns the list of drivers, filtered by  the filters param
        the filters is a dictionary of list, with each key beeing an attribute
        to check, and the values in the list , values of that param to check
        against
        """
        deferred = defer.Deferred()

        def filters_check(driver, filters):
            """driver: a driver instance
            filters: see above
            """
            for key in filters.keys():
                if not getattr(driver, key) in filters[key]:
                    return False
            return True

        def _get_drivers(filters, driver_list):
            """filters: see above
            driver_list: a list of driver instances
            """
            if filters:
                return [driver for driver in driver_list if filters_check(driver, filters)]
            else:
                return driver_list

        deferred.addCallback(_get_drivers, self._drivers.values())
        reactor.callLater(0.5, deferred.callback, filters)
        return deferred

    def delete_driver(self, driver_id=None):
        """
        Remove a driver
        Params:
        driver_id: the driver_id of the driver
        """
        deferred = defer.Deferred()

        def remove(driver_id):
            driver = self._drivers.get(driver_id)
            del self._drivers[driver_id]
            self._unregister_driver(driver)
            if driver.is_connected:
                driver.disconnect()
            log.msg("Removed driver %s" % str(driver), system="DriverManager", logLevel=logging.CRITICAL)
        deferred.addCallback(remove)
        reactor.callLater(0, deferred.callback, driver_id)
        return deferred

    @defer.inlineCallbacks
    def clear_drivers(self):
        """
        Removes & deletes ALL the drivers (disconnecting them first)
        This should be used with care, as well as checks on client side
        """
        for driver_id in self._drivers.keys():
            yield self.delete_driver(driver_id=driver_id)

    """
    ###########################################################################
    The following are helper methods
    """

    def get_unbound_ports(self, hardware_interface):
        hardware_interface_info = self._hardware_interfaces.get(hardware_interface)
        unbound_ports = hardware_interface_info.get_unbound_ports()
        return unbound_ports

    """
    ###########################################################################
    The following are driver related methods
    """
    @defer.inlineCallbacks
    def set_remote_id(self, driver, port=None):
        """this method is usually used the first time a device is connected, to set
        its correct device id"""
        log.msg("Setting remote id", driver, system="DriverManager", logLevel=logging.DEBUG)
        if not port:
            unbound_ports = self._port_to_driver_bindings.get_unbound_ports()
            if unbound_ports > 0:
                port = unbound_ports[0]
                driver.connection_mode = 0
                yield driver.bind(port).addCallbacks(callback=self._driver_binding_succeeded, \
                                            callbackKeywords={"driver": driver, "port": port}, errback=self._driver_binding_failed)
        else:
            log.msg("Impossible to do device binding, no ports available", system="DriverManager")
        driver.connection_mode = 1
    """
    ###########################################################################
    The following are the plug&play and registration methods for drivers
    """

    @defer.inlineCallbacks
    def connect_to_hardware(self, driver_id=None, port=None, connection_mode=1):
        """driver_id : the id of the driver to connect
        connection_mode: the mode in which to connect the driver

        first search if driver is already bound, if it is use that data
        """
        driver = self.get_driver(driver_id=driver_id)
        if port is None:
                unbound_ports = self.get_unbound_ports(driver.hardware_interface_class)
                if len(unbound_ports) == 0:
                    raise Exception("No port specified and no port available")
                port = unbound_ports[0]
        if connection_mode == 2:
            """special case for forced connection"""
            self._port_to_driver_bindings.bind(driver, port)
        elif connection_mode == 0:
            pass
#            if driver.hardware_id is None:
#                raise Exception("No HardwareId specified Cannot configure hardware to port permabind ")

        log.msg("Connecting to hardware in mode:", connection_mode, "to port", port, system="DriverManager", logLevel=logging.CRITICAL)
        yield driver.connect(port=port, connection_mode=connection_mode)

    def upload_firmware(self, firmware):
        """upload a specific firmware to a given device
        perhaps use this kind of field as helper:
        target_hardware = "Generic_arduino"
        """
        pass

    def _register_driver(self, driver=None):
        if driver is None:
            raise UnknownDriver()
        """register a driver in the system"""
        log.msg("Registering driver", driver, system="DriverManager", logLevel=logging.DEBUG)
        drv_inteface_class = driver.hardware_interface_class
        if not drv_inteface_class in self._hardware_interfaces:
            self._hardware_interfaces[drv_inteface_class] = HardwareInterfaceInfo(drv_inteface_class)
        self._hardware_interfaces[drv_inteface_class].add_drivers([driver])
        self._drivers[driver.cid] = driver

    def _unregister_driver(self, driver):
        """for driver removal from the list of registered drivers"""
        log.msg("Unregistering driver", driver, system="DriverManager", logLevel=logging.DEBUG)
        self._hardware_interfaces[driver.hardware_interface_class].remove_drivers([driver])

    @defer.inlineCallbacks
    def _setup_drivers(self, hardware_interface):
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
            log.msg("Setting up drivers", system="DriverManager", logLevel=logging.INFO)
            for driver in unbound_drivers:
                yield self._attempt_binding(driver,self._hardware_interfaces[hardware_interface].bindings)

    @defer.inlineCallbacks
    def _attempt_binding(self, driver, binding):
        """this methods tries to bind a given driver to a correct port
        should it fail, it will try to do the binding with the next
        available port,until either:
        * the port binding was sucessfull
        * all driver/port combos were tried
        """
        for port in binding.get_driver_untested_ports(driver):
            binding_ok = False

            if not driver.is_bound and driver.do_authentification:
                try:
                    yield driver.connect(port=port, connection_mode=1)
                    binding_ok = True
                except Exception as inst:
                    pass

            if binding_ok:
                self._hardware_interfaces[driver.hardware_interface_class].bind(driver, port)
                log.msg("Driver", str(driver), "plugged in to port", port, system="DriverManager", logLevel=logging.DEBUG)
                driver.is_bound = True
                if not driver.auto_connect:
                    driver.disconnect()
            else:
                self._hardware_interfaces[driver.hardware_interface_class].add_to_tested(driver, port)
                driver.disconnect()
                log.msg("failed to plug ", driver, "to port", port, system="DriverManager", logLevel=logging.DEBUG)

    def check_for_port_changes(self, old_list, new_list):
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

    @defer.inlineCallbacks
    def update_device_list(self):
        """
        Method that gets called regularly, scans for newly plugged in/out devices
        and either 
        * tries to start the binding process if new devices were found
        * does all the necessary to remove a binding/do the cleanup, if a device was disconnected
        """
        for hardware_interface, connection_info in self._hardware_interfaces.items():
            old_ports = connection_info.get_ports()
            new_ports = (yield connection_info.list_ports())
            added_ports, removed_ports = self.check_for_port_changes(old_ports, new_ports)
            if added_ports:
                log.msg("Ports added:", added_ports, " to connection type", hardware_interface, system="DriverManager", logLevel=logging.DEBUG)
                connection_info.add_ports(list(added_ports))
            if added_ports or (len(connection_info.get_unbound_drivers()) > 0 and len(connection_info.get_unbound_ports()) > 0):
                #log.msg("New ports/drivers detected: These ports were added", added_ports, logLevel=logging.DEBUG)
                yield self._setup_drivers(hardware_interface)
            if removed_ports:
                log.msg("Ports removed:", removed_ports, logLevel=logging.DEBUG)
                oldBoundDrivers = connection_info.get_bound_drivers()
                connection_info.remove_ports(list(removed_ports))
                newBoundDrivers = connection_info.get_bound_drivers()

                for driver in set(oldBoundDrivers) - set(newBoundDrivers):
                    port = driver.hardwareHandler.port
                    log.msg("Driver", driver, "plugged out of port", port, " in connection type", hardware_interface, system="DriverManager", logLevel=logging.DEBUG)
                    driver.is_bound = False

#        self._hardware_poller = reactor.callLater(self.hardware_poll_requency, self.update_device_list)
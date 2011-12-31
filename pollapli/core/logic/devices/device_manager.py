import logging
from twisted.internet import reactor, defer
from twisted.python import log
from pollapli.core.logic.tools.signal_system import SignalDispatcher
from pollapli.exceptions import UnknownDeviceType, DeviceNotFound
from pollapli.core.logic.devices.device import Device


class DeviceManager(object):
    """
    Class for managing devices: works as a container, a handler
    and a central management point for the list of available devices
     the signal signature for device manager events is as follows:
     -for example environment_id.device_created : this is for coherence,
     signal names use underscores, while hierarchy is represented by dots)
    """

    def __init__(self, parentEnvironment):
        self._parentEnvironment = parentEnvironment
        self._persistenceLayer = parentEnvironment._persistenceLayer
        self._devices = {}
        self._signal_channel = "device_manager"
        self._signal_dispatcher = SignalDispatcher(self._signal_channel)
        self.signal_channel_prefix = "environment_" + str(self._parentEnvironment.cid)

    @defer.inlineCallbacks
    def setup(self):
        if self._persistenceLayer is None:
            self._persistenceLayer = self._parentEnvironment._persistenceLayer
        devices = yield self._persistenceLayer.load_devices(environmentId=self._parentEnvironment.cid)
        for device in devices:
            device._parent = self._parentEnvironment
            device._persistenceLayer = self._persistenceLayer
            self._devices[device.cid] = device
            #yield device.setup()

    def _send_signal(self, signal="", data=None):
        prefix = self.signal_channel_prefix + "."
        self._signal_dispatcher.send_message(prefix + signal, self, data)

    """
    ###########################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the
    general handling of devices
    """

    @defer.inlineCallbacks
    def add_device(self, name="Default device", description="", device_type=None, *args, **kwargs):
        """
        Add a new device to the list of devices of the current environment
        Params:
        name: the name of the device
        Desciption: short description of device
        device_type: the device_type of the device : very important , as it
        will be used to instanciate the correct class instance
        Connector:the connector to use for this device
        Driver: the driver to use for this device's connector
        """

        device = Device(parent=self._parentEnvironment, name=name, description=description, device_type=device_type)
        yield self._persistenceLayer.save_device(device)
        self._devices[device.cid] = device
        log.msg("Added  device ", name, logLevel=logging.CRITICAL)
        self._send_signal("device_created", device)
        defer.returnValue(device)

    def get_device(self, device_id):
        if not device_id in self._devices.keys():
            raise DeviceNotFound()
        return self._devices[device_id]

    def get_devices(self, filters=None, *args, **kwargs):
        """
        Returns the list of devices, filtered by  the filter param
        the filter is a dictionary of list, with each key beeing an attribute
        to check, and the values in the list , values of that param to check
        against
        """
        deferred = defer.Deferred()

        def filter_check(device, filters):
            for key in filters.keys():
                if not getattr(device, key) in filters[key]:
                    return False
            return True

        def get(filters, device_list):
            if filter:
                return [device for device in device_list if filter_check(device, filters)]
            else:
                return device_list
        deferred.addCallback(get, self._devices.values())
        reactor.callLater(0.5, deferred.callback, filters)
        return deferred

    @defer.inlineCallbacks
    def update_device(self, device_id, name=None, description=None, *args, **kwargs):
        """Method for device update"""
        device = self._devices[device_id]
        device.name = name
        device.description = description

        yield self._persistenceLayer.save_device(device)
        self._send_signal("device_updated", device)
        log.msg("updated device :new name", name, "new descrption", description, logLevel=logging.CRITICAL)
        defer.succeed(device)

    @defer.inlineCallbacks
    def delete_device(self, device_id):
        """
        Remove a device : this needs a whole set of checks,
        as it would delete a device completely
        Params:
        device_id: the device_id of the device
        """

        device = self._devices.get(device_id, None)
        if device is None:
            raise DeviceNotFound()
        yield self._persistenceLayer.delete_device(device)
        del self._devices[device_id]
        self._send_signal("device_deleted", device)
        log.msg("Removed device ", device.name, logLevel=logging.CRITICAL)
        defer.succeed(True)

    @defer.inlineCallbacks
    def clear_devices(self):
        """
        Removes & deletes ALL the devices, should be used with care
        """
        for device in self._devices.values():
            yield self.delete_device(device.cid)
        self._send_signal("devices_cleared", self._devices)

    """
    ##########################################################################
    Helper Methods
    """

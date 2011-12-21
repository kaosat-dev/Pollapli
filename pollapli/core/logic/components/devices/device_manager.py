import logging
from twisted.internet import reactor, defer
from twisted.python import log,failure
from pollapli.core.logic.tools.signal_system import SignalDispatcher
from pollapli.core.logic.components.devices.device import Device
from pollapli.exceptions import UnknownDeviceType,DeviceNotFound

class DeviceManager(object):
    """
    Class for managing devices: works as a container, a handler
    and a central management point for the list of available devices
    
     the signal signature for device manager events is as follows: 
     -for example environment_id.device_created : this is for coherence, signal names use underscores, while hierarchy is represented by dots)
    """
    
    def __init__(self,parentEnvironment):
        self._parentEnvironment = parentEnvironment
        self._persistenceLayer = parentEnvironment._persistenceLayer
        self._devices = {}
        self.signalChannel = "device_manager"
        self._signalDispatcher = SignalDispatcher(self.signalChannel)
        self.signalChannelPrefix = "environment_"+str(self._parentEnvironment._id)
     
    @defer.inlineCallbacks    
    def setup(self):
        if self._persistenceLayer is None:
            self._persistenceLayer = self._parentEnvironment._persistenceLayer        
        devices = yield self._persistenceLayer.load_devices(environmentId = self._parentEnvironment._id)
        for device in devices:
            device._parent = self._parentEnvironment
            device._persistenceLayer = self._persistenceLayer
            self._devices[device._id] = device
            #yield device.setup()
    
    def send_signal(self, signal="", data=None):
        prefix=self.signalChannelPrefix+"."
        self._signalDispatcher.send_message(prefix+signal,self,data)    
    
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of devices
    """
    @defer.inlineCallbacks
    def add_device(self,name="Default device",description="",type=None,*args,**kwargs):
        """
        Add a new device to the list of devices of the current environment
        Params:
        name: the name of the device
        Desciption: short description of device
        type: the type of the device : very important , as it will be used to instanciate the correct class
        instance
        Connector:the connector to use for this device
        Driver: the driver to use for this device's connector
        """
            
        device = Device(parent= self._parentEnvironment, name=name, description=description, type=type)
        yield self._persistenceLayer.save_device(device)
        self._devices[device._id]=device
        log.msg("Added  device ",name, logLevel=logging.CRITICAL)
        self.send_signal("device_created", device)
        defer.returnValue(device)
      
    def get_device(self,id):
        if not id in self._devices.keys():
            raise DeviceNotFound()
        return self._devices[id]
          
    def get_devices(self, filter = None, *args, **kwargs):
        """
        Returns the list of devices, filtered by  the filter param
        the filter is a dictionary of list, with each key beeing an attribute
        to check, and the values in the list , values of that param to check against
        """
        d=defer.Deferred()
        
        def filter_check(device,filter):
            for key in filter.keys():
                if not getattr(device, key) in filter[key]:
                    return False
            return True
      
        def get(filter,devicesList):
            if filter:
                return [device for device in devicesList if filter_check(device,filter)]
            else:               
                return devicesList
        d.addCallback(get,self._devices.values())
        reactor.callLater(0.5,d.callback,filter)
        return d
    
    @defer.inlineCallbacks
    def update_device(self,id,name=None,description=None,*args,**kwargs):
        """Method for device update"""   
        device = self._devices[id]
        device.name=name
        device.description=description
            
        yield self._persistenceLayer.save_device(device)
        self.send_signal("device_updated", device)
        log.msg("updated device :new name",name,"new descrption",description,logLevel=logging.CRITICAL)
        defer.succeed(device)
    
    @defer.inlineCallbacks
    def delete_device(self,id):
        """
        Remove a device : this needs a whole set of checks, 
        as it would delete a device completely 
        Params:
        id: the id of the device
        """
           
        device = self._devices.get(id,None)
        if device is None:
            raise DeviceNotFound()
        yield self._persistenceLayer.delete_device(device) 
        del self._devices[id]
        self.send_signal("device_deleted", device)
        log.msg("Removed device ",device.name,logLevel=logging.CRITICAL)
        defer.succeed(True)
    
    @defer.inlineCallbacks
    def clear_devices(self):
        """
        Removes & deletes ALL the devices, should be used with care
        """
        for device in self._devices.values():
            yield self.delete_device(device._id)  
        self.send_signal("devices_cleared", self._devices)   

    """
    ####################################################################################
    Helper Methods    
    """
    
  

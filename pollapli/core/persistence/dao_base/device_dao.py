import abc


class DeviceDao(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def load_device(self, id = None, *args, **kwargs):
        """Retrieve data for device object."""
        return

    @abc.abstractmethod
    def load_devices(self, *args, **kwargs):
        """Retrieve data for all device object."""
        return

    @abc.abstractmethod
    def save_device(self, device):
        """Save the device object ."""
        return

    @abc.abstractmethod
    def save_devices(self, lDevices):
        """Save a list of device object ."""
        return
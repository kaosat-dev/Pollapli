"""
.. py:module:: node
   :synopsis: generic node class, parent of hardware and software nodes
   , node manager class etc
"""
import logging
from twisted.python import log
from pollapli.core.logic.tools.signal_system import SignalDispatcher
from pollapli.core.logic.devices.device_component import BaseDeviceComponent
from twisted.internet.defer import Deferred


class Device(BaseDeviceComponent):
    """
    Base class for all Device: a Device is a software abstraction for a
    physical device such as a webcam, reprap , arduino etc
    """
    def __init__(self, name="base_device", description="base device", environment="Home"):
        """
        :param environment : just a tag to identify the environment this device
        belongs to
        """
        BaseDeviceComponent.__init__(self, None, name="base_device", description="base device")
        self.name = name
        self.description = description
        self.status = "inactive"
        self.environment = environment
        self.driver = None
        self._signal_channel = "device %s" % self.cid
        self._signal_dispatcher = SignalDispatcher(self._signal_channel)

    def __eq__(self, other):
        return self.cid == other.cid and self.name == other.name and self.description == other.description and self.status == other.status

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getattr__(self, attr_name):
        if hasattr(self.driver, attr_name):
            attr = getattr(self.driver, attr_name)
            if hasattr(attr, '__call__'):
                def wrapper(*args, **kwargs):
                    print('before calling %s' % attr.__name__)
                    result = attr(*args, **kwargs)
                    if isinstance(result, Deferred):
                        print("method returning deferred",attr)
                    print('done calling %s' % attr.__name__)
                    return result
                return wrapper
            else:
                return attr
        else:
            raise AttributeError(attr_name)

    def setup(self):
        "configure device"
        log.msg("Device with id", self.cid, "setup successfully", system="Device", logLevel=logging.CRITICAL)

    """
    ###########################################################################
    The following are the methods for component manipulation
    """

    def enable_disable_components(self, component_list=None, component_category="actuator", component_type="stepper", component_on=False):
        pass

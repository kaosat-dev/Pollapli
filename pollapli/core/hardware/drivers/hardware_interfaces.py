"""base hardware interface classes"""
import sys
from twisted.internet import defer


class BaseHardwareInterface(object):
    blocked_ports = []
    blacklisted_ports = ["COM3"]
    available_ports = []

    def __init__(self, driver=None, protocol=None, reset_on_connection=False, *args, **kwargs):
        self.driver = driver
        self.protocol = protocol(self.driver, *args, **kwargs)
        self.reset_on_connection = reset_on_connection

    def send_data(self, command):
        self.protocol.send_data(command)

    def connect(self, port=None, *args, **kwargs):
        raise NotImplementedError()

    def reconnect(self):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()

    @classmethod
    def list_ports(cls):
        """
        Return a list of ports, in a deferred
        """
        raise NotImplementedError()

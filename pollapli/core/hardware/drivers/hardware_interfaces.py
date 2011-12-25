"""base hardware interface classes"""
import sys
from twisted.internet import defer


class BaseHardwareInterface(object):
    blocked_ports = []
    blacklisted_ports = ["COM3"]
    available_ports = []

    def __init__(self, driver=None, protocol=None, *args, **kwargs):
        self.driver = driver
        self.protocol = protocol(self.driver, *args, **kwargs)

    def send_data(self, command):
        self.protocol.send_data(command)

    def connect(self, port=None, *args, **kwargs):
        self.driver.connection_errors = 0

    def reconnect(self):
        pass

    def disconnect(self):
        pass

    @classmethod
    def list_ports(cls):
        """
        Return a list of ports, in a deferred
        """

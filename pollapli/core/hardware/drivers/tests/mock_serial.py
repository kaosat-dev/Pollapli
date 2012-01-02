"""Elements for mock serial"""
import time
from twisted.internet import reactor, defer
from twisted.python import log
from twisted.plugin import IPlugin
from zope.interface import classProvides
from pollapli.core.hardware.drivers.hardware_interfaces import BaseHardwareInterface
from pollapli import ipollapli
from serial.serialutil import SerialException
import logging

class MockSerialWrapper(object):
    """wrapper around the twisted SerialPort class, for convenience and
     bugfix
     """
    def __init__(self, protocol, deviceNameOrPortNumber, reactor, 
        baudrate = 9600, bytesize = None, parity = None,
        stopbits = None, xonxoff = 0, rtscts = 0):
    
        self._tmp_data_buffer = []
        self.reactor = reactor
        self.protocol = protocol
        self.protocol.makeConnection(self)

    def serialReadEvent(self):
        """emulate a read event"""
        read_buf = ""
        self.protocol.dataReceived(str(read_buf))

    def connectionLost(self, reason="connectionLost"):
        self.protocol.connectionLost("connectionLost")
        
    def loseConnection(self):
        self.connectionLost("")
        
    def setDTR(self, on=1):
        pass


class MockSerialHardwareInterface(BaseHardwareInterface):
    """class emulating the connection to serial based devices"""
    classProvides(IPlugin, ipollapli.IDriverHardwareHandler)
    blocked_ports = []
    blacklisted_ports = ["COM3"]
    available_ports = []

    def __init__(self, driver=None, protocol=None, reset_on_connection=True, speed=115200, *args, **kwargs):
        BaseHardwareInterface.__init__(self, driver, protocol, reset_on_connection, *args, **kwargs)
        self.speed = speed
        self.serial = None
        self.port = None

    def connect(self, port=None, *args, **kwargs):
        log.msg("Connecting... to port:", port, " at speed ", self.speed, " in mode ", self.driver.connection_mode, system="Driver", logLevel=logging.DEBUG)
        if self.port is None and port is None:
            self.driver.errors.append(Exception("No Port specified"))
#            raise Exception("No port specified")
        if port is not None:
            self.port = port
        self._connect(port, *args, **kwargs)

    def reconnect(self):
        self.disconnect(clear_port=False)
        self._connect()

    def disconnect(self, clear_port=False):
        if clear_port:
            self.port = None
            if self.port in MockSerialHardwareInterface.blocked_ports:
                MockSerialHardwareInterface.blocked_ports.remove(self.port)
        try:
            if self.serial is not None:
                try:
                    self.serial.loseConnection()
                    #self.pulseDTR()
                except Exception as inst:
                    self.driver.errors.append(inst)
                self.serial = None
        except Exception as inst:
            print("error in serial disconnection", str(inst))

    def _connect(self, *args, **kwargs):
        """Port connection/reconnection procedure"""
        if self.port is not None and self.driver.connection_errors < self.driver.max_connection_errors:
            try:
                if not self.port in MockSerialHardwareInterface.blocked_ports:
                    MockSerialHardwareInterface.blocked_ports.append(self.port)
                self.serial = MockSerialWrapper(self.protocol, self.port, reactor, baudrate=self.speed)
                if self.reset_on_connection:
                    self.pulseDTR()
            except SerialException as inst:
                self.driver.errors.append(inst)
                self.driver.connection_errors += 1
                log.msg("failed to connect serial driver,because of error", inst, "attempts left:", self.driver.max_connection_errors - self.driver.connection_errors, system="Driver")
                reactor.callLater(self.driver.connection_errors * 2, self._connect)

    @classmethod
    def list_ports(cls):
        """
        Return a list of ports
        """
        deferred = defer.Deferred()

        def _list_ports(*args, **kwargs):
            foundPorts = []
            foundPorts.append(cls.mock_ports)
            return foundPorts

        deferred.addCallback(_list_ports)
        reactor.callLater(0.1, deferred.callback, None)
        return deferred

    def pulseDTR(self):
        if self.serial is not None:
            self.serial.setDTR(1)
            time.sleep(0.022)
            self.serial.setDTR(0)
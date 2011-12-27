"""classes for the serial interface"""
from serial.serialutil import SerialException
"""necessary workaround for win32 serial port bugs in twisted"""
import re
import sys
import itertools
import logging
import glob
from twisted.python.win32 import WindowsError
from pollapli.core.hardware.drivers.protocols import DummyProtocol
if sys.platform == "win32":
    from pollapli.core.hardware.patches._win32serialport import SerialPort
else:
    from twisted.internet.serialport import SerialPort
from twisted.internet import reactor, defer
from twisted.python import log, failure
from twisted.plugin import IPlugin
from zope.interface import classProvides
from pollapli import ipollapli
from pollapli.core.hardware.drivers.hardware_interfaces import BaseHardwareInterface


class SerialWrapper(SerialPort):
    """wrapper around the twisted SerialPort class, for convenience and
     bugfix
     """
    def __init__(self, *args, **kwargs):
        SerialPort.__init__(self, *args, **kwargs)
        self._tmp_data_buffer = []
        self.deferred = defer.Deferred()

    def connectionLost(self, reason="connectionLost"):
        SerialPort.connectionLost(self, reason)
        self.deferred.callback("connection failure")


class SerialHardwareInterface(BaseHardwareInterface):
    """class handling the connection to serial based devices"""
    classProvides(IPlugin, ipollapli.IDriverHardwareHandler)
    blocked_ports = []
    blacklisted_ports = ["COM3"]
    available_ports = []

    def __init__(self, driver=None, protocol=None, speed=115200, *args, **kwargs):
        BaseHardwareInterface.__init__(self, driver, protocol, *args, **kwargs)
        self.speed = speed
        self.serial = None
        self.port = None

    def connect(self, port=None, *args, **kwargs):
        self.driver.connection_errors = 0
        log.msg("Connecting... to port:", port, " at speed ", self.speed, " in mode ", self.driver.connection_mode, system="Driver", logLevel=logging.DEBUG)
        if self.port is None and port is None:
            raise Exception("No port specified")
        if port is not None:
            self.port = port
        self._connect(port, *args, **kwargs)

    def reconnect(self):
        self.disconnect(clear_port=False)
        self._connect()

    def disconnect(self, clear_port=False):
        self.driver.is_connected = False
        self.driver.cancel_timeout()
        if clear_port:
            self.port = None
            if self.port in SerialHardwareInterface.blocked_ports:
                SerialHardwareInterface.blocked_ports.remove(self.port)
        try:
            if self.serial is not None:
                try:
                    self.serial.deferred.cancel()
                    self.serial.loseConnection()
                except:
                    pass
                self.serial = None
        except Exception as inst:
            print("error in serial disconnection", str(inst))

    def connectionClosed(self, failure):
        pass

    def _connect(self, *args, **kwargs):
        """Port connection/reconnection procedure"""
        if self.port and self.driver.connection_errors < self.driver.max_connection_errors:
            try:
                #self.port=str((yield self.scan())[0])
                if not self.port in SerialHardwareInterface.blocked_ports:
                    SerialHardwareInterface.blocked_ports.append(self.port)
                self.serial = SerialWrapper(self.protocol, self.port, reactor, baudrate=self.speed)
                self.serial.deferred.addCallbacks(callback=self._connect, errback=self.connectionClosed)
            except SerialException as inst:
                self.driver.connection_errors += 1
                log.msg("failed to connect serial driver,because of error", inst, "attempts left:", self.driver.max_connection_errors - self.driver.connection_errors, system="Driver")
                reactor.callLater(self.driver.connection_errors * 2, self._connect)
        else:
            try:
                if self.serial is not None:
                    self.serial.deferred.cancel()
                self.disconnect(clear_port=True)
            except Exception as inst:
                pass
            if self.driver.connection_mode == 1:
                log.msg("cricital error while (re-)starting serial connection : please check your driver settings and device id, as well as cables,  and make sure no other process is using the port ", system="Driver", logLevel=logging.CRITICAL)
            else:
                log.msg("Failed to establish correct connection with device/identify device by id", system="Driver", logLevel=logging.DEBUG)
            self.driver.deferred.errback(failure.Failure(Exception("Generic connection failure")))
#            reactor.callLater(0.1, , )

    @classmethod
    def list_ports(cls):
        """
        Return a list of ports
        """
        deferred = defer.Deferred()

        def _list_ports(*args, **kwargs):
            foundPorts = []
            if sys.platform == "win32":
                import _winreg as winreg
                path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                except WindowsError:
                    raise EnvironmentError
                for i in itertools.count():
                    try:
                        val = winreg.EnumValue(key, i)
                        port = str(val[1])
                        if port not in cls.blacklisted_ports: 
                            foundPorts.append(port)
                    except EnvironmentError:
                        break
            else:
                foundPorts = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/cu*') 
            #log.msg("Serial Ports on  system:",str(foundPorts),system="Driver",logLevel=logging.DEBUG)
            return foundPorts

        reactor.callLater(0.1, deferred.callback, None)
        deferred.addCallback(_list_ports)
        return deferred

    @classmethod
    @defer.inlineCallbacks 
    def list_available_ports(cls):
        """scan for available ports.
        Returns a list of actual available ports"""
        available = []
        serial = None
        for port in (yield cls.list_ports()):
            if port not in cls.blacklisted_ports:
                try:
                    serial = SerialWrapper(DummyProtocol(), port, reactor)
                    available.append(serial._serial.name)
                    #if port not in cls.available_ports:
                    #    cls.available_ports.append(serial._serial.name)
                    serial.loseConnection()
                except Exception as inst:
                    pass
                    #log.msg("Error while opening port",port,"Error:",inst)
        defer.returnValue(available)

    def pulseDTR(self, target):
        """emulation of the pulse DTR method"""
        if self.driver.is_connected:
            self.serial.setDTR(1)

            def _set_dtr(*args, **kwargs):
                self.serial.setDTR(0)
            reactor.callLater(0.5, _set_dtr)  # not sure this would work as time.sleep replacement
            self.disconnect()

    """The next methods are at least partially deprecated and not in use """
    def teardown(self):
        """
        Clean shutdown function
        """
        try:
            SerialHardwareInterface.blocked_ports.remove(self.port)
        except Exception as inst:
            log.msg("Serial error: %s " % str(inst), loglevel=logging.CRITICAL)
        self.driver.is_connected = False
        log.msg("Serial shutting down")

"""classes for the serial interface"""
from twisted.internet.defer import Deferred
import time

"""necessary workaround for win32 serial port bugs in twisted"""
import re
import sys
import itertools
import logging
import glob
from serial.serialutil import SerialException
from twisted.python.win32 import WindowsError
if sys.platform == "win32":
    from pollapli.core.hardware.patches._win32serialport import SerialPort
else:
    from twisted.internet.serialport import SerialPort
from twisted.internet import reactor, defer
from twisted.python import log
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

    def connectionLost(self, reason="connectionLost"):
        SerialPort.connectionLost(self, reason)


class SerialHardwareInterface(BaseHardwareInterface):
    """class handling the connection to serial based devices"""
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
            if self.port in SerialHardwareInterface.blocked_ports:
                SerialHardwareInterface.blocked_ports.remove(self.port)
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
                if not self.port in SerialHardwareInterface.blocked_ports:
                    SerialHardwareInterface.blocked_ports.append(self.port)
                self.serial = SerialWrapper(self.protocol, self.port, reactor, baudrate=self.speed)
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
            return foundPorts

        deferred.addCallback(_list_ports)
        reactor.callLater(0.1, deferred.callback, None)
        return deferred

    def pulseDTR(self):
        if self.serial is not None:
            self.serial.setDTR(1)
            time.sleep(0.022)
            self.serial.setDTR(0)

    def pulseDTR_alt(self):
        """emulation of the pulse DTR method"""
        deferred = Deferred()

        def _pulse_dtr(*args, **kwargs):
            self.serial.setDTR(1)
            time.sleep(0.022)
            self.serial.setDTR(0)
        deferred.addCallback(_pulse_dtr)
        reactor.callLater(0, deferred.callback, None)
        return deferred
#          s.setDTR(False) # Drop DTR
#                    timesleep(0.022)    # Read somewhere that 22ms is what the UI does.
#                    s.setDTR(True)  # UP the DTR back 

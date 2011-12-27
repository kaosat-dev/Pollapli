"""all base protocols for drivers"""
import logging
import time
import re
from twisted.internet import reactor, defer
from twisted.python import log, failure
from zope.interface import classProvides
from twisted.plugin import IPlugin
from twisted.internet.protocol import Protocol
from twisted.internet.interfaces import IProtocol
from uuid import uuid4


class DummyProtocol(Protocol):
    """empty protocol, used for connection checks"""
    classProvides(IPlugin, IProtocol)


class BaseProtocol(Protocol):
    """generic base protocol, cannot be used directly"""
    classProvides(IPlugin, IProtocol)

    def __init__(self, driver=None, handshake=None):
        self.driver = driver
        self.handshake = handshake
        self._data_handlers_order = [self.driver._handle_response]
        if self.driver.do_authentifaction:
            self._data_handlers_order.insert(0, self._handle_authentification)
        if self.driver.do_handshake:
            self._data_handlers_order.insert(0, self._handle_handshake)
        self._data_handler_index = 0

    def connectionMade(self):
        """called upon connection"""
        log.msg("Device connected", system="Driver", logLevel=logging.INFO)
        self.driver.set_timeout()
        if self.driver.connection_mode == 1:
            self.driver._send_signal("connected", self.driver._hardware_interface.port)

    def connectionLost(self, reason="connectionLost"):
        log.msg("Device disconnected", system="Driver", logLevel=logging.INFO)
        if self.driver.connection_mode == 1:
            self.driver._send_signal("disconnected", self.driver._hardware_interface.port)
        self.driver.cancel_timeout()

    """
    ###########################################################################
    The following are methods for sending/recieving/formating data
    """

    def _format_data_in(self, data):
        """
        Formats an incoming data block according to some specs/protocol 
        :param data the incoming data from the device
        :rtype: the formated data
        """
        raise NotImplementedError()

    def _format_data_out(self, data):
        """
        Formats an outgoing block of data according to some specs/protocol 
        :param data: the OUTGOING data TO the device
        :rtype:
        """
        raise NotImplementedError()

    def dataReceived(self, data):
        self.driver.cancel_timeout()
        data = self._format_data_in(data)
        log.msg("Data recieved <<: ", data,system = "Driver", logLevel = logging.DEBUG)
        self.driver._handle_response(data)

    def send_data(self, data):
        """
        Simple wrapper to send data over serial
        :param data: the data to send to the device
        """
        try:
            data = self._format_data_out(data)
            log.msg("Data sent >>: ", data, system="Driver", logLevel=logging.DEBUG)
            self.driver.set_timeout()
            self.transport.write(data)
        except Exception:
            log.msg("serial device not connected or not found on specified port", system="Driver", logLevel=logging.CRITICAL)

    def _dispatch_response(self, data):
        if not self.driver.is_connected:
            is_hans_ok = False
            is_auth_ok = False

            if self.driver.do_authentifaction:
                if self.driver.is_authentification_ok:
                    is_auth_ok = True
            else:
                is_auth_ok = True

            if self.driver.do_handshake:
                if self.driver.is_handshake_ok:
                    is_hans_ok = True
            else:
                is_hans_ok = True

            if is_hans_ok and is_auth_ok:
                self.driver.is_connected = True
                if self.driver.connection_mode == 0:
                    self.driver.is_configured = True
                self.driver.deferred.callback(None)
            else:
                handler = self._data_handlers_order[self._data_handler_index]
                handler(data)
        else:
            self.driver._handle_response(data)

    """
    ###########################################################################
    The following are methods for handshake/authentification
    """

    def _handle_handshake(self, data):
        """
        handles machine handshake
        :param data: the incoming data from the machine (the handshake)
        """
        if self.driver.do_handshake:
            self._check_handshake(data)
            if not self.driver.is_handshake_ok:
                self.driver.reconnect()

    def _check_handshake(self, data):
        """
        checks the recieved hanshake vs the expercted one
        :param data: the incoming data from the machine (the handshake)
        """
        log.msg("Attempting to validate hardware handshake", system="Driver", logLevel=logging.INFO)
        if self.handshake is None:
            raise Exception("No handshake specified")
        if self.handshake in data:
            self.driver.is_handshake_ok = True
            log.msg("Device handshake validated", system="Driver", logLevel=logging.DEBUG)
            self._data_handler_index += 1

            if self.driver.do_authentifaction:
                self._get_hardware_id()
            else:
                self._dispatch_response(data)
        else:
            log.msg("Device hanshake mismatch: expected :", self.handshake, "got:", data, system="Driver", logLevel=logging.DEBUG)
            self._handle_handshake(data)

    def _handle_authentification(self, data):
        """
        handles machine authentification
        :param data: the incoming data from the machine (should be the hardware id)
        """
        if self.driver.do_authentifaction:
#            if not hasattr(self, "_authentification_in_progress"):
#                self._authentification_in_progress = True
#                self._get_hardware_id()
#                return
            self._check_hardware_id(data)
            if not self.driver.is_authentification_ok:
                self.driver.reconnect()

    def _check_hardware_id(self, data):
        """
        checks the recieved id vs the expercted one
        :param data: the incoming data from the machine (the id)
        """
        log.msg("Attempting to validate hardware id", system="Driver", logLevel=logging.INFO)
        if self.driver.connection_mode == 1:
            if self.driver.hardware_id is None:
                raise Exception("No identifier specified")
            if data == str(self.driver.hardware_id):
                self.driver.is_authentification_ok = True
                log.msg("Device indentification validated", system="Driver", logLevel=logging.DEBUG)
                self._data_handler_index += 1
                self._dispatch_response(data)
            else:
                log.msg("Device indentification mismatch: expected :", self.driver.hardware_id, "got:", data, system="Driver", logLevel=logging.DEBUG)
        else:
            self.driver.is_authentification_ok = True
            self.driver.hardware_id = data
            log.msg("Device indentification configured", system="Driver", logLevel=logging.DEBUG)
            self._data_handler_index += 1
            self._dispatch_response(data)

    def _set_hardware_id(self):
        raise NotImplementedError()

    def _get_hardware_id(self):
        raise NotImplementedError()


class BaseTextSerialProtocol(BaseProtocol):
    """basic , text based protocol for serial devices"""
    classProvides(IPlugin, IProtocol)

    def __init__(self, driver=None, handshake="start", seperator='\r\n'):
        BaseProtocol.__init__(self, driver, handshake)
        self.seperator = seperator
        self.handshake = handshake
        self._in_data_buffer = ""
        self._regex = re.compile(self.seperator)

    """
    ###########################################################################
    The following are methods for sending/recieving/formating data
    """

    def _format_data_in(self, data):
        data = data.replace('\n', '')
        data = data.replace('\r', '')
        return data

    def _format_data_out(self, data):
        try:
            if isinstance(data, unicode):
                import unicodedata
                data = unicodedata.normalize('NFKD', data).encode('ascii','ignore')
            return "%s\n" % data
        except Exception as inst:
            log.msg("Error while formatting ouput data :", inst, system="Driver", logLevel=logging.CRITICAL)
            return ""

    def dataReceived(self, data):
        self.driver.cancel_timeout()
        try:
            self._in_data_buffer += str(data.encode('utf-8'))
            packets = None
            try:
                packets = self._regex.search(self._in_data_buffer)
            except Exception as inst:
                log.msg("Error while parsing serial data :", self._in_data_buffer, "error:", inst, system="driver", logLevel=logging.CRITICAL)

            while packets is not None:
                data_block = self._in_data_buffer[:packets.start()]
                data_block = self._format_data_in(data_block)
                log.msg("Data recieved <<: ", data_block, system="Driver", logLevel=logging.DEBUG)
                self.driver.set_timeout()
                self._dispatch_response(data_block)
                self._in_data_buffer = self._in_data_buffer[packets.end():]
                packets = None
                try:
                    packets = self._regex.search(self._in_data_buffer)
                except:
                    pass
        except Exception as inst:
            log.msg("Critical error in serial, error:", str(inst), system="Driver", logLevel=logging.CRITICAL)

    """
    ###########################################################################
    The following are methods for handshake/authentification
    """

    def _set_hardware_id(self):
        self.send_data("s%s" % str(self.driver.hardware_id))

    def _get_hardware_id(self):
        self.send_data("2")

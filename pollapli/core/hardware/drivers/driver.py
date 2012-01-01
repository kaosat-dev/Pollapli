"""base driver classes"""
import logging
from twisted.internet import reactor, defer
from twisted.python import log
from zope.interface import Interface, Attribute, implements
from pollapli.core.logic.tools.signal_system import SignalDispatcher
from pollapli.exceptions import DeviceNotConnected
from pollapli.core.base.base_component import BaseComponent
import time
from twisted.internet.error import TimeoutError


class Driver(BaseComponent):
    """
    Driver class: higher level handler of device connection that formats
    outgoing and incoming commands according to a spec before they get
    sent to the lower level connector.
     It actually mimics the way system device drivers work in a way.
     You can think of the events beeing sent out by the driver(dataRecieved...)
     as interupts of sorts
    """
    def __init__(self, hardware_id=None, auto_connect=False,
        max_connection_errors=2, connection_timeout=4, do_hanshake=False,
        do_authentification=False):
        """
        autoconnect:if autoconnect is True,device will be connected as soon as
        it is plugged in and detected
        max_connection_errors: the number of connection errors above which
        the driver gets disconnected
        connection_timeout: the number of seconds after which the driver
        gets disconnected (only in the initial , configuration phases by
        default)
        """
        BaseComponent.__init__(self, parent=None)
        self.auto_connect = auto_connect
        self.max_connection_errors = max_connection_errors
        self.connection_timeout = connection_timeout
        self.do_authentification = do_authentification
        self.do_handshake = do_hanshake
        self._hardware_interface = None
        self.hardware_id = hardware_id
        self.is_configured = False
        self.is_bound = False  # when port association has not been set
        self.is_handshake_ok = False
        self.is_authentification_ok = False
        self.is_connected = False
        self.is_bound = False
        self.is_busy = False

        self.errors = []
        self.connection_mode = 1
        self._connection_errors = 0
        self._connection_timeout = None
        self.deferred = defer.Deferred()

        self._signal_channel_prefix = ""
        self._signal_dispatcher = SignalDispatcher("driver_manager")

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __ne__(self, other):
        return not self.__eq__(other)

    def setup(self, *args, **kwargs):
        """do the driver setup phase"""
        self._signal_dispatcher.add_handler(handler=self.send_command, signal="addCommand")
        class_name = self.__class__.__name__.lower()
        log.msg("Driver of type", class_name, "setup sucessfully", system="Driver", logLevel=logging.INFO)

    def _send_signal(self, signal="", data=None):
        prefix = self._signal_channel_prefix + ".driver."
        self._signal_dispatcher.send_message(prefix + signal, self, data)

    @property
    def hardware_interface_class(self):
        """Get the current voltage."""
        return self._hardware_interface.__class__

    @property
    def connection_errors(self):
        """Get the current voltage."""
        return self._connection_errors

    @connection_errors.setter
    def connection_errors(self, value):
        self._connection_errors = value
        if self._connection_errors >= self.max_connection_errors:
            self.disconnect(clear_port=True)
            log.msg("cricital error while (re-)starting serial connection : please check your driver settings and device id, as well as cables,  and make sure no other process is using the port ", system="Driver", logLevel=logging.CRITICAL)
            self.deferred.errback(self.errors[-1])
            #self._hardware_interface._connect()  #weird way of handling disconnect
    """
    ###########################################################################
    The following are the timeout related methods
    """
    def set_connection_timeout(self):
        """sets internal timeout"""
        if self.connection_timeout > 0:
            log.msg("Setting timeout at ", time.time(), system="Driver", logLevel=logging.DEBUG)
            self._connection_timeout = reactor.callLater(self.connection_timeout, self._connection_timeout_check)

    def cancel_connection_timeout(self):
        """cancels internal timeout"""
        if self._connection_timeout is not None:
            try:
                self._connection_timeout.cancel()
                log.msg("Canceling timeout at ", time.time(), system="Driver", logLevel=logging.DEBUG)
            except:
                pass

    def _connection_timeout_check(self):
        """checks the timeout"""
        log.msg("Timeout check at ", time.time(), logLevel=logging.DEBUG)
        self.cancel_connection_timeout()
        self.errors.append(TimeoutError())
        self.connection_errors += 1
        if self.connection_errors < self.max_connection_errors:
            self.reconnect()

    """
    ###########################################################################
    The following are the connection related methods
    """
    def connect(self, port=None, connection_mode=None):
        """
        connection_mode :
        0:setup
        1:normal
        2:forced: to forcefully connect devices which have no deviceId stored
        """
        if self.is_connected:
            raise Exception("Driver already connected")
        if connection_mode is None:
            raise Exception("Invalid connection mode")

        self.deferred = defer.Deferred()
        self.connection_mode = connection_mode
        self.errors = []
        self._connection_errors = 0
        self.is_busy = True

        mode_str = "Normal"
        if self.connection_mode == 1:
            mode_str = "Setup"
        log.msg("Connecting driver in %s mode:" % mode_str, system="Driver", logLevel=logging.CRITICAL)
        reactor.callLater(0.1, self._hardware_interface.connect, port)
        return self.deferred

    def reconnect(self, *args, **kwargs):
        """Reconnect driver"""
        self._hardware_interface.reconnect(*args, **kwargs)

    def disconnect(self, *args, **kwargs):
        """Disconnect driver"""
        log.msg("Disconnecting driver", system="Driver", logLevel=logging.CRITICAL)
        self.is_connected = False
        self.is_busy = False
        self.cancel_connection_timeout()
        self._hardware_interface.disconnect(*args, **kwargs)

#self._send_signal("plugged_In", port)
#self._send_signal("plugged_Out", port)

    """
    ###########################################################################
    The following are the methods dealing with communication with the hardware
    """

    def send_command(self, command):
        """send a command to the physical device"""
        if not self.is_connected:
            raise DeviceNotConnected()
        self.command_deferred = defer.Deferred()
        reactor.callLater(0.01, self._hardware_interface.send_data, command)
        return self.command_deferred

    def _handle_response(self, data):
        """handle hardware response"""
        self.command_deferred.callback(data)

    """
    ###########################################################################
    The following are the higher level methods
    """
    def startup(self):
        """send startup command to hardware"""
        pass

    def shutdown(self):
        """send shutdown command to hardware"""
        pass

    def get_firmware_version(self):
        """retrieve firmware version from hardware"""
        pass

    def set_debug_level(self, level):
        """set hardware debug level, if any"""
        pass

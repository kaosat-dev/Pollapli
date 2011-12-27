"""base driver classes"""
import logging
from twisted.internet import reactor, defer
from twisted.python import log
from zope.interface import Interface, Attribute, implements
from pollapli.core.logic.tools.signal_system import SignalDispatcher
from pollapli.exceptions import DeviceNotConnected
from pollapli.core.base_component import BaseComponent
import time


class Driver(BaseComponent):
    """
    Driver class: higher level handler of device connection that formats
    outgoing and incoming commands according to a spec before they get
    sent to the lower level connector.
     It actually mimics the way system device drivers work in a way.
     You can think of the events beeing sent out by the driver(dataRecieved...)
     as interupts of sorts
    """
    def __init__(self, auto_connect=False, max_connection_errors=2,
        connection_timeout=4, do_hanshake=False, do_authentifaction=False,
        *args, **kwargs):
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
        self.do_authentifaction = do_authentifaction
        self.do_handshake = do_hanshake
        self._hardware_interface = None
        self.hardware_id = None
        self.is_configured = False
        self.is_bound = False  # when port association has not been set
        self.is_handshake_ok = False
        self.is_authentification_ok = False
        self.is_connected = False
        self.is_plugged_in = False

        self.connection_errors = 0
        self.connection_mode = 1
        self.deferred = defer.Deferred()
        self._timeout = None

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

    """
    ###########################################################################
    The following are the timeout related methods
    """
    def set_timeout(self):
        """sets internal timeout"""
        if self.connection_timeout>0:
            log.msg("Setting _timeout at ", time.time(), logLevel=logging.DEBUG)
            self._timeout = reactor.callLater(self.connection_timeout, self._timeout_check)

    def cancel_timeout(self):
        """cancels internal timeout"""
        if self._timeout is not None:
            try:
                self._timeout.cancel()
                log.msg("Canceling timeout at ", time.time(), logLevel=logging.DEBUG)
            except:
                pass

    def _timeout_check(self):
        """checks the timeout"""
        if self.is_connected:
            log.msg("Timeout check at ", time.time(), logLevel=logging.DEBUG)
            self.cancel_timeout()
            self.connection_errors += 1
            self.reconnect()
        else:
            self.cancel_timeout()

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
        log.msg("Connecting in mode:", self.connection_mode, system="Driver", logLevel=logging.CRITICAL)
        self._hardware_interface.connect(port=port)
        return self.deferred

    def reconnect(self, *args, **kwargs):
        """Reconnect driver"""
        self._hardware_interface.reconnect(*args, **kwargs)

    def disconnect(self, *args, **kwargs):
        """Disconnect driver"""
        self._hardware_interface.disconnect(*args, **kwargs)

    def _plugged_in(self, port):
        """
        first method that gets called upon successfull connection
        """
        self.is_plugged_in = True
        self._send_signal("plugged_In", port)
        if self.auto_connect:
            """slight delay, to prevent certain problems when trying to send
            data to the device too fast"""
            reactor.callLater(1, self.connect, 1)

    def _plugged_out(self, port):
        """
        first method that gets called upon sucessfull disconnection
        """
        self.is_handshake_ok = False
        self.is_authentification_ok = False
        self.is_connected = False
        self.is_plugged_in = False
        self._send_signal("plugged_Out", port)

    """
    ###########################################################################
    The following are the methods dealing with communication with the hardware
    """

    def send_command(self, data, sender=None, callback=None, *args, **kwargs):
        """send a command to the physical device"""
        if not self.is_connected:
            raise DeviceNotConnected()
#        if self.logic_handler:
#            self.logic_handler._handle_request(data=data,sender=sender,callback=callback)

    def _handle_response(self, data):
        """handle hardware response"""
        pass
#        if self.logic_handler:
#            self.logic_handler._handle_response(data)

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

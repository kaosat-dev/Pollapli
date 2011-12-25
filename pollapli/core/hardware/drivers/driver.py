"""base driver classes"""
import logging
from twisted.internet import reactor, defer
from twisted.python import log
from zope.interface import Interface, Attribute, implements
from pollapli.core.logic.tools.signal_system import SignalDispatcher
from pollapli.exceptions import DeviceNotConnected
from pollapli.core.base_component import BaseComponent


class Driver(BaseComponent):
    """
    Driver class: higher level handler of device connection that formats
    outgoing and incoming commands according to a spec before they get
    sent to the lower level connector.
     It actually mimics the way system device drivers work in a way.
     You can think of the events beeing sent out by the driver(dataRecieved...)
     as interupts of sorts

    Thoughts for future evolution:
    each driver will have a series of endpoints or slots/hooks,
    which represent the actual subdevices it handles:
    for example for reprap type devices, there is a :
    * "position" endpoint (abstract)
    * 3 endpoints for the cartesian bot motors
    * at least an endpoint for head temperature , one for the heater etc
    or this could be in a hiearchy , reflecting the one off the nodes:
    variable endpoint : position, and sub ones for motors

    just for future reference : this is not implemented but would be a
    declarative way to define the different "configuration steps"
    of this driver":
    *basically a dictionary with keys being the connection modes, and values
    a list of strings representing the methods to call
    *would require a "validator" :certain elements need to be mandatory
    ,such as the validation/setting of device ids
    configSteps={}
    configSteps[0]=["_handle_deviceHandshake","_handle_deviceIdInit"]
    configSteps[1]=["_handle_deviceHandshake","_handle_deviceIdInit",
    "some_other_method"]
    hardwareId will be needed to identify a specific device,
        as the system does not work purely base on ports
    """
    def __init__(self, auto_connect=False, max_connection_errors=2,
        connection_timeout=4, *args, **kwargs):
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
        self._hardware_interface = None
        self._hardware_id = None
        self.is_configured = False  # when port association has not been set
        self.is_handshake_ok = False
        self.is_identification_ok = False
        self.is_connected = False
        self.is_plugged_in = False

        self.connection_errors = 0
        self.connection_mode = 1
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
    """
    ###########################################################################
    The following are the connection related methods
    """

    def bind(self, port, set_id=True):
        """
        port : port to bind this driver to
        set_id: flag on whether to set/reset the hardware's id
        """
        self.deferred = defer.Deferred()
        log.msg("Attemtping to bind driver", self, "with deviceId:", self._hardware_id, "to port", port, system="Driver", logLevel=logging.DEBUG)
        self._hardware_interface.connect(set_id_mode=set_id, port=port)
        return self.deferred

    def connect(self, connection_mode=None, *args, **kwargs):
        """
        connection_mode :
        0:setup
        1:normal
        2:set_id
        3:forced: to forcefully connect devices which have no deviceId stored
        """
        if self.is_connected:
            raise Exception("Driver already connected")
        if connection_mode is None:
            raise Exception("Invalid connection mode")
        self.connection_mode = connection_mode
        log.msg("Connecting in mode:", self.connection_mode, system="Driver", logLevel=logging.CRITICAL)
        self._hardware_interface.connect()

    def reconnect(self, *args, **kwargs):
        """Reconnect driver"""
        self._hardware_interface.reconnect(*args, **kwargs)

    def disconnect(self, *args, **kwargs):
        """Disconnect driver"""
        self._hardware_interface.disconnect(*args, **kwargs)

    def plugged_in(self, port):
        """
        first method that gets called upon sucessfull connection
        """
        self.is_plugged_in = True
        self._send_signal("plugged_In", port)
        if self.auto_connect:
            """slight delay, to prevent certain problems when trying to send
            data to the device too fast"""
            reactor.callLater(1, self.connect, 1)

    def plugged_out(self, port):
        """
        first method that gets called upon sucessfull disconnection
        """
        self.is_configured = False
        self.is_handshake_ok = False
        self.is_identification_ok = False
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

    def _send_data(self, data, *args, **kwargs):
        """send data to the physical device, this should not be
        called directly, all commands need to go through the send_command
        method"""
        self._hardware_interface.send_data(data)

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

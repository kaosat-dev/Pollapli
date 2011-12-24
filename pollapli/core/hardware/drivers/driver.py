import logging,ast,time
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from zope.interface import Interface, Attribute,implements
from twisted.plugin import IPlugin,getPlugins
from twisted.internet.interfaces import IProtocol
from twisted.internet.protocol import Protocol
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
      ConnectionModes :
        0:setup
        1:normal
        2:set_id
        3:forced: to forcefully connect devices which have no deviceId stored

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
    def __init__(self, hardware_interface=None, protocol=None, options=None,
                 *args, **kwargs):
        """
        deviceType:
        hardware_interface:
        hardware_interface_klass:
        logic_handler_klass:
        protocol:
        options:
        """
        BaseComponent.__init__(self, parent=None)
        self.hardware_interface = hardware_interface
        self.options = options
        self.protocol = protocol

        self._hardware_id = None
        self.is_configured = False  # when port association has not been set
        self.is_hardware_handshake_ok = False
        self.is_hardware_id_ok = False
        self.is_connected = False
        self.is_plugged_in = False
        self.auto_connect = False
        # if autoconnect is True,device will be connected as soon as
        # it is plugged in and detected

        self.connection_errors = 0
        self.max_connection_errors = 2
        self.connection_timeout = 4
        self.connection_mode = 1
        self.deferred = defer.Deferred()

        self._signal_dispatcher = None
        self.signal_channel_prefix = ""
        self.signal_channel = ""
        self._signal_dispatcher = SignalDispatcher("driver_manager")

    @defer.inlineCallbacks
    def setup(self, *args, **kwargs):
        self._signal_dispatcher.add_handler(handler=self.send_command, signal="addCommand")
        class_name = self.__class__.__name__.lower()
        log.msg("Driver of type", class_name, "setup sucessfully", system="Driver", logLevel=logging.INFO)

    def _send_signal(self, signal="", data=None):
        prefix = self.signal_channel_prefix + ".driver."
        self._signal_dispatcher.send_message(prefix+signal, self, data)

    def bind(self, port, set_id=True):
        self.deferred = defer.Deferred()
        log.msg("Attemtping to bind driver", self, "with deviceId:", self._hardware_id, "to port", port, system="Driver", logLevel=logging.DEBUG)
        self.hardware_interface.connect(set_id_mode=set_id, port=port)
        return self.deferred

    def connect(self, connection_mode=None, *args, **kwargs):
        if self.is_connected:
            raise Exception("Driver already connected")
        if connection_mode is None:
            raise Exception("Invalid connection mode")
        self.connection_mode = connection_mode
        log.msg("Connecting in mode:", self.connection_mode, system="Driver", logLevel=logging.CRITICAL)
        self.hardware_interface.connect()

    def reconnect(self, *args, **kwargs):
        """Reconnect driver"""
        self.hardware_interface.reconnect(*args, **kwargs)

    def disconnect(self, *args, **kwargs):
        """Disconnect driver"""
        self.hardware_interface.disconnect(*args, **kwargs)

    def plugged_in(self, port):
        self.is_plugged_in = True
        self._send_signal("plugged_In", port)
        if self.auto_connect:
            """slight delay, to prevent certain problems when trying to send data to the device too fast"""
            reactor.callLater(1, self.connect, 1)

    def plugged_out(self, port):
        self.is_configured = False
        self.is_hardware_handshake_ok = False
        self.is_hardware_id_ok = False
        self.is_connected = False
        self.is_plugged_in = False
        self._send_signal("plugged_Out", port)

    def send_command(self, data, sender=None, callback=None, *args, **kwargs):
        if not self.is_connected:
            raise DeviceNotConnected()
#        if self.logic_handler:
#            self.logic_handler._handle_request(data=data,sender=sender,callback=callback)

    def _send_data(self, data, *args, **kwargs):
        self.hardware_interface.send_data(data)

    def _handle_response(self, data):
        pass
#        if self.logic_handler:
#            self.logic_handler._handle_response(data)

    """higher level methods""" 
    def startup(self):
        pass

    def shutdown(self):
        pass

    def init(self):
        pass

    def get_firmware_version(self):
        pass

    def set_debugLevel(self,level):
        pass

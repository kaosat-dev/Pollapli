from zope.interface import implements
from twisted.plugin import IPlugin
from zope.interface import classProvides
from twisted.python import log,failure
from pollapli.addons.ReprapAddOn.reprap.hardware.reprap_base_driver import ReprapBaseDriver
from pollapli import ipollapli
from pollapli.core.hardware.drivers.serial_hardware_interface import SerialHardwareInterface
from pollapli.core.hardware.drivers.protocols import BaseProtocol
import struct
from pollapli.core.logic.tools.wait import wait
from twisted.internet import defer
import logging


class ReprapMakerbotProtocol(BaseProtocol):
    target_firmware = ">=2.92"
    """
    Protocol for Makerbots
    Uses the following CRC
            uint8_t
            _crc_ibutton_update(uint8_t crc, uint8_t data)
            {
           uint8_t i;
           crc = crc ^ data;
           for (i = 0; i < 8; i++)
           {
               if (crc & 0x01)
                   crc = (crc >> 1) ^ 0x8C;
               else
                   crc >>= 1;
           }
           return crc;
            }
    """
    def __init__(self, driver=None, handshake=None, *args, **kwargs):
        BaseProtocol.__init__(self, driver, handshake)
        self._in_data_buffer = ""
        self._cur_packet_lng = 0

    @defer.inlineCallbacks
    def connectionMade(self):
        #BaseProtocol.connectionMade(self)
        yield wait(2.6)
        self.send_data("\x14\x1c\x00")
        self.driver.set_connection_timeout()

    def dataReceived(self, data):
        try:
            self._in_data_buffer += data
            if len(self._in_data_buffer) >= 2 and self._cur_packet_lng == 0:
                header = self._in_data_buffer[0]
                lng = ord(self._in_data_buffer[1])
                self._cur_packet_lng = lng + 3
                if header != "\xd5":
                    raise Exception("Wrong header recieved")
                    #TODO: add handling of wrong header
            if len(self._in_data_buffer) == self._cur_packet_lng and self._cur_packet_lng != 0:
                log.msg("Data recieved <<: ", self._in_data_buffer, system="Driver", logLevel=logging.DEBUG)
                data_block = self._format_data_in(self._in_data_buffer[2:])
                self._dispatch_response(data_block)
#                payload_length = self._current_packet_lng - 3
#                data = struct.unpack("%dB" % payload_length, self._in_data_buffer[2:self._cur_packet_lng - 1])
                self._cur_packet_lng = 0
                self._in_data_buffer = ""
        except Exception as inst:
            self.driver.connection_errors += 1
            log.msg("Critical error in serial, error:", str(inst), system="Driver", logLevel=logging.CRITICAL)


    def _format_data_out(self, data):
        """
        Makerbot protocol infos: (from http://replicat.org/sanguino3g)
        A package is used to wrap every command. It ensures that the command
        received is complete and not corrupted. The package contains
        the following bytes:
        0: start byte, always 0xD5
        1: length of the packet, not including the start byte, length byte or
        the CRC.
        2: the command byte - this is the first byte of the payload
        *: content of the block, all multibyte values are LSB first
        (Intel notation)
        n-1: the package ends with a single byte CRC checksum of the payload
        (Maxim 1-Wire CRC)
        """

        payload = data
        data = "\xd5"+chr(len(payload)) + payload + self._crc(payload)
        # < is used since we need little endian
        #data = struct.pack("<BB%isB" % size, 213, size, payload, crc)
        return data

    def _format_data_in(self, data, *args, **kwargs):
        """
        Reply packages are built just like the command packages. The first byte
        of the payload is the return code for the previous command
        (see Response Code below)
        All further bytes depend on the command sent.
        """
        payload_lng = len(data) - 2
        crc = data[-1:]
        rcode = ord(data[0])
        data = data[1:-1]
        rdata = struct.unpack("%dB" % payload_lng, data)
        print("crc", crc, "rcode", rcode, "rdata", rdata)

        #TODO: move this to command handling ?
        if rcode == 128:
            print("generic error packet discarded")
        elif rcode == 129 or rcode == 134 or rcode == 1:
            print("command ok")
        elif rcode >= 130 and rcode <= 135 and rcode != 134:
            print("generic error packet discarded")

        return data

    def _crc(self, payload):
        crc = 0
        for c in payload:
            crc = (crc ^ ord(c)) & 0xff
            for i in range(8):
                if crc & 0x01:
                    crc = ((crc >> 1) ^ 0x8c)
                else:
                    crc >>= 1
        return chr(crc)


class ReprapMakerbotDriver(ReprapBaseDriver):
    """Driver class for the makerbot reprap firmware"""
    classProvides(IPlugin, ipollapli.IDriver)
    target_hardware = "Makerbot"

    def __init__(self,hardware_id=None, auto_connect=False, max_connection_errors=3,
        connection_timeout=0, do_hanshake=False, do_authentifaction=False,
        speed=115200, *args, **kwargs):
        ReprapBaseDriver.__init__(self, hardware_id, auto_connect, max_connection_errors, connection_timeout, do_hanshake, do_authentifaction,*args, **kwargs)
        self._hardware_interface = SerialHardwareInterface(self, ReprapMakerbotProtocol, False, speed, *args, **kwargs)

    def startup(self):
        cmd = struct.pack("<B", 1)
        return self.send_command(cmd)

    def shutdown(self):
        cmd = struct.pack("<B", 7)
        return self.send_command(cmd)

    def echo_test(self):
        return self.send_command(0x70)

    def get_firmware_info(self):
        #cmd = "\x14\x1c\x00"
        cmd = "\x01"
        return self.send_command(cmd)

    def set_debug_level(self,level):
        return self.send_command((0x76,None))

    def enqueue_position(self, position, rapid=False):
        extended = True
        if extended:
            return self.send_command((0x1,None))
        else:
            return self.send_command((0x81,None))

    def get_position(self):
        return self.send_command((21,None))

    def start(self):
        pass

    def stop(self,extended=False,motors=False,queue=False):
        if extended:
            payload=None
            if motors:
                payload=1
            self.send_command((0x22,None))

from zope.interface import implements
from twisted.plugin import IPlugin
from zope.interface import classProvides
from twisted.python import log,failure
from pollapli.addons.ReprapAddOn.reprap.hardware.reprap_base_driver import ReprapBaseDriver
from pollapli import ipollapli
from pollapli.core.hardware.drivers.serial_hardware_interface import SerialHardwareInterface
from pollapli.core.hardware.drivers.protocols import BaseProtocol
import struct


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
        def crc(payload):
            crc = 0
            for c in payload:
                crc = (crc ^ ord(c)) & 0xff
                for i  in range(8):
                    if crc & 0x01:
                        crc = ((crc >>1) ^ 0x8c)
                    else:
                        crc >>= 1
            return chr(crc)

        payload = data

        data = "\xd5"+chr(len(payload))+payload+crc(payload)
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
        print("in format data in")
        start, lng, rcode, rdata, crc = struct.unpack("<BBBIB",data)

        if rcode == 128:
            print("generic error packet discarded")
        elif rcode == 129 or rcode == 134:
            print("success")
        elif rcode >= 130 and rcode <= 135 and rcode != 134:
            print("success")

        return data


class ReprapMakerbotDriver(ReprapBaseDriver):
    """Driver class for the makerbot reprap firmware"""
    classProvides(IPlugin, ipollapli.IDriver)
    target_hardware = "Makerbot"

    def __init__(self,hardware_id=None, auto_connect=False, max_connection_errors=3,
        connection_timeout=0, do_hanshake=False, do_authentifaction=False,
        speed=38400, *args, **kwargs):
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
        cmd = "\x14\x1c\x00"
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

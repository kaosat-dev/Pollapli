import sys
if sys.platform == "win32":
    from twisted.internet import win32eventreactor
    win32eventreactor.install()
from twisted.trial import unittest
from twisted.internet import defer, reactor
import struct
from pollapli.addons.ReprapAddOn.reprap.hardware.reprap_makerbot_driver import ReprapMakerbotProtocol,\
    ReprapMakerbotDriver


class TestReprapMakerbotProtocol(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_format_data_out_get_firmware_info(self):
        reprap_makerbot_protocol = ReprapMakerbotProtocol(driver=ReprapMakerbotDriver(), do_checksum=True)
        cmd = struct.pack("<B", 0)
        cmd_size = struct.calcsize("<B")
        payload = (cmd, cmd_size)

        obs_data = reprap_makerbot_protocol._format_data_out(payload)
        exp_data = "\xd5\x01\x01\xd2"
        self.assertEquals(obs_data, exp_data)
    
    def test_format_data_out_init(self):
        reprap_makerbot_protocol = ReprapMakerbotProtocol(driver=ReprapMakerbotDriver(), do_checksum=True)
        cmd = struct.pack("<B", 1)
        cmd_size = struct.calcsize("<B")
        payload = (cmd, cmd_size)

        obs_data = reprap_makerbot_protocol._format_data_out(payload)
        truc = struct.unpack("<BB%isB" % cmd_size, obs_data)
        exp_data = "\xd5\x01\x01\xd2"
        self.assertEquals(obs_data, exp_data)

    def test_format_data_out_shutdown(self):
        reprap_makerbot_protocol = ReprapMakerbotProtocol(driver=ReprapMakerbotDriver(), do_checksum=True)
        cmd = struct.pack("<B", 7)
        cmd_size = struct.calcsize("<B")
        payload = (cmd, cmd_size)

        obs_data = reprap_makerbot_protocol._format_data_out(payload)
        truc = struct.unpack("<BB%isB" % cmd_size, obs_data)
        exp_data = "\xd5\x01\x07\xf7"
        self.assertEquals(obs_data, exp_data)

    def test_format_data_in_get_position(self):
        reprap_makerbot_protocol = ReprapMakerbotProtocol(driver=ReprapMakerbotDriver(), do_checksum=True)

        cmd_format = "<BBBIB"
        cmd = struct.pack(cmd_format, 213, 10, 129, 3568, 13)

        obs_data = reprap_makerbot_protocol._format_data_in(cmd)
#        exp_data = ""
#        self.assertEquals(obs_data, exp_data)
